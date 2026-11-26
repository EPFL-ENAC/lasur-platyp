"""A user with permissions on a company must not be able to change the entities of another one."""
from datetime import datetime

import pytest
from enacit4r_auth.models.auth import User
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from api import auth
from api.models.domain import Campaign, CompanyAction, Participant, Record, Workplace
from api.models.query import CampaignDraft, CompanyActionDraft, ParticipantDraft, RecordDraft
from api.services.actions import CompanyActionService
from api.services.campaigns import CampaignService
from api.services.participants import ParticipantService
from api.services.records import RecordService

# company 1 (campaigns 1 and 3) is the user's own, company 2 (campaign 2) is someone else's
USER = User(id="abc", username="test", email="test@me.com", first_name="Foo", last_name="Bar",
            realm_roles=[], client_roles=[])
ADMIN = USER.model_copy(update={"realm_roles": [auth.ADMIN_ROLE]})


@compiles(JSONB, "sqlite")
def jsonb_as_json(element, compiler, **kw):
    return "JSON"


class AsyncSessionStub:
    """Async facade of a sync session (no async SQLite driver in the dependencies)"""

    def __init__(self, session: Session):
        self.session = session
        self.add = session.add

    async def exec(self, statement):
        return self.session.exec(statement)

    async def delete(self, entity):
        self.session.delete(entity)

    async def commit(self):
        self.session.commit()


@pytest.fixture
def db(monkeypatch):
    async def check(user, resource, permission):
        return resource == "company:1" and permission == "update"
    monkeypatch.setattr(auth, "check_admin_or_perm", check)

    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    # no company table: foreign keys are not enforced by SQLite
    for model in [Campaign, CompanyAction, Participant, Record, Workplace]:
        model.__table__.create(engine)
    with Session(engine, expire_on_commit=False) as session:
        ts = {"created_at": datetime.now(), "updated_at": datetime.now()}
        for id, company_id in [(1, 1), (2, 2), (3, 1)]:
            session.add(Campaign(id=id, name=f"c{id}", company_id=company_id, **ts))
        for id, identifier in [(1, "p1"), (2, "p2"), (3, "p1")]:
            session.add(Participant(id=id, token=f"t{id}", identifier=identifier, campaign_id=id, **ts))
        session.add(CompanyAction(id=1, group="global", company_id=1))
        session.add(Record(id=1, token="t2", data={"a": 1}, campaign_id=2, company_id=2, **ts))
        session.commit()
        yield session


def update_participant(db, id, campaign_id, identifier, user=USER):
    return ParticipantService(AsyncSessionStub(db)).update(
        id, ParticipantDraft(identifier=identifier, campaign_id=campaign_id), user)


@pytest.mark.asyncio
async def test_participant_of_other_company(db):
    for campaign_id in (1, 2):
        with pytest.raises(HTTPException) as e:
            await update_participant(db, 2, campaign_id, "stolen")
        assert e.value.status_code == 403
    db.expire_all()
    assert db.get(Participant, 2).identifier == "p2"
    assert db.get(Participant, 2).campaign_id == 2


@pytest.mark.asyncio
async def test_participant_moved_to_other_company(db):
    with pytest.raises(HTTPException) as e:
        await update_participant(db, 1, 2, "p1")
    assert e.value.status_code == 403
    db.expire_all()
    assert db.get(Participant, 1).campaign_id == 1


@pytest.mark.asyncio
async def test_participant_allowed(db):
    assert (await update_participant(db, 1, 1, "renamed")).identifier == "renamed"
    assert (await update_participant(db, 1, 3, "renamed")).campaign_id == 3
    # admin, and no user (end of survey, see collect.saveComments)
    assert (await update_participant(db, 2, 2, "by admin", ADMIN)).identifier == "by admin"
    participant = db.get(Participant, 2)
    participant.status = "completed"
    await ParticipantService(AsyncSessionStub(db)).update(2, participant)
    db.expire_all()
    assert db.get(Participant, 2).status == "completed"


@pytest.mark.asyncio
async def test_participant_identifier_unique_in_target_campaign(db):
    with pytest.raises(HTTPException) as e:
        await update_participant(db, 1, 3, "p1")
    assert e.value.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("user", [USER, ADMIN])
async def test_company_id_is_immutable(db, user):
    session = AsyncSessionStub(db)
    for update in (CampaignService(session).update(1, CampaignDraft(name="moved", company_id=2), user),
                   CompanyActionService(session).update(1, CompanyActionDraft(group="moved", company_id=2), user)):
        with pytest.raises(HTTPException) as e:
            await update
        assert e.value.status_code == 400
    # same company is fine
    await CampaignService(session).update(1, CampaignDraft(name="renamed", company_id=1), user)
    await CompanyActionService(session).update(1, CompanyActionDraft(group="train", company_id=1), user)
    db.expire_all()
    assert (db.get(Campaign, 1).name, db.get(Campaign, 1).company_id) == ("renamed", 1)
    assert (db.get(CompanyAction, 1).group, db.get(CompanyAction, 1).company_id) == ("train", 1)


@pytest.mark.asyncio
async def test_read_permission_is_not_enough(db, monkeypatch):
    async def check(user, resource, permission):
        return resource == "company:1" and permission == "read"
    monkeypatch.setattr(auth, "check_admin_or_perm", check)
    with pytest.raises(HTTPException) as e:
        await update_participant(db, 1, 1, "renamed")
    assert e.value.status_code == 403


@pytest.mark.asyncio
async def test_record_moved_to_other_campaign(db):
    with pytest.raises(HTTPException) as e:
        await RecordService(AsyncSessionStub(db)).createOrUpdate(
            RecordDraft(token="t2", data={"stolen": True}), db.get(Campaign, 1))
    assert e.value.status_code == 400
    db.expire_all()
    record = db.get(Record, 1)
    assert (record.data, record.campaign_id, record.company_id) == ({"a": 1}, 2, 2)


@pytest.mark.asyncio
async def test_participant_with_record_cannot_move(db):
    db.add(Record(id=2, token="t1", campaign_id=1, company_id=1))
    db.commit()
    with pytest.raises(HTTPException) as e:
        await update_participant(db, 1, 3, "renamed")
    assert e.value.status_code == 400
    db.expire_all()
    assert db.get(Participant, 1).campaign_id == 1
    # same campaign is fine
    assert (await update_participant(db, 1, 1, "renamed")).identifier == "renamed"

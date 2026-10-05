from logging import debug
import secrets
from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import Participant
from api.models.query import ParticipantResult, ParticipantDraft
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime
from api.auth import User, is_admin, require_admin_or_perm

from api.services.campaigns import CampaignService
from api.services.entities import EntityService


class ParticipantQueryBuilder(QueryBuilder):

    def build_count_query_with_joins(self, filter):
        query = self.build_count_query()
        query = self._apply_joins(query, filter)
        return query

    def build_query_with_joins(self, total_count, filter, fields=None):
        start, end, query = self.build_query(total_count, fields)
        query = self._apply_joins(query, filter)
        return start, end, query

    def _apply_joins(self, query, filter):
        query = query.distinct()
        return query


class ParticipantService(EntityService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count(self) -> int:
        """Count all participants"""
        count = (await self.session.exec(text("select count(id) from participant"))).scalar()
        return count

    async def get(self, id: int, user: User = None) -> Participant:
        """Get a participant by id"""
        res = await self.session.exec(
            select(Participant).where(
                Participant.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")
        if user is not None and not is_admin(user):
            await CampaignService(self.session).get(entity.campaign_id, user)
        return entity

    async def get_by_token(self, token: str) -> Participant:
        """Get a participant by token"""
        res = await self.session.exec(
            select(Participant).where(
                Participant.token == token))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")
        return entity

    async def delete(self, id: int, user: User = None) -> Participant:
        """Delete a participant by id"""
        res = await self.session.exec(
            select(Participant).where(Participant.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")

        campaign = await CampaignService(self.session).get(entity.campaign_id, user)
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{campaign.company_id}", "update")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list, user: User = None) -> ParticipantResult:
        """Get all participants matching filter and range"""
        # TODO filter by permitted company ids through campaigns
        if user is not None and not is_admin(user):
            permitted_campaign_ids = await CampaignService(self.session).list_permitted_ids(user, "read")
            if filter is None:
                filter = {}
            if permitted_campaign_ids:
                if "campaign_id" in filter:
                    filter["campaign_id"] = self.merge_ids_filter(
                        filter["campaign_id"], permitted_campaign_ids)
                else:
                    filter["campaign_id"] = permitted_campaign_ids
            else:
                # No permitted campaigns, return empty result
                # Assuming no campaign has campaign_id -1
                filter["campaign_id"] = [-1]

        builder = ParticipantQueryBuilder(
            Participant, filter, sort, range, {})

        # Do a query to satisfy total count
        count_query = builder.build_count_query_with_joins(filter)
        total_count_query = await self.session.exec(count_query)
        total_count = total_count_query.one()

        # Main query
        start, end, query = builder.build_query_with_joins(
            total_count, filter, fields)

        # Execute query
        results = await self.session.exec(query)
        entities = results.all()

        return ParticipantResult(
            total=total_count,
            skip=start,
            limit=end - start + 1,
            data=entities
        )

    async def create(self, payload: ParticipantDraft, user: User = None) -> Participant:
        """Create a new participant"""
        # Get campaign to verify access
        campaign = await CampaignService(self.session).get(payload.campaign_id, user)
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{campaign.company_id}", "update")

        res = await self.session.exec(
            select(Participant).where(
                Participant.identifier == payload.identifier, Participant.campaign_id == payload.campaign_id)
        )
        entity = res.one_or_none()
        if entity:
            raise HTTPException(
                status_code=400, detail="Participant identifier already exists")
        entity = Participant(**payload.model_dump())
        entity.created_at = datetime.now()
        entity.updated_at = datetime.now()
        if user:
            entity.created_by = user.username
            entity.updated_by = user.username
        # generate unique token
        found = True
        while found:
            entity.token = secrets.token_urlsafe(16)
            res = await self.session.exec(
                select(Participant).where(
                    Participant.token == entity.token)
            )
            found = res.one_or_none() is not None

        self.session.add(entity)
        await self.session.commit()
        return entity

    async def update(self, id: int, payload: ParticipantDraft, user: User = None) -> Participant:
        """Update a participant"""
        # Get campaign to verify access
        campaign = await CampaignService(self.session).get(payload.campaign_id, user)
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{campaign.company_id}", "update")

        res = await self.session.exec(
            select(Participant).where(Participant.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")
        if entity.identifier != payload.identifier:
            # changing the identifier is allowed but make sure it is unique in the campaign
            res = await self.session.exec(
                select(Participant).where(
                    Participant.identifier == payload.identifier, Participant.campaign_id == entity.campaign_id)
            )
            if res.one_or_none() is not None:
                raise HTTPException(
                    status_code=400, detail="Participant identifier already exists")
        for key, value in payload.model_dump().items():
            print(key, value)
            if key not in ["id", "created_at", "updated_at", "created_by", "updated_by", "token"]:
                setattr(entity, key, value)
        entity.updated_at = datetime.now()
        if user:
            entity.updated_by = user.username
        await self.session.commit()
        return entity

from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import Participant
from api.models.query import ParticipantResult
from api.services.participants import ParticipantService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import Participant

router = APIRouter()


@router.get("/", response_model=ParticipantResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
) -> ParticipantResult:
    """Search for participants"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await ParticipantService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=Participant, response_model_exclude_none=True)
async def get(id: int, session: AsyncSession = Depends(get_session)) -> Participant:
    """Get a participant by id"""
    return await ParticipantService(session).get(id)


@router.delete("/{id}", response_model=Participant, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Participant:
    """Delete a participant by id"""
    return await ParticipantService(session).delete(id)


@router.post("/", response_model=Participant, response_model_exclude_none=True)
async def create(
    natural_resource: Participant,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Participant:
    """Create a participant"""
    return await ParticipantService(session).create(natural_resource, user)


@router.put("/{id}", response_model=Participant, response_model_exclude_none=True)
async def update(
    id: int,
    natural_resource: Participant,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Participant:
    """Update a participant by id"""
    return await ParticipantService(session).update(id, natural_resource, user)

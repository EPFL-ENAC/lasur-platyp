from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import Participant
from api.models.query import ParticipantResult, ParticipantData, ParticipantDraft
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
    user: User = Depends(kc_service.get_user_info()),
) -> ParticipantResult:
    """Search for participants"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await ParticipantService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"], user)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=Participant, response_model_exclude_none=True)
async def get(id: int, session: AsyncSession = Depends(get_session),
              user: User = Depends(kc_service.get_user_info())
              ) -> Participant:
    """Get a participant by id"""
    return await ParticipantService(session).get(id, user)


@router.delete("/{id}", response_model=Participant, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Participant:
    """Delete a participant by id"""
    return await ParticipantService(session).delete(id, user)


@router.post("/", response_model=Participant, response_model_exclude_none=True)
async def create(
    item: ParticipantDraft,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Participant:
    """Create a participant"""
    return await ParticipantService(session).create(item, user)


@router.put("/{id}", response_model=Participant, response_model_exclude_none=True)
async def update(
    id: int,
    item: ParticipantDraft,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Participant:
    """Update a participant by id"""
    return await ParticipantService(session).update(id, item, user)


@router.post("/_upload", response_model=List[ParticipantData], response_model_exclude_none=True)
async def read_participants_from_excel(
        files: UploadFile = File(
            description="Excel file containing participant descriptions"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
):
    return await ParticipantService(session).parse(files.file._file)

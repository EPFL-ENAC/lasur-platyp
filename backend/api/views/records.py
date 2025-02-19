from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import Record
from api.models.query import RecordResult
from api.services.records import RecordService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import Record

router = APIRouter()


@router.get("/", response_model=RecordResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
) -> RecordResult:
    """Search for records"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await RecordService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=Record, response_model_exclude_none=True)
async def get(id: int, session: AsyncSession = Depends(get_session)) -> Record:
    """Get a record by id"""
    return await RecordService(session).get(id)


@router.delete("/{id}", response_model=Record, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Record:
    """Delete a record by id"""
    return await RecordService(session).delete(id)

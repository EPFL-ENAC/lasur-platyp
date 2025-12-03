from fastapi import APIRouter, Depends, Query, HTTPException, Response
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import Record
from api.models.query import RecordResult
from api.services.records import RecordService
from enacit4r_sql.utils.query import validate_params, ValidationError

router = APIRouter()


@router.get("/", response_model=RecordResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    user: User = Depends(kc_service.require_admin()),
    session: AsyncSession = Depends(get_session),
) -> RecordResult:
    """Search for records"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await RecordService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=Record, response_model_exclude_none=True)
async def get(id: int,
              user: User = Depends(kc_service.require_admin()),
              session: AsyncSession = Depends(get_session)) -> Record:
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


@router.get("/flat", response_model_exclude_none=True)
async def compute_flat(
    filter: str = Query(None),
    completed: bool = Query(
        False, description="Whether to include only completed records"),
    user: User = Depends(kc_service.require_admin()),
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Query records in flat format as a CSV"""
    try:
        validated = validate_params(filter, None, None, None)
        service = RecordService(session)
        df = await service.get_dataframe(validated["filter"], flat=True)
        if completed:
            df = service.filter_completed(df)
        return Response(content=df.to_csv(date_format="%Y-%m-%dT%H:%M:%S.%f", index=False), media_type="text/csv")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")

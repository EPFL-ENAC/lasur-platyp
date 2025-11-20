from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.query import Stats
from api.services.records import RecordService
from api.services.stats import StatsService
from enacit4r_sql.utils.query import validate_params, ValidationError

router = APIRouter()


@router.get("/all", response_model_exclude_none=True)
async def compute_all_statistics(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Stats:
    """Query all type of all statistics in records"""
    try:
        validated = validate_params(filter, None, None, None)
        df = await RecordService(session).get_dataframe(validated["filter"], flat=True)
        return StatsService().compute_stats(df)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")

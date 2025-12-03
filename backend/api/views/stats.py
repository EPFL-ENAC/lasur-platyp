from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.query import Stats, LocationFilter
from api.services.records import RecordService
from api.services.stats.stats import StatsService
from enacit4r_sql.utils.query import validate_params, ValidationError, paramAsDict

router = APIRouter()


@router.get("/all", response_model_exclude_none=True)
async def compute_all_statistics(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Stats:
    """Query all type of all statistics in records"""
    try:
        filterDict = paramAsDict(filter)
        workPlaceFilter = filterDict.get('workplace_location', None)
        if 'workplace_location' in filterDict:
            del filterDict['workplace_location']
        validated = validate_params(filterDict, None, None, None)
        service = RecordService(session)
        df = await service.get_dataframe(validated["filter"], flat=True)
        if workPlaceFilter:
            workPlaceFilter = LocationFilter.model_validate(
                workPlaceFilter, by_alias=True)
            df = service.filter_by_workplace_location(df, workPlaceFilter)
        return StatsService().compute_stats(df)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")

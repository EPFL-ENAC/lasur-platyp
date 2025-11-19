import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.query import Stats, Frequencies, Emissions, Links
from api.services.records import RecordService
from enacit4r_sql.utils.query import validate_params, ValidationError

router = APIRouter()


@router.get("/freq_mod_pro", response_model=list[Frequencies], response_model_exclude_none=True)
async def compute_freq_mod_pro_frequencies(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> list[Frequencies]:
    """Query frequency of professional modalities in records"""
    try:
        validated = validate_params(filter, None, None, None)
        return [await RecordService(session).get_mod_stats(mod, validated["filter"]) for mod in [
            'freq_mod_pro_local_walking',
            'freq_mod_pro_local_car',
            'freq_mod_pro_local_pub',
            'freq_mod_pro_local_bike',
            'freq_mod_pro_local_moto',
            'freq_mod_pro_local_train',
            'freq_mod_pro_region_car',
            'freq_mod_pro_region_pub',
            'freq_mod_pro_region_train',
            'freq_mod_pro_region_moto',
            'freq_mod_pro_region_plane',
            'freq_mod_pro_europe_car',
            'freq_mod_pro_europe_train',
            'freq_mod_pro_europe_plane',
            'freq_mod_pro_inter_car',
            'freq_mod_pro_inter_train',
            'freq_mod_pro_inter_plane']]
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/mod_reco", response_model=Links, response_model_exclude_none=True)
async def compute_freq_mod_recommendations_links(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Links:
    """Query modality to recommendation links in records"""
    try:
        validated = validate_params(filter, None, None, None)
        return await RecordService(session).get_mod_reco_links(validated["filter"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/all", response_model_exclude_none=True)
async def compute_all_statistics(
    filter: str = Query(None),
    # user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Stats:
    """Query all type of all statistics in records"""
    try:
        validated = validate_params(filter, None, None, None)
        return await RecordService(session).compute_stats(validated["filter"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/flat", response_model_exclude_none=True)
async def compute_flat(
    filter: str = Query(None),
    completed: bool = Query(
        False, description="Whether to include only completed records"),
    # user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Query records in flat format as a CSV"""
    try:
        validated = validate_params(filter, None, None, None)
        service = RecordService(session)
        df = await service.get_dataframe(validated["filter"], flat=True)
        if completed:
            df = service.filter_completed_records(df)
        return Response(content=df.to_csv(date_format="%Y-%m-%dT%H:%M:%S.%f", index=False), media_type="text/csv")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")

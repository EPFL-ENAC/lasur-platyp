from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.query import Frequencies
from api.services.records import RecordService
from enacit4r_sql.utils.query import validate_params, ValidationError

router = APIRouter()


@router.get("/equipments", response_model=Frequencies, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Frequencies:
    """Query frequency of equipments in records"""
    try:
        validated = validate_params(filter, None, None, None)
        return await RecordService(session).get_equipments_frequencies(validated["filter"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/constraints", response_model=Frequencies, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Frequencies:
    """Query frequency of constraints in records"""
    try:
        validated = validate_params(filter, None, None, None)
        return await RecordService(session).get_constraints_frequencies(validated["filter"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/travel_time", response_model=Frequencies, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Frequencies:
    """Query frequency of travel_time in records"""
    try:
        validated = validate_params(filter, None, None, None)
        return await RecordService(session).get_travel_time_frequencies(validated["filter"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/freq_mod", response_model=list[Frequencies], response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    # user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> list[Frequencies]:
    """Query frequency of modalities in records"""
    try:
        validated = validate_params(filter, None, None, None)
        return [await RecordService(session).get_mod_stats(mod, validated["filter"]) for mod in [
            'freq_mod_car',
            'freq_mod_pub',
            'freq_mod_bike', 'freq_mod_moto', 'freq_mod_train', 'freq_mod_walking']]
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/freq_mod_pro", response_model=list[Frequencies], response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    # user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> list[Frequencies]:
    """Query frequency of modalities in records"""
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
            'freq_mod_pro_inter_car',
            'freq_mod_pro_inter_train',
            'freq_mod_pro_inter_plane']]
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")

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
        return await RecordService(session).find_equipments_frequencies(validated["filter"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")

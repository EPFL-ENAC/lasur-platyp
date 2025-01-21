from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import Campaign
from api.models.query import CampaignResult
from api.services.campaigns import CampaignService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import Campaign

router = APIRouter()


@router.get("/", response_model=CampaignResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
) -> CampaignResult:
    """Search for campaigns"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await CampaignService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=Campaign, response_model_exclude_none=True)
async def get(id: int, session: AsyncSession = Depends(get_session)) -> Campaign:
    """Get a campaign by id"""
    return await CampaignService(session).get(id)


@router.delete("/{id}", response_model=Campaign, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Campaign:
    """Delete a campaign by id"""
    return await CampaignService(session).delete(id)


@router.post("/", response_model=Campaign, response_model_exclude_none=True)
async def create(
    item: Campaign,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Campaign:
    """Create a campaign"""
    return await CampaignService(session).create(item, user)


@router.put("/{id}", response_model=Campaign, response_model_exclude_none=True)
async def update(
    id: int,
    item: Campaign,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Campaign:
    """Update a campaign by id"""
    return await CampaignService(session).update(id, item, user)

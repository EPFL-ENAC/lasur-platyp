from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import CompanyAction
from api.models.query import CompanyActionResult, CompanyActionDraft
from api.services.actions import CompanyActionService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import CompanyAction

router = APIRouter()


@router.get("/", response_model=CompanyActionResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin()),
) -> CompanyActionResult:
    """Search for company actions"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await CompanyActionService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=CompanyAction, response_model_exclude_none=True)
async def get(id: int,
              session: AsyncSession = Depends(get_session),
              user: User = Depends(kc_service.require_admin())) -> CompanyAction:
    """Get a company action by id"""
    return await CompanyActionService(session).get(id)


@router.delete("/{id}", response_model=CompanyAction, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> CompanyAction:
    """Delete a company action by id"""
    return await CompanyActionService(session).delete(id)


@router.post("/", response_model=CompanyAction, response_model_exclude_none=True)
async def create(
    item: CompanyActionDraft,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> CompanyAction:
    """Create a company action"""
    return await CompanyActionService(session).create(item, user)


@router.put("/{id}", response_model=CompanyAction, response_model_exclude_none=True)
async def update(
    id: int,
    item: CompanyActionDraft,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> CompanyAction:
    """Update a company action by id"""
    return await CompanyActionService(session).update(id, item, user)

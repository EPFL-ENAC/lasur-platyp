from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User, require_admin_or_perm
from api.models.domain import Company
from api.models.query import CompanyResult
from api.services.companies import CompanyService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import Company

router = APIRouter()


@router.get("/", response_model=CompanyResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> CompanyResult:
    """Search for companies"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await CompanyService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=Company, response_model_exclude_none=True)
async def get(id: int,
              session: AsyncSession = Depends(get_session),
              user: User = Depends(kc_service.get_user_info())
              ) -> Company:
    """Get a company by id"""
    await require_admin_or_perm(user, f"company:{id}", "read")
    return await CompanyService(session).get(id)


@router.delete("/{id}", response_model=Company, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Company:
    """Delete a company by id"""
    return await CompanyService(session).delete(id)


@router.post("/", response_model=Company, response_model_exclude_none=True)
async def create(
    item: Company,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Company:
    """Create a company"""
    return await CompanyService(session).create(item, user)


@router.put("/{id}", response_model=Company, response_model_exclude_none=True)
async def update(
    id: int,
    item: Company,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Company:
    """Update a company by id"""
    return await CompanyService(session).update(id, item, user)

from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import Form
from api.models.query import FormResult
from api.services.forms import FormService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import Form

router = APIRouter()


@router.get("/", response_model=FormResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
) -> FormResult:
    """Search for natural resources"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await FormService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=Form, response_model_exclude_none=True)
async def get(id: int, session: AsyncSession = Depends(get_session)) -> Form:
    """Get a natural resource by id"""
    return await FormService(session).get(id)


@router.delete("/{id}", response_model=Form, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Form:
    """Delete a natural resource by id"""
    return await FormService(session).delete(id)


@router.post("/", response_model=Form, response_model_exclude_none=True)
async def create(
    natural_resource: Form,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Form:
    """Create a natural resource"""
    return await FormService(session).create(natural_resource, user)


@router.put("/{id}", response_model=Form, response_model_exclude_none=True)
async def update(
    id: int,
    natural_resource: Form,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> Form:
    """Update a natural resource by id"""
    return await FormService(session).update(id, natural_resource, user)

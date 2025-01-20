from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import FormRevision
from api.models.query import FormRevisionResult
from api.services.form_revisions import FormRevisionService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import FormRevision

router = APIRouter()


@router.get("/", response_model=FormRevisionResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
) -> FormRevisionResult:
    """Search for form revisions"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await FormRevisionService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=FormRevision, response_model_exclude_none=True)
async def get(id: int, session: AsyncSession = Depends(get_session)) -> FormRevision:
    """Get a form revision by id"""
    return await FormRevisionService(session).get(id)


@router.delete("/{id}", response_model=FormRevision, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> FormRevision:
    """Delete a form revision by id"""
    return await FormRevisionService(session).delete(id)


@router.post("/", response_model=FormRevision, response_model_exclude_none=True)
async def create(
    natural_resource: FormRevision,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> FormRevision:
    """Create a form revision"""
    return await FormRevisionService(session).create(natural_resource, user)


@router.put("/{id}", response_model=FormRevision, response_model_exclude_none=True)
async def update(
    id: int,
    natural_resource: FormRevision,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> FormRevision:
    """Update a form revision by id"""
    return await FormRevisionService(session).update(id, natural_resource, user)

from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import CaseReport
from api.models.query import CaseReportResult
from api.services.case_reports import CaseReportService
from enacit4r_sql.utils.query import validate_params, ValidationError
from api.models.domain import CaseReport

router = APIRouter()


@router.get("/", response_model=CaseReportResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
) -> CaseReportResult:
    """Search for case reports"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await CaseReportService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=CaseReport, response_model_exclude_none=True)
async def get(id: int, session: AsyncSession = Depends(get_session)) -> CaseReport:
    """Get a case report by id"""
    return await CaseReportService(session).get(id)


@router.delete("/{id}", response_model=CaseReport, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.require_admin())
) -> CaseReport:
    """Delete a case report by id"""
    return await CaseReportService(session).delete(id)

from logging import debug
from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.orm import selectinload
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import CaseReport, Campaign
from api.models.query import CaseReportResult, CaseReportDraft
from enacit4r_sql.utils.query import QueryBuilder


class CaseReportQueryBuilder(QueryBuilder):

    def build_count_query_with_joins(self, filter):
        query = self.build_count_query()
        query = self._apply_joins(query, filter)
        return query

    def build_query_with_joins(self, total_count, filter, fields=None):
        start, end, query = self.build_query(total_count, fields)
        query = self._apply_joins(query, filter)
        return start, end, query

    def _apply_joins(self, query, filter):
        query = query.distinct()
        return query


class CaseReportService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(self) -> int:
        """Count all case reports"""
        count = (await self.session.exec(text("select count(id) from casereport"))).scalar()
        return count

    async def get(self, id: int) -> CaseReport:
        """Get a case report by id"""
        res = await self.session.exec(
            select(CaseReport).where(
                CaseReport.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="CaseReport not found")
        return entity

    async def get_by_token(self, token: str) -> CaseReport:
        """Get a case report by token"""
        res = await self.session.exec(
            select(CaseReport).where(
                CaseReport.token == token))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="CaseReport not found")
        return entity

    async def delete(self, id: int) -> CaseReport:
        """Delete a case report by id"""
        res = await self.session.exec(
            select(CaseReport).where(CaseReport.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="CaseReport not found")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list) -> CaseReportResult:
        """Get all case reports matching filter and range"""
        builder = CaseReportQueryBuilder(
            CaseReport, filter, sort, range, {})

        # Do a query to satisfy total count
        count_query = builder.build_count_query_with_joins(filter)
        total_count_query = await self.session.exec(count_query)
        total_count = total_count_query.one()

        # Main query
        start, end, query = builder.build_query_with_joins(
            total_count, filter, fields)

        # Execute query
        results = await self.session.exec(query)
        entities = results.all()

        return CaseReportResult(
            total=total_count,
            skip=start,
            limit=end - start + 1,
            data=entities
        )

    async def createOrUpdate(self, payload: CaseReportDraft, campaign: Campaign) -> CaseReport:
        """Create or update a case report based on its token"""
        res = await self.session.exec(
            select(CaseReport).where(CaseReport.token == payload.token)
        )
        entity = res.one_or_none()
        if entity:
            return await self.update(entity.id, payload, campaign)
        return await self.create(payload, campaign)

    async def create(self, payload: CaseReportDraft, campaign: Campaign) -> CaseReport:
        """Create a new case report"""
        entity = CaseReport(**payload.model_dump())
        entity.campaign_id = campaign.id
        entity.company_id = campaign.company_id
        self.session.add(entity)
        await self.session.commit()
        return entity

    async def update(self, id: int, payload: CaseReportDraft, campaign: Campaign) -> CaseReport:
        """Update a case report"""
        res = await self.session.exec(
            select(CaseReport).where(CaseReport.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="CaseReport not found")
        for key, value in payload.model_dump().items():
            print(key, value)
            if key not in ["id"]:
                setattr(entity, key, value)
        entity.campaign_id = campaign.id
        entity.company_id = campaign.company_id
        await self.session.commit()
        return entity

from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import CompanyAction
from api.models.query import CompanyActionResult, CompanyActionDraft
from enacit4r_sql.utils.query import QueryBuilder
from api.auth import User


class CompanyActionQueryBuilder(QueryBuilder):

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


class CompanyActionService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(self) -> int:
        """Count all company actions"""
        count = (await self.session.exec(text("select count(id) from companyaction"))).scalar()
        return count

    async def get(self, id: int) -> CompanyAction:
        """Get a company action by id"""
        res = await self.session.exec(
            select(CompanyAction).where(
                CompanyAction.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company action not found")
        return entity

    async def delete(self, id: int) -> CompanyAction:
        """Delete a company action by id"""
        res = await self.session.exec(
            select(CompanyAction).where(CompanyAction.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company action not found")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list) -> CompanyActionResult:
        """Get all company actions matching filter and range"""
        builder = CompanyActionQueryBuilder(
            CompanyAction, filter, sort, range, {})

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

        return CompanyActionResult(
            total=total_count,
            skip=start,
            limit=end - start + 1,
            data=entities
        )

    async def create(self, payload: CompanyActionDraft, user: User = None) -> CompanyAction:
        """Create a new company action"""
        entity = CompanyAction(**payload.model_dump())
        self.session.add(entity)
        await self.session.commit()
        return entity

    async def update(self, id: int, payload: CompanyActionDraft, user: User = None) -> CompanyAction:
        """Update a company action"""
        res = await self.session.exec(
            select(CompanyAction).where(CompanyAction.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company action not found")
        for key, value in payload.model_dump().items():
            # print(key, value)
            if key not in ["id"]:
                setattr(entity, key, value)
        await self.session.commit()
        return entity

    async def get_company_actions(self, company_id: int) -> list[CompanyAction]:
        """Get all actions for a company"""
        res = await self.session.exec(
            select(CompanyAction).where(CompanyAction.company_id == company_id)
        )
        entities = res.all()
        return entities

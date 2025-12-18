from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import CompanyAction
from api.models.query import CompanyActionResult, CompanyActionDraft
from enacit4r_sql.utils.query import QueryBuilder
from api.auth import User, is_admin, require_admin_or_perm
from api.services.companies import CompanyService
from api.services.entities import EntityService


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


class CompanyActionService(EntityService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count(self) -> int:
        """Count all company actions"""
        count = (await self.session.exec(text("select count(id) from companyaction"))).scalar()
        return count

    async def get(self, id: int, user: User = None) -> CompanyAction:
        """Get a company action by id"""
        res = await self.session.exec(
            select(CompanyAction).where(
                CompanyAction.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company action not found")
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "read")
        return entity

    async def delete(self, id: int, user: User = None) -> CompanyAction:
        """Delete a company action by id"""
        res = await self.session.exec(
            select(CompanyAction).where(CompanyAction.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company action not found")
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "update")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list, user: User = None) -> CompanyActionResult:
        """Get all company actions matching filter and range"""
        # Add permission filter
        if user is not None and not is_admin(user):
            permitted_company_ids = await CompanyService(self.session).list_permitted_ids(user, "read")
            if permitted_company_ids:
                if filter is None:
                    filter = {}
                if "company_id" in filter:
                    filter["company_id"] = self.merge_ids_filter(
                        filter["company_id"], permitted_company_ids)
                else:
                    filter["company_id"] = permitted_company_ids
            else:
                # No permitted campaigns, return empty result
                # Assuming no campaign has company_id -1
                filter["company_id"] = [-1]

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

        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "update")

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

        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "update")

        for key, value in payload.model_dump().items():
            # print(key, value)
            if key not in ["id"]:
                setattr(entity, key, value)
        await self.session.commit()
        return entity

    async def get_company_actions(self, company_id: int, user: User = None) -> list[CompanyAction]:
        """Get all actions for a company"""
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{company_id}", "read")

        res = await self.session.exec(
            select(CompanyAction).where(CompanyAction.company_id == company_id)
        )
        entities = res.all()
        return entities

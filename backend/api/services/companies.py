from logging import debug
from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.orm import selectinload
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import Company
from api.models.query import CompanyResult
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime
from api.auth import User
from api.services.authz import ACLService


class CompanyQueryBuilder(QueryBuilder):

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


class CompanyService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(self) -> int:
        """Count all compagnies"""
        count = (await self.session.exec(text("select count(id) from company"))).scalar()
        return count

    async def get(self, id: int) -> Company:
        """Get a company by id"""
        res = await self.session.exec(
            select(Company).where(
                Company.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company not found")
        return entity

    async def delete(self, id: int) -> Company:
        """Delete a company by id"""
        res = await self.session.exec(
            select(Company).where(Company.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company not found")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list) -> CompanyResult:
        """Get all compagnies matching filter and range"""
        builder = CompanyQueryBuilder(
            Company, filter, sort, range, {})

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

        return CompanyResult(
            total=total_count,
            skip=start,
            limit=end - start + 1,
            data=entities
        )

    async def create(self, payload: Company, user: User = None) -> Company:
        """Create a new company"""
        entity = Company(**payload.model_dump())
        entity.created_at = datetime.now()
        entity.updated_at = datetime.now()
        if user:
            entity.created_by = user.username
            entity.updated_by = user.username
        self.session.add(entity)
        await self.session.commit()
        self.apply_admin_permissions(entity)

        return entity

    async def update(self, id: int, payload: Company, user: User = None) -> Company:
        """Update a company"""
        res = await self.session.exec(
            select(Company).where(Company.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company not found")
        for key, value in payload.model_dump().items():
            print(key, value)
            if key not in ["id", "created_at", "updated_at", "created_by", "updated_by"]:
                setattr(entity, key, value)
        entity.updated_at = datetime.now()
        if user:
            entity.updated_by = user.username
        await self.session.commit()
        self.apply_admin_permissions(entity)
        return entity

    def apply_admin_permissions(self, entity: Company):
        resource = self.as_resource(entity)
        acl_service = ACLService(self.session)
        # Note: permissions are only applied
        acl_service.delete_user_permissions(resource)
        if entity.administrators:
            for admin in entity.administrators:
                acl_service.apply_user_permission(resource, "*", admin)
                pass

    def as_resource(self, entity: Company):
        return f"company:{entity.id}"

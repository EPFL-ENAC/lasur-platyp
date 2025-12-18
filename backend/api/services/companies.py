from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import Company
from api.models.query import CompanyResult
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime
from api.auth import User, check_admin_or_perm, is_admin, require_admin_or_perm
from api.services.authz import ACLService
from api.services.entities import EntityService


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


class CompanyService(EntityService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count(self) -> int:
        """Count all companies"""
        count = (await self.session.exec(text("select count(id) from company"))).scalar()
        return count

    async def list_all_ids(self) -> list[int]:
        """List all company ids"""
        res = await self.session.exec(
            select(Company.id)
        )
        ids = res.all()
        return ids

    async def list_permitted_ids(self, user: User, permission: str) -> list[int]:
        """List all company ids the user has the given permission on"""
        permitted_ids = []
        all_ids = await self.list_all_ids()
        for company_id in all_ids:
            permitted = await check_admin_or_perm(user, f"company:{company_id}", permission)
            if permitted:
                permitted_ids.append(company_id)
        return permitted_ids

    async def get(self, id: int, user: User = None) -> Company:
        """Get a company by id"""
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{id}", "read")
        res = await self.session.exec(
            select(Company).where(
                Company.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company not found")
        return entity

    async def delete(self, id: int, user: User = None) -> Company:
        """Delete a company by id"""
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{id}", "delete")
        res = await self.session.exec(
            select(Company).where(Company.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Company not found")
        await self.session.delete(entity)
        await self.session.commit()
        await self.delete_permissions(entity)
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list, user: User = None) -> CompanyResult:
        """Get all companies matching filter and range"""
        # Add permission filter
        if user is not None and not is_admin(user):
            if filter is None:
                filter = {}
            # Restrict to companies the user has "read" permission on
            # Note: this is a simple implementation, may not scale well with many companies
            # A more efficient implementation would require a join with the ACL table
            permitted_ids = await self.list_permitted_ids(user, "read")
            if permitted_ids:
                if "id" in filter:
                    filter["id"] = self.merge_ids_filter(
                        filter["id"], permitted_ids)
                else:
                    filter["id"] = permitted_ids
            else:
                # No permitted companies, return empty result
                filter["id"] = [-1]  # Assuming no company has id -1

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
            # Ensure creating user is in administrators list
            if not entity.administrators:
                entity.administrators = [user.email]
            elif user.email not in entity.administrators:
                entity.administrators.append(user.email)
        self.session.add(entity)
        await self.session.commit()
        await self.apply_admin_permissions(entity)
        return entity

    async def update(self, id: int, payload: Company, user: User = None) -> Company:
        """Update a company"""
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{id}", "update")
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
            # Ensure updating user is in administrators list
            if not entity.administrators:
                entity.administrators = [user.email]
            elif user.email not in entity.administrators:
                entity.administrators.append(user.email)
        await self.session.commit()
        await self.apply_admin_permissions(entity)
        return entity

    async def apply_admin_permissions(self, entity: Company):
        resource = self.as_resource(entity)
        acl_service = ACLService(self.session)
        # Note: permissions are only applied
        await acl_service.delete_user_permissions(resource)
        if entity.administrators:
            for admin in entity.administrators:
                await acl_service.apply_user_permission(resource, "*", admin)

    async def delete_permissions(self, entity: Company):
        resource = self.as_resource(entity)
        acl_service = ACLService(self.session)
        await acl_service.delete_user_permissions(resource)

    def as_resource(self, entity: Company):
        return f"company:{entity.id}"

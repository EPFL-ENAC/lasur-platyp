from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlmodel import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from api.models.domain import Campaign, Workplace
from api.models.query import CampaignResult, CampaignDraft
from api.services.companies import CompanyService
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime
from api.auth import User, require_admin_or_perm, is_admin
from api.services.entities import EntityService


class CampaignQueryBuilder(QueryBuilder):

    def build_count_query_with_joins(self, filter):
        query = self.build_count_query()
        query = self._apply_joins(query, filter)
        return query

    def build_query_with_joins(self, total_count, filter, fields=None):
        start, end, query = self.build_query(total_count, fields)
        if fields is None or fields == [] or (len(fields) > 0 and "workplaces" in fields):
            query = self._apply_joins(query, filter).options(
                selectinload(Campaign.workplaces))
        return start, end, query

    def _apply_joins(self, query, filter):
        query = query.distinct()
        return query


class CampaignService(EntityService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count(self) -> int:
        """Count all campaigns"""
        count = (await self.session.exec(text("select count(id) from campaign"))).scalar()
        return count

    async def get(self, id: int, user: User = None) -> Campaign:
        """Get a campaign by id"""
        res = await self.session.exec(
            select(Campaign)
            .options(selectinload(Campaign.workplaces))
            .where(Campaign.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Campaign not found")
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "read")
        return entity

    async def get_by_slug(self, slug: str) -> Campaign:
        """Get a campaign by slug"""
        res = await self.session.exec(
            select(Campaign)
            .options(selectinload(Campaign.workplaces))
            .where(Campaign.slug == slug))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Campaign not found")
        return entity

    async def delete(self, id: int, user: User = None) -> Campaign:
        """Delete a campaign by id"""
        res = await self.session.exec(
            select(Campaign).where(Campaign.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Campaign not found")
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "update")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list, user: User = None) -> CampaignResult:
        """Get all campaigns matching filter and range"""
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

        builder = CampaignQueryBuilder(
            Campaign, filter, sort, range, {})

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

        return CampaignResult(
            total=total_count,
            skip=start,
            limit=end - start + 1,
            data=entities
        )

    async def create(self, payload: CampaignDraft, user: User = None) -> Campaign:
        """Create a new campaign"""
        workplaces = payload.workplaces
        payload_dict = payload.model_dump(exclude={'workplaces'})
        entity = Campaign(**payload_dict)

        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "update")

        entity.created_at = datetime.now()
        entity.updated_at = datetime.now()
        if user:
            entity.created_by = user.username
            entity.updated_by = user.username
        self.session.add(entity)
        await self.session.commit()
        # Add workplaces
        for wp in workplaces:
            wp_entity = wp.model_dump()
            wp_entity["campaign_id"] = entity.id
            self.session.add(Workplace.model_validate(wp_entity))
        await self.session.commit()
        return entity

    async def update(self, id: int, payload: CampaignDraft, user: User = None) -> Campaign:
        """Update a campaign"""
        workplaces = payload.workplaces
        res = await self.session.exec(
            select(Campaign)
            .options(selectinload(Campaign.workplaces))
            .where(Campaign.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Campaign not found")

        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "update")

        for key, value in payload.model_dump().items():
            # print(key, value)
            if key not in ["id", "created_at", "updated_at", "created_by", "updated_by", "workplaces"]:
                setattr(entity, key, value)
        entity.updated_at = datetime.now()
        if user:
            entity.updated_by = user.username
        # Update workplaces
        incoming_wp_ids = {wp.id for wp in workplaces if wp.id is not None}
        # Delete removed workplaces
        for wp in entity.workplaces:
            if wp.id not in incoming_wp_ids:
                await self.session.delete(wp)
        # Add or update workplaces
        for wp in workplaces:
            if wp.id is None:
                # New workplace
                wp_entity = wp.model_dump()
                wp_entity["campaign_id"] = entity.id
                self.session.add(Workplace.model_validate(wp_entity))
            else:
                # Update existing workplace
                for existing_wp in entity.workplaces:
                    if existing_wp.id == wp.id:
                        for key, value in wp.model_dump().items():
                            if key not in ["id", "campaign_id"]:
                                setattr(existing_wp, key, value)
                        break
        await self.session.commit()
        return entity

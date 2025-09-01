from html import entities
from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy import select, func, and_, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Integer, select
from fastapi import HTTPException
from api.models.domain import Record, Campaign
from api.models.query import RecordResult, RecordDraft, Frequencies, Frequency
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime


class RecordQueryBuilder(QueryBuilder):

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


class RecordService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(self) -> int:
        """Count all records"""
        count = (await self.session.exec(text("select count(id) from record"))).scalar()
        return count

    async def count_completed(self, filter: dict) -> int:
        """Count all completed records"""
        builder = RecordQueryBuilder(
            Record, filter, [], [], {})
        count_query = builder.build_count_query_with_joins(filter)
        count_query = count_query.where(
            Record.typo['reco'] != cast('null', JSONB))
        count = (await self.session.exec(count_query)).one()
        return count

    async def get(self, id: int) -> Record:
        """Get a record by id"""
        res = await self.session.exec(
            select(Record).where(
                Record.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Record not found")
        return entity

    async def get_by_token(self, token: str) -> Record:
        """Get a record by token"""
        res = await self.session.exec(
            select(Record).where(
                Record.token == token))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Record not found")
        return entity

    async def delete(self, id: int) -> Record:
        """Delete a record by id"""
        res = await self.session.exec(
            select(Record).where(Record.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Record not found")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list) -> RecordResult:
        """Get all records matching filter and range"""
        builder = RecordQueryBuilder(
            Record, filter, sort, range, {})

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

        return RecordResult(
            total=total_count,
            skip=start,
            limit=end - start + 1,
            data=entities
        )

    async def createOrUpdate(self, payload: RecordDraft, campaign: Campaign) -> Record:
        """Create or update a record based on its token"""
        res = await self.session.exec(
            select(Record).where(Record.token == payload.token)
        )
        entity = res.one_or_none()
        if entity:
            return await self.update(entity.id, payload, campaign)
        return await self.create(payload, campaign)

    async def create(self, payload: RecordDraft, campaign: Campaign) -> Record:
        """Create a new record"""
        entity = Record(**payload.model_dump())
        entity.campaign_id = campaign.id
        entity.company_id = campaign.company_id
        entity.created_at = datetime.now()
        entity.updated_at = datetime.now()
        self.session.add(entity)
        await self.session.commit()
        return entity

    async def update(self, id: int, payload: RecordDraft, campaign: Campaign = None) -> Record:
        """Update a record"""
        res = await self.session.exec(
            select(Record).where(Record.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Record not found")
        for key, value in payload.model_dump().items():
            # print(key, value)
            if key not in ["id", "created_at", "updated_at"]:
                setattr(entity, key, value)
        if entity.created_at is None:  # legacy from db upgrade
            entity.created_at = datetime.now()
        entity.updated_at = datetime.now()
        entity.campaign_id = campaign.id if campaign else entity.campaign_id
        entity.company_id = campaign.company_id if campaign else entity.company_id
        await self.session.commit()
        return entity

    async def get_equipments_frequencies(self, filter: dict) -> Frequencies:
        total_count = await self.count_completed(filter)
        if total_count == 0:
            return Frequencies(total=0, data=[])

        results = await self.find(filter, fields=[], sort=[], range=[])
        ids = [entity.id for entity in results.data]

        # Create a subquery/CTE that expands the JSON array
        expanded = (
            select(
                Record.id,
                func.jsonb_array_elements_text(
                    Record.data['equipments']).label('equipment')
            )
            .select_from(Record)
            .where(and_(Record.id.in_(ids), Record.typo['reco'] != cast('null', JSONB)))
            .subquery()
        )

        # Main query
        query = (
            select(
                expanded.c.equipment,
                func.count().label('usage_count')
            )
            .group_by(expanded.c.equipment)
            .order_by(func.count().desc())
        )

        counts = await self.session.exec(query)

        return Frequencies(
            field='equipments',
            total=total_count,
            data=[
                Frequency(
                    value=row.equipment,
                    count=row.usage_count
                )
                for row in counts
            ]
        )

    async def get_constraints_frequencies(self, filter: dict) -> Frequencies:
        total_count = await self.count_completed(filter)
        if total_count == 0:
            return Frequencies(total=0, data=[])

        results = await self.find(filter, fields=[], sort=[], range=[])
        ids = [entity.id for entity in results.data]

        # Create a subquery/CTE that expands the JSON array
        expanded = (
            select(
                Record.id,
                func.jsonb_array_elements_text(
                    Record.data['constraints']).label('constraint')
            )
            .select_from(Record)
            .where(and_(Record.id.in_(ids), Record.typo['reco'] != cast('null', JSONB)))
            .subquery()
        )

        # Main query
        query = (
            select(
                expanded.c.constraint,
                func.count().label('usage_count')
            )
            .group_by(expanded.c.constraint)
            .order_by(func.count().desc())
        )

        counts = await self.session.exec(query)

        return Frequencies(
            field='constraints',
            total=total_count,
            data=[
                Frequency(
                    value=row.constraint,
                    count=row.usage_count
                )
                for row in counts
            ]
        )

    async def get_travel_time_frequencies(self, filter: dict) -> Frequencies:
        total_count = await self.count_completed(filter)
        if total_count == 0:
            return Frequencies(total=0, data=[])

        results = await self.find(filter, fields=[], sort=[], range=[])
        ids = [entity.id for entity in results.data]

        # Create a subquery/CTE that expands the JSON array
        expanded = (
            select(
                Record.id,
                Record.data['travel_time'].astext.label('travel_time')
            )
            .select_from(Record)
            .where(and_(Record.id.in_(ids), Record.typo['reco'] != cast('null', JSONB)))
            .subquery()
        )

        # Main query
        query = (
            select(
                expanded.c.travel_time,
                func.count().label('usage_count')
            )
            .group_by(expanded.c.travel_time)
            .order_by(func.count().desc())
        )

        counts = await self.session.exec(query)

        return Frequencies(
            field='travel_time',
            total=total_count,
            data=[
                Frequency(
                    value=row.travel_time,
                    count=row.usage_count
                )
                for row in counts
            ]
        )

    async def get_mod_stats(self, mod: str, filter: dict):
        total_count = await self.count_completed(filter)
        if total_count == 0:
            return Frequencies(total=0, data=[])

        results = await self.find(filter, fields=[], sort=[], range=[])
        ids = [entity.id for entity in results.data]

        # Create a subquery/CTE that expands the JSON array
        expanded = (
            select(
                Record.id,
                Record.data[mod].astext.label('mod')
            )
            .select_from(Record)
            .where(and_(Record.id.in_(ids), Record.typo['reco'] != cast('null', JSONB)))
            .subquery()
        )

        # Main query
        query = (
            select(
                expanded.c.mod,
                func.sum(cast(expanded.c.mod, Integer)).label('usage_sum'),
                func.count().label('usage_count')
            )
            .group_by(expanded.c.mod)
            .order_by(func.count().desc())
        )

        counts = await self.session.exec(query)

        return Frequencies(
            field=mod,
            total=total_count,
            data=[
                Frequency(
                    value=row.mod,
                    count=row.usage_count,
                    sum=row.usage_sum
                )
                for row in counts
            ]
        )

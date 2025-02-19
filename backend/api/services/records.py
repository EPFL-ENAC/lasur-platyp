from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import Record, Campaign
from api.models.query import RecordResult, RecordDraft
from enacit4r_sql.utils.query import QueryBuilder


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
        self.session.add(entity)
        await self.session.commit()
        return entity

    async def update(self, id: int, payload: RecordDraft, campaign: Campaign) -> Record:
        """Update a record"""
        res = await self.session.exec(
            select(Record).where(Record.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Record not found")
        for key, value in payload.model_dump().items():
            print(key, value)
            if key not in ["id"]:
                setattr(entity, key, value)
        entity.campaign_id = campaign.id
        entity.company_id = campaign.company_id
        await self.session.commit()
        return entity

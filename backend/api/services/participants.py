from logging import debug
from typing import List
import secrets
from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import Participant
from api.models.query import ParticipantResult, ParticipantData, ParticipantDraft
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime
from api.auth import User
import pandas as pd
import numpy as np


class ParticipantQueryBuilder(QueryBuilder):

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


class ParticipantService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(self) -> int:
        """Count all participants"""
        count = (await self.session.exec(text("select count(id) from participant"))).scalar()
        return count

    async def get(self, id: int) -> Participant:
        """Get a participant by id"""
        res = await self.session.exec(
            select(Participant).where(
                Participant.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")
        return entity

    async def get_by_token(self, token: str) -> Participant:
        """Get a participant by token"""
        res = await self.session.exec(
            select(Participant).where(
                Participant.token == token))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")
        return entity

    async def delete(self, id: int) -> Participant:
        """Delete a participant by id"""
        res = await self.session.exec(
            select(Participant).where(Participant.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list) -> ParticipantResult:
        """Get all participants matching filter and range"""
        builder = ParticipantQueryBuilder(
            Participant, filter, sort, range, {})

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

        return ParticipantResult(
            total=total_count,
            skip=start,
            limit=end - start + 1,
            data=entities
        )

    async def create(self, payload: ParticipantDraft, user: User = None) -> Participant:
        """Create a new participant"""
        res = await self.session.exec(
            select(Participant).where(
                Participant.identifier == payload.identifier, Participant.campaign_id == payload.campaign_id)
        )
        entity = res.one_or_none()
        if entity:
            raise HTTPException(
                status_code=400, detail="Participant identifier already exists")
        entity = Participant(**payload.model_dump())
        entity.created_at = datetime.now()
        entity.updated_at = datetime.now()
        if user:
            entity.created_by = user.username
            entity.updated_by = user.username
        # generate unique token
        found = True
        while found:
            entity.token = secrets.token_urlsafe(16)
            res = await self.session.exec(
                select(Participant).where(
                    Participant.token == entity.token)
            )
            found = res.one_or_none() is not None

        self.session.add(entity)
        await self.session.commit()
        return entity

    async def update(self, id: int, payload: ParticipantDraft, user: User = None) -> Participant:
        """Update a participant"""
        res = await self.session.exec(
            select(Participant).where(Participant.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Participant not found")
        if entity.identifier != payload.identifier:
            # changing the identifier is allowed but make sure it is unique in the campaign
            res = await self.session.exec(
                select(Participant).where(
                    Participant.identifier == payload.identifier, Participant.campaign_id == entity.campaign_id)
            )
            if res.one_or_none() is not None:
                raise HTTPException(
                    status_code=400, detail="Participant identifier already exists")
        for key, value in payload.model_dump().items():
            print(key, value)
            if key not in ["id", "created_at", "updated_at", "created_by", "updated_by", "token"]:
                setattr(entity, key, value)
        entity.updated_at = datetime.now()
        if user:
            entity.updated_by = user.username
        await self.session.commit()
        return entity

    async def parse(self, io) -> List[ParticipantData]:
        df = pd.read_excel(io, sheet_name=0)
        df = self._clean_header(df)
        for column in df.columns:
            df[column] = self._mormalize_column(df, column)
        # To explicitly convert NaN to None
        df = df.replace({np.nan: None})

        data = []
        for i, row in df.iterrows():
            datum = row.to_dict()
            if datum["identifier"] is not None:
                data.append(ParticipantData(data=datum))
        return data

    def _clean_header(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove first row
        # df = df.iloc[1:]
        # Remove non-printable/invisible characters from column names
        df.columns = df.columns.str.replace(
            r'[^\x20-\x7E]', ' ', regex=True)
        df.columns = df.columns.str.strip().str.lower()
        return df

    def _mormalize_column(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        # Lower case and replace non-printable/invisible characters with space and do stripping
        if df[column].dtype == "string":
            return df[column].str.lower().str.replace(
                r'[^\x20-\x7E]', ' ', regex=True).str.strip()
        return df[column]

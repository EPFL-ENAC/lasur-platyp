from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy import select, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import select
from fastapi import HTTPException
from api.models.domain import Record, Campaign
from api.models.query import RecordResult, RecordDraft, LocationFilter
from api.auth import User, is_admin, require_admin_or_perm
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime
import pandas as pd
from shapely.geometry import Point, Polygon as ShapelyPolygon, MultiPolygon as ShapelyMultiPolygon

from api.services.companies import CompanyService
from api.services.entities import EntityService


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


class RecordService(EntityService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

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

    async def get(self, id: int, user: User = None) -> Record:
        """Get a record by id"""
        res = await self.session.exec(
            select(Record).where(
                Record.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Record not found")
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "read")
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

    async def delete(self, id: int, user: User = None) -> Record:
        """Delete a record by id"""
        res = await self.session.exec(
            select(Record).where(Record.id == id)
        )
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Record not found")
        if user is not None and not is_admin(user):
            await require_admin_or_perm(user, f"company:{entity.company_id}", "update")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def find(self, filter: dict, fields: list, sort: list, range: list, user: User = None) -> RecordResult:
        """Get all records matching filter and range"""
        if user is not None and not is_admin(user):
            permitted_company_ids = await CompanyService(self.session).list_permitted_ids(user, "read")
            if filter is None:
                filter = {}
            if permitted_company_ids:
                if "company_id" in filter:
                    filter["company_id"] = self.merge_ids_filter(
                        filter["company_id"], permitted_company_ids)
                else:
                    filter["company_id"] = permitted_company_ids
            else:
                # No permitted records, return empty result
                # Assuming no record has company_id -1
                filter["company_id"] = [-1]

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

    async def get_dataframe(self, filter: dict, flat: bool = False, user: User = None) -> pd.DataFrame:
        """Get a DataFrame representation of the records.

        Args:
            filter (dict): The filter criteria for the records.
            flat (bool, optional): Whether to flatten the DataFrame. Defaults to False.
            user (User, optional): The user requesting the data. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame representation of the records.
        """
        results = await self.find(filter, fields=[], sort=[], range=[], user=user)
        # Read results into a pandas DataFrame
        df = pd.DataFrame([result.model_dump() for result in results.data])
        if not flat:
            return df
        # Flatten nested JSON fields in 'data' and 'typo'
        for col in ['data', 'typo']:
            if col in df.columns:
                # Replace NaN with empty dict
                df[col] = df[col].apply(
                    lambda x: x if isinstance(x, dict) else {})
                # Flatten the JSON column
                df_data = df[col].apply(self.flatten_json).apply(pd.Series)
                # Filter out empty columns
                df_data = df_data.loc[:, df_data.notna().any()]
                # Filter out columns with empty names
                df_data = df_data.loc[:, df_data.columns.str.strip() != '']
                # Prefix column names
                df_data = df_data.add_prefix(f"{col}.")
                # Combine with original DataFrame
                df = pd.concat(
                    [df.drop(columns=[col]), df_data], axis=1)
        # Return a simple message for testing purposes
        # return {"message": f"Columns count: {len(df_flat.columns)}", "columns": df_flat.columns.tolist()}
        return df

    def filter_completed(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get a DataFrame representation of the completed records.

        Args:
            df (pd.DataFrame): The DataFrame containing record data.

        Returns:
            pd.DataFrame: A DataFrame filtered to include only completed records.
        """
        # Filter records with values in column typo.reco_dt2.0
        df = df[df['typo.reco.reco_dt2.0'].notna()]
        return df

    def filter_by_workplace_location(self, df: pd.DataFrame, filter: LocationFilter) -> pd.DataFrame:
        geom = filter.geo_within.geometry
        shapely_polygon = None
        # Depending on geometry type, extract coordinates
        if geom.type == "Polygon":
            coordinates = geom.coordinates[0]  # Outer ring
            shapely_polygon = ShapelyPolygon(coordinates)
        elif geom.type == "MultiPolygon":
            # Each element in geom.coordinates is a polygon (list of rings)
            polygons = [ShapelyPolygon(polygon[0])
                        for polygon in geom.coordinates]
            shapely_polygon = ShapelyMultiPolygon(polygons)
        else:
            raise ValueError(
                "Unsupported geometry type for workplace location filter")

        def contains_point(lat, lon):
            point = Point(lon, lat)  # Note: Point takes (x, y) = (lon, lat)
            return shapely_polygon.contains(point)

        # Filter out rows with missing or NaN lat/lon before applying polygon filter
        df = df[
            pd.notna(df['data.workplace.lat']) &
            pd.notna(df['data.workplace.lon'])
        ]
        df = df[df.apply(lambda row: contains_point(
            row['data.workplace.lat'], row['data.workplace.lon']), axis=1)]
        return df

    def flatten_json(self, obj, parent_key="", sep="."):
        """Recursively flatten JSON with lists indexed."""
        items = []

        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                items.extend(self.flatten_json(v, new_key, sep=sep).items())

        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_key = f"{parent_key}{sep}{i}"
                items.extend(self.flatten_json(v, new_key, sep=sep).items())

        else:
            items.append((parent_key, obj))

        return dict(items)

from api.db import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy import Float, select, func, and_, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Integer, select
from fastapi import HTTPException
from api.models.domain import Record, Campaign
from api.models.query import Stats, Links, RecordResult, RecordDraft, Frequencies, Frequency, Emissions
from enacit4r_sql.utils.query import QueryBuilder
from datetime import datetime
import pandas as pd


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

    async def get_recommendation_frequencies(self, filter: dict) -> Frequencies:
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
                    Record.typo["reco"]["reco_dt2"]).label('reco')
            )
            .select_from(Record)
            .where(and_(Record.id.in_(ids), Record.typo['reco'] != cast('null', JSONB)))
            .subquery()
        )

        # Main query
        query = (
            select(
                expanded.c.reco,
                func.count().label('reco_count')
            )
            .group_by(expanded.c.reco)
            .order_by(func.count().desc())
        )

        counts = await self.session.exec(query)

        return Frequencies(
            field='reco_dt2',
            total=total_count,
            data=[
                Frequency(
                    value=row.reco,
                    count=row.reco_count
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

    async def get_mod_co2_emissions(self, mod: str, filter: dict) -> Emissions:
        total_count = await self.count_completed(filter)
        if total_count == 0:
            return Emissions(field=mod, total=0, distances=0, journeys=0, emissions=0)

        results = await self.find(filter, fields=[], sort=[], range=[])
        ids = [entity.id for entity in results.data]

        mod_emissions = {'car': 186, 'train': 8, 'pub': 25,
                         'bike': 6, 'moto': 155, 'walking': 0}

        # calculate distances between origin (lat, lon) and workplace (lat, lon)
        origin_lat = cast(Record.data["origin"]["lat"].astext, Float)
        origin_lon = cast(Record.data["origin"]["lon"].astext, Float)
        work_lat = cast(Record.data["workplace"]["lat"].astext, Float)
        work_lon = cast(Record.data["workplace"]["lon"].astext, Float)

        # Main query
        query = (
            select(
                Record.id,
                (6371 * func.acos(
                    func.cos(func.radians(origin_lat)) *
                    func.cos(func.radians(work_lat)) *
                    func.cos(func.radians(work_lon) - func.radians(origin_lon)) +
                    func.sin(func.radians(origin_lat)) *
                    func.sin(func.radians(work_lat))
                )).label("distance_km"),
                Record.data[mod].astext.label('mod')
            ).where(and_(Record.id.in_(ids), Record.typo['reco'] != cast('null', JSONB)))
        )

        counts = await self.session.exec(query)
        rows = [row for row in counts if row.distance_km is not None and row.mod is not None and int(
            row.mod) > 0]
        distances = [row.distance_km * 1.3 for row in rows]
        journeys = [45 * 2 * int(row.mod) for row in rows]
        emissions = [row.distance_km * 1.3 * 45 * 2 * int(
            row.mod) * mod_emissions[mod.replace("freq_mod_", "")] / 1000 for row in rows]
        return Emissions(field=mod, total=total_count, distances=sum(distances), journeys=sum(journeys), emissions=sum(emissions))

    async def get_mod_reco_links(self, filter: dict) -> Links:
        total_count = await self.count_completed(filter)
        if total_count == 0:
            return Links(total=0, data=[])

        results = await self.find(filter, fields=[], sort=[], range=[])
        ids = [entity.id for entity in results.data]

        # JSON fields
        train_val = cast(Record.data["freq_mod_train"].astext, Integer)
        car_val = cast(Record.data["freq_mod_car"].astext, Integer)
        pub_val = cast(Record.data["freq_mod_pub"].astext, Integer)
        bike_val = cast(Record.data["freq_mod_bike"].astext, Integer)
        moto_val = cast(Record.data["freq_mod_moto"].astext, Integer)
        walking_val = cast(Record.data["freq_mod_walking"].astext, Integer)
        combined_val = Record.data["freq_mod_combined"].astext

        query = (
            select(
                Record.id,
                (train_val > 0).label("train"),
                (car_val > 0).label("car"),
                (pub_val > 0).label("pub"),
                (bike_val > 0).label("bike"),
                (moto_val > 0).label("moto"),
                (walking_val > 0).label("walking"),
                combined_val.label("combined"),
                # first reco only
                Record.typo["reco"]["reco_dt2"][0].astext.label('reco')
            )
            .select_from(Record)
            .where(and_(Record.id.in_(ids), Record.typo['reco'] != cast('null', JSONB)))
        )

        rows = await self.session.exec(query)
        counts = {}
        for row in rows:
            for mod in ['train', 'car', 'pub', 'bike', 'moto', 'walking']:
                if getattr(row, mod):
                    reco = row.reco
                    mod_counts = counts.get(mod, {})
                    mod_counts[reco] = mod_counts.get(reco, 0) + 1
                    counts[mod] = mod_counts
        links = [{"source": mod, "target": reco, "value": count} for mod,
                 reco_counts in counts.items() for reco, count in reco_counts.items()]
        return Links(total=total_count, data=links)

    def compute_equipments_frequencies(self, df: pd.DataFrame) -> Frequencies:
        """Compute equipments frequencies from a DataFrame of records."""
        # Find columns starting with 'data.equipments.'
        equipments_cols = [
            col for col in df.columns if col.startswith('data.equipments.')]
        # Each column contains the name of an equipment if present, else NaN
        all_equipments = []
        for col in equipments_cols:
            all_equipments.extend(
                df[col].dropna().tolist()
            )
        equipment_counts = pd.Series(all_equipments).value_counts()

        return Frequencies(
            field='equipments',
            total=len(df),
            data=[
                Frequency(
                    value=equipment,
                    count=count
                )
                for equipment, count in equipment_counts.items()
            ]
        )

    def compute_constraints_frequencies(self, df: pd.DataFrame) -> Frequencies:
        """Compute constraints frequencies from a DataFrame of records."""
        # Find columns starting with 'data.constraints.'
        constraints_cols = [
            col for col in df.columns if col.startswith('data.constraints.')]
        # Each column contains the name of a constraint if present, else NaN
        all_constraints = []
        for col in constraints_cols:
            all_constraints.extend(
                df[col].dropna().tolist()
            )
        constraint_counts = pd.Series(all_constraints).value_counts()

        return Frequencies(
            field='constraints',
            total=len(df),
            data=[
                Frequency(
                    value=constraint,
                    count=count
                )
                for constraint, count in constraint_counts.items()
            ]
        )

    def compute_travel_time_frequencies(self, df: pd.DataFrame) -> Frequencies:
        """Compute travel time frequencies from a DataFrame of records."""
        travel_time_series = df['data.travel_time'].dropna().astype(str)
        travel_time_counts = travel_time_series.value_counts()

        return Frequencies(
            field='travel_time',
            total=len(df),
            data=[
                Frequency(
                    value=travel_time,
                    count=count
                )
                for travel_time, count in travel_time_counts.items()
            ]
        )

    def compute_recommendation_frequencies(self, df: pd.DataFrame) -> Frequencies:
        """Compute recommendation frequencies from a DataFrame of records."""
        reco_series = df['typo.reco.reco_dt2.0'].dropna()
        reco_counts = reco_series.value_counts()

        return Frequencies(
            field='reco_dt2',
            total=len(df),
            data=[
                Frequency(
                    value=reco,
                    count=count
                )
                for reco, count in reco_counts.items()
            ]
        )

    def compute_mod_frequencies_v1(self, df: pd.DataFrame, mod: str) -> Frequencies:
        """Compute a mode frequency from a DataFrame of records."""
        # Legacy data version: get the series for the specific mode

        # Find the column name for the mode
        col_name = f'data.freq_mod_{mod}'
        if col_name not in df.columns:
            return Frequencies(field=mod, total=len(df), data=[])
        # Get the series for the specific mode
        mod_series = df[f'data.freq_mod_{mod}'].dropna().astype(int)
        mod_counts = mod_series.value_counts()
        mod_sums = mod_series.groupby(mod_series).sum()

        return Frequencies(
            field=mod,
            total=len(df),
            data=[
                Frequency(
                    value=str(mod_value),
                    count=mod_counts[mod_value],
                    sum=mod_sums[mod_value]
                )
                for mod_value in mod_counts.index if mod_value > 0
            ]
        )

    def compute_mod_frequencies_v2(self, df: pd.DataFrame, mod: str) -> Frequencies:
        """Compute a mode frequency from a DataFrame of records."""

        def is_intermodal(row, mod, i):
            modes = []
            for col in row.index:
                if col.startswith(f'data.freq_mod_journeys.{i}.modes.'):
                    val = row[col]
                    # walking is not considered for intermodality
                    if not pd.isna(val) and val != 'walking':
                        modes.append(val)
            modes = set(modes)
            return len(modes) > 1

        def extract_mod_days(row, mod, i):
            modes = []
            for col in row.index:
                if col.startswith(f'data.freq_mod_journeys.{i}.modes.'):
                    val = row[col]
                    if not pd.isna(val) and val == mod:
                        modes.append(val)
            modes = set(modes)
            if len(modes) == 0:
                return 0
            if len(modes) > 1:
                # intermodality, make sure walking is not counted
                if 'walking' in modes:
                    modes.remove('walking')
            # get days value
            days_col = f'data.freq_mod_journeys.{i}.days'
            days = row[days_col]
            if mod in modes:
                return int(days) if not pd.isna(days) else 0
            return 0

        # New data version: get the series from data.freq_mod_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]
        # print(
        #     f"Computing mod frequencies for version 2.x using columns: {col_days.tolist()}")
        frequencies = []
        for i in range(len(col_days)):
            # print("mod:", mod, " i:", i)
            col_modes_i = df.columns[df.columns.str.startswith(
                f'data.freq_mod_journeys.{str(i)}.modes.')]
            if col_modes_i.empty:
                continue
            col_days_i = col_days[i]
            # make a dataframe with only i columns
            df_i = df[[col_days_i] + col_modes_i.tolist()].copy()
            # intermodality if more than one mode
            # TODO not used for now
            df_i['inter'] = df_i.apply(
                lambda row: is_intermodal(row, mod, i), axis=1)
            # extract mod days
            df_i['mod_days'] = df_i.apply(
                lambda row: extract_mod_days(row, mod, i), axis=1)
            # count positive mod_days
            df_i = df_i[df_i['mod_days'] > 0]
            for row in df_i.itertuples():
                days = row.mod_days
                count = 1
                # find in frequencies the one with value is str(days)
                freq = next(
                    (f for f in frequencies if f.value == str(days)), None)
                if freq is None:
                    frequencies.append(
                        Frequency(
                            value=str(days),
                            count=int(count),
                            sum=int(days)
                        )
                    )
                else:
                    freq.count += int(count)
                    freq.sum += int(days)
            # print(df_i)

        # print("Final frequencies for mod", mod, ":", frequencies)
        return Frequencies(
            field=mod,
            total=len(df),
            data=frequencies
        )

    def compute_mods_frequencies(self, df: pd.DataFrame) -> list[Frequencies]:
        """Compute all modes frequencies from a DataFrame of records."""
        mods = [
            'walking',
            'bike',
            'ebike',
            'pub',
            'moto',
            'carpool',
            'car',
            'train'
        ]
        # TODO handle intermodality

        # v1 is where data.version is na
        df_v1 = df[df['data.version'].isna()]
        results = []
        for mod in mods:
            results.append(self.compute_mod_frequencies_v1(df_v1, mod))

        # if data.version starts with '2.' count frequencies from data.freq_mod_journeys
        df_v2 = df[df['data.version'].notna(
        ) & df['data.version'].str.startswith('2.')]
        results_v2 = []
        if not df_v2.empty:
            for mod in mods:
                results_v2 = self.compute_mod_frequencies_v2(df_v2, mod)
                results = self.merge_frequencies(results, results_v2)

        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(df)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))

        return results

    def compute_mods_emissions(self, df: pd.DataFrame) -> list[Emissions]:
        """Compute all modes CO2 emissions from a DataFrame of records."""
        mods = [
            'walking',
            'bike',
            'ebike',
            'pub',
            'moto',
            'carpool',
            'car',
            'train'
        ]
        results = []
        for mod in mods:
            emissions = self.get_mod_co2_emissions(mod, df)
            results.append(emissions)
        return results

    async def compute_stats(self, filter: dict) -> Stats:
        """Compute all statistics for equipments, constraints, travel_time, and recommendations."""
        df = await self.get_dataframe(filter, flat=True)
        df = self.filter_completed_records(df)
        equipments = self.compute_equipments_frequencies(df)
        constraints = self.compute_constraints_frequencies(df)
        travel_time = self.compute_travel_time_frequencies(df)
        recommendations = self.compute_recommendation_frequencies(df)
        freq_mods = self.compute_mods_frequencies(df)
        # emissions = self.compute_mods_emissions(df)

        return Stats(
            total=len(df),
            frequencies=[
                equipments,
                constraints,
                travel_time,
                recommendations
            ],
            freq_mods=freq_mods,
            # emissions=emissions
        )

    def merge_frequencies(self, frequencies: list[Frequencies], freq2: Frequencies) -> Frequencies:
        """Merge Frequencies into a list of Frequencies."""
        freq1 = next((f for f in frequencies if f.field == freq2.field), None)
        if not freq1:
            frequencies.append(freq2)
            return frequencies
        merged_data = freq1.data.copy()
        for freq in freq2.data:
            existing_freq = next(
                (f for f in merged_data if f.value == freq.value), None)
            if existing_freq:
                existing_freq.count += freq.count
                if freq.sum is not None:
                    if existing_freq.sum is None:
                        existing_freq.sum = 0
                    existing_freq.sum += freq.sum
            else:
                merged_data.append(freq)
        freq = Frequencies(
            field=freq1.field,
            total=freq1.total + freq2.total,
            data=merged_data
        )
        # replace in frequencies
        for i in range(len(frequencies)):
            if frequencies[i].field == freq.field:
                frequencies[i] = freq
                break
        return frequencies

    def filter_completed_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get a DataFrame representation of the completed records.

        Args:
            filter (dict): The filter criteria for the records.
            flat (bool, optional): Whether to flatten the DataFrame. Defaults to False.
        """
        # Filter records with values in column typo.reco_dt2.0
        df = df[df['typo.reco.reco_dt2.0'].notna()]
        return df

    async def get_dataframe(self, filter: dict, flat: bool = False) -> pd.DataFrame:
        """Get a DataFrame representation of the records.

        Args:
            filter (dict): The filter criteria for the records.
            flat (bool, optional): Whether to flatten the DataFrame. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame representation of the records.
        """
        # Implement your test logic here
        results = await self.find(filter, fields=[], sort=[], range=[])
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

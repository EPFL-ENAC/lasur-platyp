import pandas as pd
import h3
from api.models.query import Link, Stats, Links, Frequencies, Frequency, Emissions

MODE_EMISSIONS = {
    'walking': 0,
    'bike': 6,
    'ebike': 11,
    'pub': 25,
    'moto': 155,
    'carpool': 93,
    'car': 186,
    'train': 8,
}

MODES = [
    'walking',
    'bike',
    'ebike',
    'pub',
    'moto',
    'carpool',
    'car',
    'train'
]

MODES_PRO_V1 = [
    'local_walking',
    'local_car',
    'local_pub',
    'local_bike',
    'local_moto',
    'local_train',
    'region_car',
    'region_pub',
    'region_train',
    'region_moto',
    'region_plane',
    'europe_car',
    'europe_train',
    'europe_plane',
    'inter_car',
    'inter_train',
    'inter_plane'
]

MODES_PRO = [
    'walking',
    'bike',
    'pub',
    'moto',
    'car',
    'train',
    'boat',
    'plane',
]


class StatsService:

    def compute_stats(self, df: pd.DataFrame) -> Stats:
        """Compute all statistics for equipments, constraints, travel_time, and recommendations."""
        df = self._preprocess_dataframe(df)
        equipments = self.compute_equipments_frequencies(df)
        constraints = self.compute_constraints_frequencies(df)
        travel_time = self.compute_travel_time_frequencies(df)
        recommendations = self.compute_recommendation_frequencies(df)
        mode_frequencies = self.compute_modes_frequencies(df)
        mode_emissions = self.compute_modes_emissions(df)
        mode_links = self.compute_mode_reco_links(df)
        mode_pro_frequencies = self.compute_modes_pro_frequencies(df)

        return Stats(
            total=len(df),
            frequencies=[
                equipments,
                constraints,
                travel_time,
                recommendations
            ],
            mode_frequencies=mode_frequencies,
            mode_emissions=mode_emissions,
            mode_links=mode_links,
            mode_pro_frequencies=mode_pro_frequencies
        )

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

    def compute_modes_frequencies(self, df: pd.DataFrame) -> list[Frequencies]:
        """Compute all modes frequencies from a DataFrame of records."""
        # TODO handle intermodality

        # v1: count frequencies from legacy fields
        df_v1 = self._get_records_v1(df)
        results = []
        for mode in MODES:
            results.append(self._compute_mode_frequencies_v1(df_v1, mode))

        # v2: count frequencies from data.freq_mod_journeys
        df_v2 = self._get_records_v2(df)
        if not df_v2.empty:
            results_v2 = []
            for mode in MODES:
                results_v2.append(
                    self._compute_mode_frequencies_v2(df_v2, mode))
            results = self._merge_frequencies(results, results_v2)

        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(df)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))

        return results

    def compute_modes_emissions(self, df: pd.DataFrame) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records."""

        def calculate_distance_home_to_work(row):
            origin_lat = float(row['data.origin.lat'])
            origin_lon = float(row['data.origin.lon'])
            work_lat = float(row['data.workplace.lat'])
            work_lon = float(row['data.workplace.lon'])
            return self._calculate_distance(origin_lat, origin_lon, work_lat, work_lon)

        # Calculate distance_km to workplace for each record
        df['distance_km'] = df.apply(
            lambda row: calculate_distance_home_to_work(row), axis=1)

        # v1: count emissions from legacy fields
        df_v1 = self._get_records_v1(df)
        results = []
        for mode in MODES:
            results.append(self._compute_mode_emissions_v1(df_v1, mode))

        # v2: count emissions from data.freq_mod_journeys
        df_v2 = self._get_records_v2(df)
        if not df_v2.empty:
            results_v2 = []
            for mode in MODES:
                results_v2.append(self._compute_mode_emissions_v2(df_v2, mode))
            # merge v1 and v2 results
            for em_v2 in results_v2:
                # find in results the one with same field
                em_v1 = next(
                    (e for e in results if e.field == em_v2.field), None)
                if em_v1 is None:
                    results.append(em_v2)
                else:
                    em_v1.total += em_v2.total
                    em_v1.distances += em_v2.distances
                    em_v1.journeys += em_v2.journeys
                    em_v1.emissions += em_v2.emissions

        # finalize totals
        for emission in results:
            emission.total = len(df)
            # round distances, emissions
            emission.distances = round(emission.distances, 3)
            emission.emissions = round(emission.emissions, 3)

        return results

    def compute_modes_pro_frequencies(self, df: pd.DataFrame) -> list[Frequencies]:
        """Compute all modes frequencies from a DataFrame of records."""
        # v1: count frequencies from legacy fields
        df_v1 = self._get_records_v1(df)
        results = []
        for mode in MODES_PRO_V1:
            results.append(self._compute_mode_pro_frequencies_v1(df_v1, mode))

         # v2: count frequencies from data.freq_mod_journeys
        df_v2 = self._get_records_v2(df)
        if not df_v2.empty:
            results_v2 = []
            for mode in MODES_PRO:
                results_v2.extend(
                    self._compute_mode_pro_frequencies_v2(df_v2, mode))
            results = self._merge_frequencies(results, results_v2)
        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(df)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))
        # filter out frequencies with empty data
        results = [f for f in results if len(f.data) > 0]

        return results

    def compute_mode_reco_links(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""
        # v1: legacy data version
        df_v1 = self._get_records_v1(df)
        links = self._compute_mode_reco_links_v1(df_v1)

        # v2: new data version
        df_v2 = self._get_records_v2(df)
        if not df_v2.empty:
            links_v2 = self._compute_mode_reco_links_v2(df_v2)
            # merge links of same source and target
            merged_links = {}
            for link in links.data + links_v2.data:
                key = (link.source, link.target)
                if key in merged_links:
                    merged_links[key].value += link.value
                else:
                    merged_links[key] = Link(
                        source=link.source, target=link.target, value=link.value)
            links.data = list(merged_links.values())
            links.total = len(df)

        return links

    #
    # Internal functions
    #

    def _compute_mode_pro_frequencies_v1(self, df: pd.DataFrame, mode: str) -> Frequencies:
        """Compute a mode frequency from a DataFrame of records."""
        # Legacy data version: get the series for the specific mode

        # Find the column name for the mode
        col_name = f'data.freq_mod_pro_{mode}'
        if col_name not in df.columns:
            return Frequencies(field=mode, total=len(df), data=[])
        # Get the series for the specific mode
        mode_series = df[f'data.freq_mod_pro_{mode}'].dropna().astype(int)
        mode_counts = mode_series.value_counts()
        mode_sums = mode_series.groupby(mode_series).sum()

        return Frequencies(
            field=mode.replace('region_', 'national_'),
            total=len(df),
            data=[
                Frequency(
                    value=str(mod_value),
                    count=mode_counts[mod_value],
                    sum=mode_sums[mod_value]
                )
                for mod_value in mode_counts.index if mod_value > 0
            ]
        )

    def _compute_mode_pro_frequencies_v2(self, df: pd.DataFrame, mode: str) -> list[Frequencies]:
        """Compute a mode frequency from a DataFrame of records."""

        def calculate_distance_type(row, i):
            lat = float(row['data.workplace.lat'])
            lon = float(row['data.workplace.lon'])
            h3_index = row[f'data.freq_mod_pro_journeys.{str(i)}.hex_id']
            mode = row[f'data.freq_mod_pro_journeys.{str(i)}.mode']
            dist = self._calculate_distance_to_h3(lat, lon, h3_index, mode)
            if dist < 20:
                return 'local'
            elif dist < 500:
                return 'national'
            elif dist < 1500:
                return 'europe'
            else:
                return 'inter'

        # New data version: get the series from data.freq_mod_pro_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_pro_journeys\..*\.days$', regex=True)]
        # print(
        #     f"Computing mod frequencies for version 2.x using columns: {col_days.tolist()}")
        field_frequencies = {}
        for i in range(len(col_days)):
            # print("mode:", mode, "journey:", i)
            col_mode_i = f'data.freq_mod_pro_journeys.{str(i)}.mode'
            col_hexid_i = f'data.freq_mod_pro_journeys.{str(i)}.hex_id'
            col_days_i = col_days[i]
            # make a dataframe with only i columns and workplace lat/lon
            df_i = df[['data.workplace.lat', 'data.workplace.lon',
                       col_days_i, col_mode_i, col_hexid_i]].copy()
            # Calculate distance type from workplace to pro travel destination for each record
            df_i['type'] = df_i.apply(
                lambda row: calculate_distance_type(row, i), axis=1)
            # print(df_i)
            # count positive mod_days
            df_i = df_i[df_i[col_days_i] > 0]
            for idx, row in df_i.iterrows():
                days = int(row[col_days_i])
                type = row['type']
                field = f"{type}_{mode}"
                if field not in field_frequencies:
                    field_frequencies[field] = Frequencies(
                        field=field,
                        total=len(df),
                        data=[]
                    )
                frequencies = field_frequencies[field].data
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

        return list(field_frequencies.values())

    def _compute_mode_frequencies_v1(self, df: pd.DataFrame, mode: str) -> Frequencies:
        """Compute a mode frequency from a DataFrame of records."""
        # Legacy data version: get the series for the specific mode

        # Find the column name for the mode
        col_name = f'data.freq_mod_{mode}'
        if col_name not in df.columns:
            return Frequencies(field=mode, total=len(df), data=[])
        # Get the series for the specific mode
        mode_series = df[f'data.freq_mod_{mode}'].dropna().astype(int)
        mode_counts = mode_series.value_counts()
        mode_sums = mode_series.groupby(mode_series).sum()

        return Frequencies(
            field=mode,
            total=len(df),
            data=[
                Frequency(
                    value=str(mod_value),
                    count=mode_counts[mod_value],
                    sum=mode_sums[mod_value]
                )
                for mod_value in mode_counts.index if mod_value > 0
            ]
        )

    def _compute_mode_frequencies_v2(self, df: pd.DataFrame, mode: str) -> Frequencies:
        """Compute a mode frequency from a DataFrame of records."""

        def is_intermodal(row, i):
            modes = []
            for col in row.index:
                if col.startswith(f'data.freq_mod_journeys.{i}.modes.'):
                    val = row[col]
                    # walking is not considered for intermodality
                    if not pd.isna(val) and val != 'walking':
                        modes.append(val)
            modes = set(modes)
            return len(modes) > 1

        def extract_mod_days(row, mode, i):
            modes = []
            for col in row.index:
                if col.startswith(f'data.freq_mod_journeys.{i}.modes.'):
                    val = row[col]
                    if not pd.isna(val) and val == mode:
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
            if mode in modes:
                return int(days) if not pd.isna(days) else 0
            return 0

        # New data version: get the series from data.freq_mod_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]
        # print(
        #     f"Computing mod frequencies for version 2.x using columns: {col_days.tolist()}")
        frequencies = []
        for i in range(len(col_days)):
            # print("mode:", mode, "journey:", i)
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
                lambda row: is_intermodal(row, i), axis=1)
            # extract mod days
            df_i['mod_days'] = df_i.apply(
                lambda row: extract_mod_days(row, mode, i), axis=1)
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

        # print("Final frequencies for mode", mode, ":", frequencies)
        return Frequencies(
            field=mode,
            total=len(df),
            data=frequencies
        )

    def _compute_mode_emissions_v1(self, df: pd.DataFrame, mode: str) -> Emissions:
        """Compute all CO2 emissions from a DataFrame of records."""
        emissions = Emissions(
            field=mode, total=len(df), distances=0, journeys=0, emissions=0)
        # Find the column name for the mode
        col_name = f'data.freq_mod_{mode}'
        if col_name not in df.columns:
            return emissions

        # Subset the dataframe for the specific mode, filtered by colname not na
        df_mode = df[df[col_name].notna()]
        if len(df_mode) == 0:
            return emissions
        emissions.distances = float(df_mode['distance_km'].sum())
        emissions.journeys = int(df_mode[col_name].sum() * 45 * 2)
        emissions.emissions = float(sum(
            df_mode['distance_km'] * df_mode[col_name] * 45 * 2 * MODE_EMISSIONS[mode] / 1000))
        return emissions

    def _compute_mode_emissions_v2(self, df: pd.DataFrame, mode: str) -> Emissions:
        """Compute all CO2 emissions from a DataFrame of records."""
        def compute_mode_emissions(row, mode, i):
            modes = []
            for col in row.index:
                if col.startswith(f'data.freq_mod_journeys.{i}.modes.'):
                    val = row[col]
                    if not pd.isna(val):
                        modes.append(val)
            modes = set(modes)

            # if the train is one of the modes, consider that 80% of the distance is done by train,
            # then split the rest equally among the other modes used.
            co2 = 0
            if 'train' in modes:
                if mode == 'train':
                    co2 += 0.8 * 45 * 2 * (row[f'data.freq_mod_journeys.{i}.days'] *
                                           row['distance_km'] *
                                           MODE_EMISSIONS['train'] / 1000)
                elif mode in modes:
                    co2 += 0.2 / (len(modes) - 1) * 45 * 2 * (row[f'data.freq_mod_journeys.{i}.days'] *
                                                              row['distance_km'] *
                                                              MODE_EMISSIONS[mode] / 1000)
            elif mode in modes:
                co2 += 1 / len(modes) * 45 * 2 * (row[f'data.freq_mod_journeys.{i}.days'] *
                                                  row['distance_km'] *
                                                  MODE_EMISSIONS[mode] / 1000)
            em_factor = co2 * 1000 / \
                (45 * 2 *
                 (row[f'data.freq_mod_journeys.{i}.days'] * row['distance_km']))
            return [co2, em_factor]

        # New data version: get the series from data.freq_mod_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]
        emissions = Emissions(
            field=mode,
            total=len(df),
            distances=0,
            journeys=0,
            emissions=0
        )
        for i in range(len(col_days)):
            # print("journey:", i)
            col_modes_i = df.columns[df.columns.str.startswith(
                f'data.freq_mod_journeys.{str(i)}.modes.')]
            if col_modes_i.empty:
                continue
            col_days_i = col_days[i]
            # make a dataframe with only i columns
            df_i = df[['distance_km', col_days_i] +
                      col_modes_i.tolist()].copy()
            # compute emissions factor
            df_i[['mode_emissions', 'em_factor']] = df_i.apply(
                lambda row: compute_mode_emissions(row, mode, i), axis=1, result_type='expand')
            # filter only positive emissions
            df_i = df_i[df_i['mode_emissions'] > 0]
            # print(df_i)
            emissions.distances += float(sum(
                df_i['distance_km'] * df_i[col_days_i] * 45 * 2))
            emissions.journeys += int(sum(
                df_i[col_days_i] * 45 * 2))
            emissions.emissions += float(sum(df_i['mode_emissions']))

        return emissions

    def _compute_mode_reco_links_v1(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""
        counts = {}
        for mode in MODES:
            col_name = f'data.freq_mod_{mode}'
            if col_name not in df.columns:
                continue
            df_mode = df[df[col_name].notna()]
            for _, row in df_mode.iterrows():
                reco = row['typo.reco.reco_dt2.0']
                mod_count = int(row[col_name])
                if mod_count <= 0:
                    continue
                mod_counts = counts.get(mode, {})
                mod_counts[reco] = mod_counts.get(reco, 0) + 1
                counts[mode] = mod_counts
        links = [Link(source=mod, target=reco, value=int(count)) for mod,
                 reco_counts in counts.items() for reco, count in reco_counts.items()]
        return Links(total=len(df), data=links)

    def _compute_mode_reco_links_v2(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""

        # New data version: get the series from data.freq_mod_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]
        counts = {}
        for i in range(len(col_days)):
            col_modes_i = df.columns[df.columns.str.startswith(
                f'data.freq_mod_journeys.{str(i)}.modes.')]
            if col_modes_i.empty:
                continue
            col_days_i = col_days[i]
            # make a dataframe with only i columns
            df_i = df[[col_days_i] + col_modes_i.tolist() +
                      ['typo.reco.reco_dt2.0']].copy()
            # iterate rows
            for _, row in df_i.iterrows():
                days = row[col_days_i]
                if pd.isna(days) or int(days) <= 0:
                    continue
                for col in col_modes_i:
                    mode = row[col]
                    if pd.isna(mode):
                        continue
                    reco = row['typo.reco.reco_dt2.0']
                    mod_counts = counts.get(mode, {})
                    mod_counts[reco] = mod_counts.get(reco, 0) + 1
                    counts[mode] = mod_counts
        data = [Link(source=mod, target=reco, value=int(count)) for mod,
                reco_counts in counts.items() for reco, count in reco_counts.items()]
        links = Links(total=len(df), data=data)
        return links

    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the DataFrame before computing statistics."""
        # Filter only completed records
        df = self._filter_completed_records(df).copy()
        return df

    def _get_records_v1(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get records with data.version as NaN"""
        if 'data.version' not in df.columns:
            return df.copy()
        df_v1 = df[df['data.version'].isna()].copy()
        return df_v1

    def _get_records_v2(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get records with data.version starting with '2.'"""
        if 'data.version' not in df.columns:
            return pd.DataFrame()
        df_v2 = df[df['data.version'].notna(
        ) & df['data.version'].str.startswith('2.')].copy()
        return df_v2

    def _calculate_distance(self, origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> float:
        """Calculate the distance between origin and destination locations."""
        try:
            from math import radians, cos, sin, acos
            distance_km = 6371 * acos(
                cos(radians(origin_lat)) *
                cos(radians(dest_lat)) *
                cos(radians(dest_lon) - radians(origin_lon)) +
                sin(radians(origin_lat)) *
                sin(radians(dest_lat))
            )
            return distance_km * 1.3  # factor for real distance
        except:
            return 0

    def _calculate_distance_to_h3(self, lat: float, lon: float, h3_index: str, mode: str) -> float:
        """Calculate the distance between workplace and destination with a transport mode."""
        try:
            if pd.isna(h3_index):
                return 0
            # Hypothèse sur l'allongement des distances : en moyenne, 1.22 (network based vs real measured distances : https://journals.sagepub.com/doi/abs/10.3141/1804-28)
            # On pourrait améliorer ca en cherchant la meme chose pour l'avion (études sur les détours/distances faites lorsqu'on doit attendre au dessus d'un aéroport plein...)
            # Pareil pour le bateau (pour l'instant on applique 1.22 à tous)
            avg_dist_coeff = {'train': 1.22, 'car': 1.22, 'bike': 1.22,
                              'walk': 1.22, 'moto': 1.22, 'pub': 1.22, 'boat': 1.22, 'plane': 1.22}
            if h3.latlng_to_cell(lat, lon, h3.get_resolution(h3_index)) == h3_index:
                # Si meme hexagone (apres mise à la resolution choisie par l'utilisateur), on prend une distance moyenne de la taille d'une arrête de l'hexagone.
                return h3.average_hexagon_edge_length(h3.get_resolution(h3_index))
            else:
                # Si pas meme hexagone, on convertit le centre du h3 sélectionné en h3 plus petit pour calculer des distances plus précises
                return h3.great_circle_distance(h3.cell_to_latlng(h3.cell_to_center_child(h3_index, 9)),
                                                (lat, lon)) * avg_dist_coeff[mode]
        except:
            return 0

    def _merge_frequencies(self, frequencies: list[Frequencies], frequencies2: list[Frequencies]) -> Frequencies:
        """Merge each Frequencies into a list of Frequencies."""
        for freq2 in frequencies2:
            freq1 = next(
                (f for f in frequencies if f.field == freq2.field), None)
            if not freq1:
                frequencies.append(freq2)
                continue
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

    def _filter_completed_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get a DataFrame representation of the completed records.

        Args:
            filter (dict): The filter criteria for the records.
            flat (bool, optional): Whether to flatten the DataFrame. Defaults to False.
        """
        # Filter records with values in column typo.reco_dt2.0
        df = df[df['typo.reco.reco_dt2.0'].notna()]
        return df

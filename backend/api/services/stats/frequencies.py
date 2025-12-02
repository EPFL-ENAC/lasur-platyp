import pandas as pd
from api.models.query import Frequencies, Frequency
from api.services.stats.commons import BaseStatsService, MODES, MODES_PRO, MODES_PRO_V1


class FrequenciesService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_equipments_frequencies(self) -> Frequencies:
        """Compute equipments frequencies from a DataFrame of records."""
        # Find columns starting with 'data.equipments.'
        equipments_cols = [
            col for col in self.df.columns if col.startswith('data.equipments.')]
        # Each column contains the name of an equipment if present, else NaN
        all_equipments = []
        for col in equipments_cols:
            all_equipments.extend(
                self.df[col].dropna().tolist()
            )
        equipment_counts = pd.Series(all_equipments).value_counts()

        return Frequencies(
            field='equipments',
            total=len(self.df),
            data=[
                Frequency(
                    value=equipment,
                    count=count
                )
                for equipment, count in equipment_counts.items()
            ]
        )

    def compute_constraints_frequencies(self) -> Frequencies:
        """Compute constraints frequencies from a DataFrame of records."""
        # Find columns starting with 'data.constraints.'
        constraints_cols = [
            col for col in self.df.columns if col.startswith('data.constraints.')]
        # Each column contains the name of a constraint if present, else NaN
        all_constraints = []
        for col in constraints_cols:
            all_constraints.extend(
                self.df[col].dropna().tolist()
            )
        constraint_counts = pd.Series(all_constraints).value_counts()

        return Frequencies(
            field='constraints',
            total=len(self.df),
            data=[
                Frequency(
                    value=constraint,
                    count=count
                )
                for constraint, count in constraint_counts.items()
            ]
        )

    def compute_travel_time_frequencies(self) -> Frequencies:
        """Compute travel time frequencies from a DataFrame of records."""
        travel_time_series = self.df['data.travel_time'].dropna().astype(str)
        travel_time_counts = travel_time_series.value_counts()

        return Frequencies(
            field='travel_time',
            total=len(self.df),
            data=[
                Frequency(
                    value=travel_time,
                    count=count
                )
                for travel_time, count in travel_time_counts.items()
            ]
        )

    def compute_recommendation_frequencies(self) -> Frequencies:
        """Compute recommendation frequencies from a DataFrame of records."""
        reco_series = self.df['typo.reco.reco_dt2.0'].dropna()
        reco_counts = reco_series.value_counts()

        return Frequencies(
            field='reco_dt2',
            total=len(self.df),
            data=[
                Frequency(
                    value=reco,
                    count=count
                )
                for reco, count in reco_counts.items()
            ]
        )

    def compute_recommendation_pro_frequencies(self) -> Frequencies:
        """Compute recommendation professional frequencies from a DataFrame of records."""
        all_reco_pros = []
        # v1: recommendations are made per destination area type
        for col in ['typo.reco_pro.reco_pro_loc', 'typo.reco_pro.reco_pro_reg', 'typo.reco_pro.reco_pro_inter']:
            if col in self.df.columns:
                all_reco_pros.extend(
                    self.df[col].dropna().tolist()
                )

        # v2: recommendations are made per journey
        col_reco_pros = self.df.columns[self.df.columns.str.contains(
            r'^typo\.reco_pro\.reco_pros\..*$', regex=True)]
        for col in col_reco_pros:
            all_reco_pros.extend(
                self.df[col].dropna().tolist()
            )
        reco_counts = pd.Series(all_reco_pros).value_counts()

        return Frequencies(
            field='reco_pros',
            total=len(self.df),
            data=[
                Frequency(
                    value=reco,
                    count=count
                )
                for reco, count in reco_counts.items() if reco
            ]
        )

    def compute_modes_frequencies(self) -> list[Frequencies]:
        """Compute all modes frequencies from a DataFrame of records."""
        # TODO handle intermodality

        # v1: count frequencies from legacy fields
        df_v1 = self._get_records_v1()
        results = []
        for mode in MODES:
            results.append(self._compute_mode_frequencies_v1(df_v1, mode))

        # v2: count frequencies from data.freq_mod_journeys
        df_v2 = self._get_records_v2()
        if not df_v2.empty:
            results_v2 = []
            for mode in MODES:
                results_v2.append(
                    self._compute_mode_frequencies_v2(df_v2, mode))
            results = self._merge_frequencies(results, results_v2)

        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(self.df)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))

        return results

    def compute_modes_pro_frequencies(self) -> list[Frequencies]:
        """Compute all modes frequencies from a DataFrame of records."""
        # v1: count frequencies from legacy fields
        df_v1 = self._get_records_v1()
        results = []
        for mode in MODES_PRO_V1:
            results.append(self._compute_mode_pro_frequencies_v1(df_v1, mode))

         # v2: count frequencies from data.freq_mod_journeys
        df_v2 = self._get_records_v2()
        if not df_v2.empty:
            results_v2 = []
            for mode in MODES_PRO:
                results_v2.extend(
                    self._compute_mode_pro_frequencies_v2(df_v2, mode))
            results = self._merge_frequencies(results, results_v2)
        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(self.df)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))
        # filter out frequencies with empty data
        results = [f for f in results if len(f.data) > 0]

        return results

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
        # days per month to days per year
        mode_series = mode_series * 12
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
            if col_mode_i not in df.columns:
                continue
            col_hexid_i = f'data.freq_mod_pro_journeys.{str(i)}.hex_id'
            if col_hexid_i not in df.columns:
                continue
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

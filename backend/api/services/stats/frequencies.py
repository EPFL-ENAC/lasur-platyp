import re
import pandas as pd
from api.models.query import Frequencies, Frequency
from api.services.stats.commons import BaseStatsService, MODES_PRO, DAYS_PER_YEAR_FACTOR, normalize_pro_days_to_yearly


class FrequenciesService(BaseStatsService):
    # Pre-compiled regex patterns for performance
    RECO_PROS_PATTERN = re.compile(r"^typo\.reco_pro\.reco_pros\..*$")
    JOURNEY_DAYS_PATTERN = re.compile(r"^data\.freq_mod_journeys\..*\.days$")
    PRO_JOURNEY_DAYS_PATTERN = re.compile(
        r"^data\.freq_mod_pro_journeys\..*\.days$")
    JOURNEY_MODES_PATTERN = re.compile(
        r"^data\.freq_mod_journeys\.(\d+)\.modes\..*$")
    SIMPLE_LABEL_PATTERN = re.compile(r"^typo\.reco\.simple_labels\.\d+$")
    COMPLEX_LABEL_PATTERN = re.compile(r"^typo\.reco\.complex_labels\.\d+$")

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_equipments_frequencies(self) -> Frequencies:
        """Compute equipments frequencies from a DataFrame of records."""
        # Find columns starting with 'data.equipments.'
        equipments_cols = [
            col for col in self.df.columns if col.startswith("data.equipments.")
        ]
        # Each column contains the name of an equipment if present, else NaN
        all_equipments = []
        for col in equipments_cols:
            all_equipments.extend(self.df[col].dropna().tolist())
        equipment_counts = pd.Series(all_equipments).value_counts()

        return Frequencies(
            field="equipments",
            total=len(self.df),
            data=[
                Frequency(value=equipment, count=count)
                for equipment, count in equipment_counts.items()
            ],
        )

    def compute_constraints_frequencies(self) -> Frequencies:
        """Compute constraints frequencies from a DataFrame of records."""
        # Find columns starting with 'data.constraints.'
        constraints_cols = [
            col for col in self.df.columns if col.startswith("data.constraints.")
        ]
        # Each column contains the name of a constraint if present, else NaN
        all_constraints = []
        for col in constraints_cols:
            all_constraints.extend(self.df[col].dropna().tolist())
        constraint_counts = pd.Series(all_constraints).value_counts()

        return Frequencies(
            field="constraints",
            total=len(self.df),
            data=[
                Frequency(value=constraint, count=count)
                for constraint, count in constraint_counts.items()
            ],
        )

    def compute_travel_time_frequencies(self) -> Frequencies:
        """Compute travel time frequencies from a DataFrame of records."""
        if "data.travel_time" not in self.df.columns:
            return Frequencies(field="travel_time", total=len(self.df), data=[])

        travel_time_series = self.df["data.travel_time"].dropna().astype(str)
        travel_time_counts = travel_time_series.value_counts()

        return Frequencies(
            field="travel_time",
            total=len(self.df),
            data=[
                Frequency(value=travel_time, count=count)
                for travel_time, count in travel_time_counts.items()
            ],
        )

    def compute_recommendation_frequencies(self) -> Frequencies:
        """Compute recommendation frequencies from a DataFrame of records.

        Each recommendation is taken into account (one per journey for new-style
        typo.reco.reco_inter.N records, one per legacy typo.reco.reco_dt2.{0,1} for
        older records), weighted by the days of the journey(s) it applies to.
        """
        reco_df = self._build_reco_weighted(self.df)
        if reco_df is None:
            return Frequencies(field="reco_inter", total=len(self.df), data=[])

        grouped = reco_df.groupby("reco_mode")["days"]

        return Frequencies(
            field="reco_inter",
            total=len(self.df),
            data=[
                Frequency(value=reco, count=int(
                    counts.count()), sum=int(counts.sum()))
                for reco, counts in grouped
            ],
        )

    def compute_recommendation_pro_frequencies(self) -> Frequencies:
        """Compute recommendation professional frequencies from a DataFrame of records."""
        if self.df.empty:
            return Frequencies(field="reco_pros", total=0, data=[])

        all_reco_pros = []
        # recommendations are made per journey
        col_reco_pros = [
            col for col in self.df.columns if self.RECO_PROS_PATTERN.match(col)
        ]
        for col in col_reco_pros:
            all_reco_pros.extend(self.df[col].dropna().tolist())
        reco_counts = pd.Series(all_reco_pros).value_counts()

        return Frequencies(
            field="reco_pros",
            total=len(self.df),
            data=[
                Frequency(value=reco, count=count)
                for reco, count in reco_counts.items()
                if reco
            ],
        )

    def compute_modes_pro_frequencies(self) -> list[Frequencies]:
        """Compute all modes frequencies from a DataFrame of records (v3 only)."""
        df_v3 = self._get_records_v3()
        if df_v3.empty:
            return []

        results = []
        for mode in MODES_PRO:
            results.extend(self._compute_mode_pro_frequencies_v3(df_v3, mode))

        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(df_v3)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))
        # filter out frequencies with empty data
        results = [f for f in results if len(f.data) > 0]

        return results

    def compute_modes_frequencies_simple_labels(self) -> list[Frequencies]:
        """Compute mode frequencies from typo.reco.simple_labels, one Frequencies
        per label actually observed in the data (rather than a fixed mode list)."""
        df_v3 = self._get_records_v3()
        if df_v3.empty:
            return []

        label_cols = [
            col for col in df_v3.columns if self.SIMPLE_LABEL_PATTERN.match(col)
        ]
        if not label_cols:
            return []

        observed_labels = pd.unique(df_v3[label_cols].values.ravel())
        observed_labels = sorted(
            str(label) for label in observed_labels if pd.notna(label)
        )

        results = [
            self._compute_mode_frequencies_simple_labels(df_v3, label)
            for label in observed_labels
        ]

        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(df_v3)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))

        return results

    def compute_modes_frequencies_complex_labels(self) -> list[Frequencies]:
        """Compute mode frequencies from typo.reco.complex_labels, one Frequencies
        per label actually observed in the data (rather than a fixed mode list)."""
        df_v3 = self._get_records_v3()
        if df_v3.empty:
            return []

        label_cols = [
            col for col in df_v3.columns if self.COMPLEX_LABEL_PATTERN.match(col)
        ]
        if not label_cols:
            return []

        observed_labels = pd.unique(df_v3[label_cols].values.ravel())
        observed_labels = sorted(
            str(label) for label in observed_labels if pd.notna(label)
        )

        results = [
            self._compute_mode_frequencies_complex_labels(df_v3, label)
            for label in observed_labels
        ]

        # finalize totals and sort data
        for frequencies in results:
            frequencies.total = len(df_v3)
            # sort frequencies data by value as integer
            frequencies.data.sort(key=lambda x: int(x.value))

        return results

    #
    # Internal functions
    #

    def _distance_type(self, lat: float, lon: float, h3_index, mode: str) -> str:
        dist = self._calculate_distance_to_h3(lat, lon, h3_index, mode)
        if dist < 20:
            return "local"
        elif dist < 500:
            return "national"
        elif dist < 1500:
            return "europe"
        else:
            return "inter"

    def _compute_mode_pro_frequencies_v3(
        self, df: pd.DataFrame, mode: str
    ) -> list[Frequencies]:
        """Compute a mode frequency from a DataFrame of records.

        Builds a days -> (count, sum) histogram per field (distance_type_mode)
        vectorized per journey index -- filtering, day normalization and
        histogram aggregation are vectorized; only the h3 distance-type
        lookup stays a per-row call (h3 has no bulk API), and only over the
        already mode-filtered, positive-days subset rather than the full df.
        """
        col_days = df.columns[
            df.columns.str.contains(
                r"^data\.freq_mod_pro_journeys\..*\.days$", regex=True
            )
        ]
        # field -> {days_str: [count, sum]}
        totals: dict[str, dict[str, list[int]]] = {}
        for i in range(len(col_days)):
            col_mode_i = f"data.freq_mod_pro_journeys.{str(i)}.mode"
            if col_mode_i not in df.columns:
                continue
            col_hexid_i = f"data.freq_mod_pro_journeys.{str(i)}.hex_id"
            if col_hexid_i not in df.columns:
                continue
            col_days_i = col_days[i]
            col_days_per_i = f"data.freq_mod_pro_journeys.{str(i)}.days_per"

            # Coerce before comparing/using: some records have this field
            # stored as a non-numeric string, which would otherwise raise on
            # `> 0` (invalid values are treated as missing, same as skipping
            # them would).
            days_s = pd.to_numeric(df[col_days_i], errors='coerce')
            mask = (df[col_mode_i] == mode) & (days_s > 0)
            if not mask.any():
                continue

            idx = df.index[mask]
            workplace_lat = df["data.workplace.lat"].loc[idx]
            workplace_lon = df["data.workplace.lon"].loc[idx]
            hex_ids = df[col_hexid_i].loc[idx]
            days_per_s = df[col_days_per_i].loc[idx] if col_days_per_i in df.columns else pd.Series(
                None, index=idx)

            # h3 distance-type lookup, per-row over the small filtered subset
            types = pd.Series(
                [self._distance_type(float(lat), float(lon), hex_id, mode)
                 for lat, lon, hex_id in zip(workplace_lat, workplace_lon, hex_ids)],
                index=idx,
            )

            factor = days_per_s.map(DAYS_PER_YEAR_FACTOR).fillna(1)
            days_yearly = (days_s.loc[idx] * factor).astype(int)

            hist = pd.DataFrame({"type": types.to_numpy(), "days": days_yearly.to_numpy()})
            for (type_, days_val), count in hist.groupby(["type", "days"]).size().items():
                field = f"{type_}_{mode}"
                bucket = totals.setdefault(field, {})
                entry = bucket.setdefault(str(days_val), [0, 0])
                entry[0] += int(count)
                entry[1] += int(days_val) * int(count)

        return [
            Frequencies(
                field=field, total=len(df),
                data=[Frequency(value=key, count=count, sum=total_days)
                      for key, (count, total_days) in days_map.items()],
            )
            for field, days_map in totals.items()
        ]

    def _compute_mode_frequencies_by_label(
        self, df: pd.DataFrame, mode: str, label_col_prefix: str
    ) -> Frequencies:
        """Compute a mode frequency from data.freq_mod_journeys, using the
        aggregated typo.reco.{simple,complex}_labels.{i} instead of the raw
        modes.* list, so each journey's days are credited to exactly one
        label. Builds a days -> (count, sum) histogram vectorized per journey
        index instead of a linear-search-per-row Python loop."""
        col_days = [
            col for col in df.columns if self.JOURNEY_DAYS_PATTERN.match(col)]
        totals: dict[str, list[int]] = {}
        for i in range(len(col_days)):
            col_label_i = f"{label_col_prefix}.{str(i)}"
            if col_label_i not in df.columns:
                continue
            col_days_i = col_days[i]
            days_s = pd.to_numeric(df[col_days_i], errors='coerce')
            label_s = df[col_label_i]
            mask = label_s.notna() & (label_s == mode) & (days_s > 0)
            if not mask.any():
                continue
            days_int = days_s[mask].astype(int)
            for days_val, count in days_int.value_counts().items():
                key = str(days_val)
                bucket = totals.setdefault(key, [0, 0])
                bucket[0] += int(count)
                bucket[1] += int(days_val) * int(count)

        frequencies = [
            Frequency(value=key, count=count, sum=total_days)
            for key, (count, total_days) in totals.items()
        ]
        return Frequencies(field=mode, total=len(df), data=frequencies)

    def _compute_mode_frequencies_simple_labels(
        self, df: pd.DataFrame, mode: str
    ) -> Frequencies:
        return self._compute_mode_frequencies_by_label(df, mode, "typo.reco.simple_labels")

    def _compute_mode_frequencies_complex_labels(
        self, df: pd.DataFrame, mode: str
    ) -> Frequencies:
        return self._compute_mode_frequencies_by_label(df, mode, "typo.reco.complex_labels")


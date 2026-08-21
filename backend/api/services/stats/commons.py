import re
import numpy as np
import pandas as pd
import h3


RECOS = [
    'train',
    'tpu',
    'vae',
    'velo',
    'marche',
    'inter',
    'elec',
    'covoit'
]

MODES_PRO = [
    'walking',
    'bike',
    'cargo',
    'pub',
    'moto',
    'truck',
    'car',
    'train',
    'boat',
    'plane',
]

RECOS_PRO = [
    'train',
    'ebike',
    'bike',
    'walking',
    'elec',
    'plane',
    'boat',
    'elec_moto',
    'pub'
]

DAYS_PER_YEAR_FACTOR = {
    'week': 47,  # worked weeks
    'month': 11,  # worked months
    'year': 1,
}


def normalize_pro_days_to_yearly(days: float, days_per) -> float:
    """Convert pro journey days count to an annual equivalent.

    Old records lack days_per (treated as yearly). New records carry
    days_per in {'week', 'month', 'year'}.
    """
    if pd.isna(days_per) or days_per not in DAYS_PER_YEAR_FACTOR:
        return days
    return days * DAYS_PER_YEAR_FACTOR[days_per]


RECO_INTER_PATTERN = re.compile(r'^typo\.reco\.reco_inter\.(\d+)$')
# Legacy general recommendations (not tied to a specific journey), superseded by
# typo.reco.reco_inter but still present on records collected before that change.
RECO_LEGACY_COLUMNS = ['typo.reco.reco_dt2.0', 'typo.reco.reco_dt2.1']


class BaseStatsService:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._v3_cache = None
        self._journey_attributes_cache = {}

    def _reco_inter_columns(self, df: pd.DataFrame) -> list[str]:
        """typo.reco.reco_inter.N columns present in df, sorted by journey index N."""
        cols = [c for c in df.columns if RECO_INTER_PATTERN.match(c)]
        return sorted(cols, key=lambda c: int(RECO_INTER_PATTERN.match(c).group(1)))

    def _reco_legacy_columns(self, df: pd.DataFrame) -> list[str]:
        """typo.reco.reco_dt2.{0,1} columns present in df."""
        return [c for c in RECO_LEGACY_COLUMNS if c in df.columns]

    def _has_completed_recommendation(self, df: pd.DataFrame) -> pd.Series:
        """Boolean mask: whether a row has a recommendation, new or legacy."""
        reco_cols = self._reco_inter_columns(
            df) + self._reco_legacy_columns(df)
        if not reco_cols:
            return pd.Series(False, index=df.index)
        return df[reco_cols].notna().any(axis=1)

    def _build_reco_weighted(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        One row per recommendation instance that should be taken into account, with
        the journey-frequency weight it should count for: ['token', 'journey',
        'reco_mode', 'days'].

        - New-style typo.reco.reco_inter.N is matched 1:1 by index N with the journey
          of the same index in data.freq_mod_journeys, and weighted by that specific
          journey's own `days` (same index convention already used for professional
          travel: freq_mod_pro_journeys.N / reco_pro.reco_pros.N).
        - Legacy typo.reco.reco_dt2.0 / .1 are general recommendations that predate
          per-journey recommendations, so each is weighted by the sum of the person's
          journey days (or 1 if no per-journey day data exists, e.g. pure V1 records) —
          this matches how these legacy recommendations were originally applied.

        Args:
            df: DataFrame of records (needs a 'token' column to key journeys/legacy
                rows; falls back to the row index when absent)

        Returns:
            DataFrame with columns ['token', 'journey', 'reco_mode', 'days'] or None
            if no recommendation data is found.
        """
        if df.empty:
            return None

        # Total journey days per token, computed directly from the journey day
        # columns rather than via _build_journey_dataframe, which additionally
        # requires a 'distance_km' column not all callers compute.
        journey_days_cols = [c for c in df.columns if re.fullmatch(
            r'data\.freq_mod_journeys\.\d+\.days', c)]
        if journey_days_cols and 'token' in df.columns:
            # Coerce before summing: some records have this field stored as a
            # non-numeric string, which would otherwise raise (or
            # string-concatenate instead of summing).
            days_by_token = df[journey_days_cols].apply(
                pd.to_numeric, errors='coerce').sum(axis=1)
            days_by_token.index = df['token']
            days_by_token = days_by_token.groupby(level=0).sum()
        else:
            days_by_token = pd.Series(dtype=float)

        token_series = df['token'] if 'token' in df.columns else pd.Series(
            df.index, index=df.index)

        # One (token, journey, reco_mode, days) frame per recommendation
        # column, concatenated at the end -- vectorized instead of a
        # Python-level `.items()` loop per column.
        frames = []
        for col in self._reco_inter_columns(df):
            journey_id = RECO_INTER_PATTERN.match(col).group(1)
            days_col = f'data.freq_mod_journeys.{journey_id}.days'
            reco_s = df[col].dropna()
            if reco_s.empty:
                continue
            idx = reco_s.index
            tokens = token_series.loc[idx]
            # Coerce: some records store this field as a non-numeric string,
            # which would otherwise raise in the arithmetic downstream
            # (energy/emissions calculations multiply by 'days').
            own_days = pd.to_numeric(df[days_col].loc[idx], errors='coerce') if days_col in df.columns else pd.Series(
                np.nan, index=idx)
            fallback_days = tokens.map(days_by_token).fillna(1)
            days = own_days.where(own_days.notna(), fallback_days)
            frames.append(pd.DataFrame({
                'token': tokens.to_numpy(),
                'journey': journey_id,
                'reco_mode': reco_s.to_numpy(),
                'days': days.to_numpy(),
            }))

        for col in self._reco_legacy_columns(df):
            journey_id = f'legacy_{col.rsplit(".", 1)[1]}'
            reco_s = df[col].dropna()
            if reco_s.empty:
                continue
            idx = reco_s.index
            tokens = token_series.loc[idx]
            days = tokens.map(days_by_token).fillna(1)
            frames.append(pd.DataFrame({
                'token': tokens.to_numpy(),
                'journey': journey_id,
                'reco_mode': reco_s.to_numpy(),
                'days': days.to_numpy(),
            }))

        if not frames:
            return None
        return pd.concat(frames, ignore_index=True)

    def _get_records_v3(self) -> pd.DataFrame:
        """Get records with data.version starting with '3.'

        Cached per instance: called repeatedly by the same stats service
        with an identical result each time. Safe to return the cached frame
        as-is (not a copy) since no caller mutates it in place -- they only
        read from it or derive new frames from it.
        """
        if self._v3_cache is None:
            if 'data.version' not in self.df.columns:
                self._v3_cache = pd.DataFrame()
            else:
                self._v3_cache = self.df[self.df['data.version'].notna(
                ) & self.df['data.version'].str.startswith('3.')].copy()
        return self._v3_cache

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
        except Exception:
            return 0

    def _calculate_distance_to_h3(self, lat: float, lon: float, h3_index: str, mode: str) -> float:
        """Calculate the distance between workplace and destination with a transport mode."""
        try:
            if pd.isna(h3_index):
                return 0
            # Hypothèse sur l'allongement des distances : en moyenne, 1.22 (network based vs real measured distances : https://journals.sagepub.com/doi/abs/10.3141/1804-28)
            # On pourrait améliorer ca en cherchant la meme chose pour l'avion (études sur les détours/distances faites lorsqu'on doit attendre au dessus d'un aéroport plein...)
            # Pareil pour le bateau (pour l'instant on applique 1.22 à tous)
            avg_dist_coeff = {
                'train': 1.22,
                'car': 1.22,
                'bike': 1.22,
                'walk': 1.22,
                'moto': 1.22,
                'pub': 1.22,
                'boat': 1.22,
                'plane': 1.22,
                'truck': 1.22,
                'cargo': 1.22,
                'other': 1.22
            }
            if h3.latlng_to_cell(lat, lon, h3.get_resolution(h3_index)) == h3_index:
                # Si meme hexagone (apres mise à la resolution choisie par l'utilisateur), on prend une distance moyenne de la taille d'une arrête de l'hexagone.
                return h3.average_hexagon_edge_length(h3.get_resolution(h3_index))
            else:
                # Si pas meme hexagone, on convertit le centre du h3 sélectionné en h3 plus petit pour calculer des distances plus précises
                return h3.great_circle_distance(h3.cell_to_latlng(h3.cell_to_center_child(h3_index, 9)),
                                                (lat, lon)) * avg_dist_coeff[mode]
        except Exception:
            return 0

    def _calculate_distance_home_to_work(self, row):
        """Calculate distance from home to workplace for a record."""
        with_origin_lat = 'data.origin.lat' in row and not pd.isna(
            row['data.origin.lat'])
        with_origin_lon = 'data.origin.lon' in row and not pd.isna(
            row['data.origin.lon'])
        with_work_lat = 'data.workplace.lat' in row and not pd.isna(
            row['data.workplace.lat'])
        with_work_lon = 'data.workplace.lon' in row and not pd.isna(
            row['data.workplace.lon'])
        if not (with_origin_lat and with_origin_lon and with_work_lat and with_work_lon):
            return 0
        origin_lat = float(row['data.origin.lat'])
        origin_lon = float(row['data.origin.lon'])
        work_lat = float(row['data.workplace.lat'])
        work_lon = float(row['data.workplace.lon'])
        return self._calculate_distance(origin_lat, origin_lon, work_lat, work_lon)

    def _calculate_distance_home_to_work_series(self, df: pd.DataFrame) -> pd.Series:
        """Vectorized equivalent of _calculate_distance_home_to_work applied
        over every row at once, instead of via DataFrame.apply(axis=1)."""
        required = ['data.origin.lat', 'data.origin.lon',
                    'data.workplace.lat', 'data.workplace.lon']
        if not all(c in df.columns for c in required):
            return pd.Series(0.0, index=df.index)

        origin_lat = pd.to_numeric(df['data.origin.lat'], errors='coerce')
        origin_lon = pd.to_numeric(df['data.origin.lon'], errors='coerce')
        work_lat = pd.to_numeric(df['data.workplace.lat'], errors='coerce')
        work_lon = pd.to_numeric(df['data.workplace.lon'], errors='coerce')
        valid = origin_lat.notna() & origin_lon.notna() & work_lat.notna() & work_lon.notna()

        with np.errstate(invalid='ignore'):
            cos_angle = (
                np.cos(np.radians(origin_lat)) * np.cos(np.radians(work_lat)) *
                np.cos(np.radians(work_lon) - np.radians(origin_lon)) +
                np.sin(np.radians(origin_lat)) * np.sin(np.radians(work_lat))
            )
            # guard against floating-point drift just past acos's [-1, 1] domain
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            distance_km = 6371 * np.arccos(cos_angle) * 1.3

        return pd.Series(np.where(valid, distance_km, 0.0), index=df.index)

    def _build_journey_dataframe(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Extract journey data from freq_mod_journeys columns.

        Extracts journey information from data.freq_mod_journeys.*.days columns
        and returns a DataFrame with journey-level information.

        Args:
            df: DataFrame with V2 records containing freq_mod_journeys data

        Returns:
            DataFrame with columns ['token', 'journey', 'days', 'dist', 'travel_time'] or None if no data
        """
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]

        if len(col_days) == 0:
            return None

        # Reshape wide day-per-journey columns into one row per (record, journey),
        # vectorized instead of a Python-level iterrows/column scan. Coerce to
        # numeric first: some records store this field as a non-numeric
        # string, which would otherwise raise on `> 0`.
        journey_id_by_col = {c: c.split('.')[2] for c in col_days}
        stacked = df[col_days].apply(pd.to_numeric, errors='coerce').stack()  # drops NaN by default
        stacked = stacked[stacked > 0]
        if stacked.empty:
            return None

        row_idx = stacked.index.get_level_values(0)
        col_idx = stacked.index.get_level_values(1)
        token_series = df['token'] if 'token' in df.columns else pd.Series(
            df.index, index=df.index)
        travel_time_series = df['data.travel_time'] if 'data.travel_time' in df.columns else pd.Series(
            0, index=df.index)

        return pd.DataFrame({
            'token': token_series.loc[row_idx].to_numpy(),
            'journey': col_idx.map(journey_id_by_col).to_numpy(),
            'days': stacked.to_numpy(),
            'dist': df['distance_km'].loc[row_idx].to_numpy(),
            'travel_time': travel_time_series.loc[row_idx].to_numpy(),
        })

    def _build_modes_dataframe(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Extract mode data from freq_mod_journeys columns.

        Extracts mode information from data.freq_mod_journeys.*.modes.* columns
        and returns a DataFrame with mode-level information.

        NOTE: Mode names are NOT normalized here to preserve the original behavior
        where intermodality calculations use raw mode names. Normalization happens
        later in the aggregation step.

        Args:
            df: DataFrame with V2 records containing freq_mod_journeys data

        Returns:
            DataFrame with columns ['token', 'journey', 'mode'] or None if no data
        """
        mode_cols = [c for c in df.columns if '.freq_mod_journeys.' in c and '.modes.' in c]
        if not mode_cols:
            return None

        journey_id_by_col = {c: c.split('.')[2] for c in mode_cols}
        stacked = df[mode_cols].stack()  # drops NaN by default
        if stacked.empty:
            return None

        row_idx = stacked.index.get_level_values(0)
        col_idx = stacked.index.get_level_values(1)
        token_series = df['token'] if 'token' in df.columns else pd.Series(
            df.index, index=df.index)

        return pd.DataFrame({
            'token': token_series.loc[row_idx].to_numpy(),
            'journey': col_idx.map(journey_id_by_col).to_numpy(),
            'mode': stacked.to_numpy(),
        })

    def _calculate_intermodality_attributes(self, combined_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate intermodality attributes for each journey.

        Determines whether each journey is intermodal (uses multiple non-walking modes)
        and whether it includes train travel.

        Args:
            combined_df: DataFrame with journeys and modes merged

        Returns:
            DataFrame with added columns: ['has_train', 'n_modes', 'is_intermodal', 'is_walking_intermodal']
        """
        combined_df['is_train'] = combined_df['mode'] == 'train'
        combined_df['is_walking'] = combined_df['mode'].isin(
            ['walking', 'marche'])

        journey_info = combined_df.groupby(['token', 'journey']).agg({
            'is_train': 'any',
            'mode': 'count',
            'is_walking': 'sum'
        }).rename(columns={'is_train': 'has_train', 'mode': 'n_modes', 'is_walking': 'n_walking'}).reset_index()

        # is_intermodal = n_modes - sum(is_walking) > 1
        journey_info['is_intermodal'] = (
            journey_info['n_modes'] - journey_info['n_walking']) > 1
        # specific treatment for walking + bike or walking + train + walking, which are a specific type of intermodality for MET
        journey_info['is_walking_intermodal'] = (journey_info['n_walking'] > 0) & (
            (journey_info['n_modes'] - journey_info['n_walking']) >= 1)

        # Join back to combined df
        combined_df = combined_df.merge(
            journey_info[['token', 'journey', 'has_train',
                          'n_modes', 'is_intermodal', 'is_walking_intermodal']],
            on=['token', 'journey'],
            how='left'
        )

        return combined_df

    def _build_journey_attributes(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Orchestrator function to build complete journey attributes dataframe.

        Combines journey extraction, mode extraction, and intermodality calculation
        into a single enriched dataframe.

        Args:
            df: DataFrame with V2 records

        Returns:
            Enriched DataFrame with all journey attributes or None if no data
            Columns: ['token', 'journey', 'days', 'dist', 'mode', 'is_train',
                     'is_walking', 'has_train', 'n_modes', 'is_intermodal', 'is_walking_intermodal']

        Cached per (instance, df identity): callers commonly invoke this
        repeatedly with the same frame (e.g. the cached _get_records_v3()
        result). A copy is returned on every call since callers mutate the
        result in place (adding computed columns).
        """
        cache_key = id(df)
        if cache_key in self._journey_attributes_cache:
            cached = self._journey_attributes_cache[cache_key]
            return None if cached is None else cached.copy()

        # Step 1: Build journeys dataframe
        journeys_df = self._build_journey_dataframe(df)
        if journeys_df is None:
            self._journey_attributes_cache[cache_key] = None
            return None

        # Step 2: Build modes dataframe
        modes_df = self._build_modes_dataframe(df)
        if modes_df is None:
            self._journey_attributes_cache[cache_key] = None
            return None

        # Step 3: Join journeys and modes
        combined_df = journeys_df.merge(
            modes_df, on=['token', 'journey'], how='inner')

        if len(combined_df) == 0:
            self._journey_attributes_cache[cache_key] = None
            return None

        # Step 4: Calculate intermodality attributes
        combined_df = self._calculate_intermodality_attributes(combined_df)

        self._journey_attributes_cache[cache_key] = combined_df
        return combined_df.copy()

    def _normalize_mode_name(self, df: pd.DataFrame, column: str) -> str:
        """Normalize mode naming, because recommendations use different terms."""
        if column not in df.columns:
            return df[column]
        df[column] = df[column].replace({
            'covoit': 'carpool',
            'velo': 'bike',
            'marche': 'walking',
            'tpu': 'pub',
            'vae': 'ebike'
        })
        return df[column]

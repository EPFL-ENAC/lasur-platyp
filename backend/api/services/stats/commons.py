import re
import pandas as pd
import h3


MODES = [
    'walking',
    'bike',
    'ebike',
    'pub',
    'moto',
    'carpool',
    'car',
    'train',
    'other'
]

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
    'week': 45,  # worked weeks
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

    def _reco_inter_columns(self, df: pd.DataFrame) -> list[str]:
        """typo.reco.reco_inter.N columns present in df, sorted by journey index N."""
        cols = [c for c in df.columns if RECO_INTER_PATTERN.match(c)]
        return sorted(cols, key=lambda c: int(RECO_INTER_PATTERN.match(c).group(1)))

    def _reco_legacy_columns(self, df: pd.DataFrame) -> list[str]:
        """typo.reco.reco_dt2.{0,1} columns present in df."""
        return [c for c in RECO_LEGACY_COLUMNS if c in df.columns]

    def _has_completed_recommendation(self, df: pd.DataFrame) -> pd.Series:
        """Boolean mask: whether a row has a recommendation, new or legacy."""
        reco_cols = self._reco_inter_columns(df) + self._reco_legacy_columns(df)
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
            days_by_token = df[journey_days_cols].sum(axis=1)
            days_by_token.index = df['token']
            days_by_token = days_by_token.groupby(level=0).sum()
        else:
            days_by_token = pd.Series(dtype=float)

        rows = []
        for col in self._reco_inter_columns(df):
            journey_id = RECO_INTER_PATTERN.match(col).group(1)
            days_col = f'data.freq_mod_journeys.{journey_id}.days'
            for idx, reco in df[col].dropna().items():
                token = df.at[idx, 'token'] if 'token' in df.columns else idx
                if days_col in df.columns and pd.notna(df.at[idx, days_col]):
                    days = df.at[idx, days_col]
                else:
                    days = days_by_token.get(token, 1)
                rows.append({'token': token, 'journey': journey_id,
                              'reco_mode': reco, 'days': days})

        for col in self._reco_legacy_columns(df):
            journey_id = f'legacy_{col.rsplit(".", 1)[1]}'
            for idx, reco in df[col].dropna().items():
                token = df.at[idx, 'token'] if 'token' in df.columns else idx
                days = days_by_token.get(token, 1)
                rows.append({'token': token, 'journey': journey_id,
                              'reco_mode': reco, 'days': days})

        if not rows:
            return None
        return pd.DataFrame(rows)

    def _get_records_v1(self) -> pd.DataFrame:
        """Get records with data.version as NaN"""
        if 'data.version' not in self.df.columns:
            return self.df.copy()
        df_v1 = self.df[self.df['data.version'].isna()].copy()
        return df_v1

    def _get_records_v2(self) -> pd.DataFrame:
        """Get records with data.version starting with '2.'"""
        if 'data.version' not in self.df.columns:
            return pd.DataFrame()
        df_v2 = self.df[self.df['data.version'].notna(
        ) & self.df['data.version'].str.startswith('2.')].copy()
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

        journeys_list = []
        for idx, row in df.iterrows():
            for col in col_days:
                days = row[col]
                if pd.notna(days) and days > 0:
                    # Extract journey number from column name
                    journey_id = col.split('.')[2]
                    journeys_list.append({
                        'token': row.get('token', idx),
                        'journey': journey_id,
                        'days': days,
                        'dist': row['distance_km'],
                        'travel_time': row.get('data.travel_time', 0)
                    })

        if len(journeys_list) == 0:
            return None

        return pd.DataFrame(journeys_list)

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
        modes_list = []
        for idx, row in df.iterrows():
            for col in df.columns:
                if '.freq_mod_journeys.' in col and '.modes.' in col:
                    mode_val = row[col]
                    if pd.notna(mode_val):
                        parts = col.split('.')
                        journey_id = parts[2]
                        modes_list.append({
                            'token': row.get('token', idx),
                            'journey': journey_id,
                            'mode': mode_val
                        })

        if len(modes_list) == 0:
            return None

        return pd.DataFrame(modes_list)

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
        """
        # Step 1: Build journeys dataframe
        journeys_df = self._build_journey_dataframe(df)
        if journeys_df is None:
            return None

        # Step 2: Build modes dataframe
        modes_df = self._build_modes_dataframe(df)
        if modes_df is None:
            return None

        # Step 3: Join journeys and modes
        combined_df = journeys_df.merge(
            modes_df, on=['token', 'journey'], how='inner')

        if len(combined_df) == 0:
            return None

        # Step 4: Calculate intermodality attributes
        combined_df = self._calculate_intermodality_attributes(combined_df)

        return combined_df

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

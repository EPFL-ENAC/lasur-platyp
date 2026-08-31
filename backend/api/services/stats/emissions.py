import numpy as np
import pandas as pd
from api.models.query import EmissionReductions, Emissions
from api.services.stats.commons import (
    BaseStatsService, MODES_PRO, normalize_pro_days_to_yearly,
    COMPLEX_LABEL_MERGE, merge_label_components,
)

MODE_EMISSIONS = {
    'walking': 0,
    'bike': 6,
    'ebike': 11,
    'pub': 25,
    'moto': 155,
    'elec_moto': 82,
    'carpool': 93,
    'car': 186,
    'train': 8,
    'boat': 161,
    'plane': 263,
    'elec': 90,
    'vae': 11,
    'cargo': 11,
    'tpu': 25,
    'velo': 6,
    'marche': 0,
    'covoit': 93,
    'avoid': 0,
    'other': 45.7,
    'inter': 56.72391025641025,  # Mean intermodality emissions calculated from dataset
    'truck': 300,
    'elec_truck': 150
}

class EmissionsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self._pro_journey_cache = {}
        # Calculate distance_km to workplace for each record
        if self.df.empty:
            self.df['distance_km'] = pd.Series(dtype=float)
        else:
            self.df['distance_km'] = self._calculate_distance_home_to_work_series(self.df)

    def compute_modes_emissions_simple_labels(self, apply_reco: bool = False) -> list[Emissions]:
        """
        Compute CO2 emissions grouped by typo.reco.simple_labels (v3 records
        only). Journeys are always grouped by their current simple label; if
        apply_reco is True, the emissions value reported for each label is
        what the journeys in that label would emit by following their
        recommendation, instead of their current emissions.
        """
        return self._compute_journey_emissions_by_label(
            self._get_records_v3(), 'typo.reco.simple_labels', apply_reco)

    def compute_modes_emissions_complex_labels(self, apply_reco: bool = False) -> list[Emissions]:
        """
        Compute CO2 emissions grouped by typo.reco.complex_labels (v3
        records only). Journeys are always grouped by their current complex
        label; if apply_reco is True, the emissions value reported for each
        label is what the journeys in that label would emit by following
        their recommendation, instead of their current emissions.
        COMPLEX_LABEL_MERGE values ("pub" and "train") are merged into "tp",
        component-wise so intermodal combos fold too (e.g. "car+pub" -> "car+tp").
        """
        return self._compute_journey_emissions_by_label(
            self._get_records_v3(), 'typo.reco.complex_labels', apply_reco,
            merge_labels=COMPLEX_LABEL_MERGE)

    def compute_modes_emission_reductions_simple_labels(self) -> list[EmissionReductions]:
        """Compute potential CO2 emission reductions grouped by typo.reco.simple_labels (v3 records only)."""
        return self._compute_journey_emission_reductions_by_label(
            self._get_records_v3(), 'typo.reco.simple_labels')

    def compute_modes_emission_reductions_complex_labels(self) -> list[EmissionReductions]:
        """Compute potential CO2 emission reductions grouped by typo.reco.complex_labels
        (v3 records only). COMPLEX_LABEL_MERGE values ("pub" and "train") are
        merged into "tp", component-wise so intermodal combos fold too
        (e.g. "car+pub" -> "car+tp")."""
        return self._compute_journey_emission_reductions_by_label(
            self._get_records_v3(), 'typo.reco.complex_labels',
            merge_labels=COMPLEX_LABEL_MERGE)

    def compute_modes_pro_emissions(self, apply_reco: bool = False) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records for pro journeys (v3 only)."""
        df_v3 = self._get_records_v3()
        results = []
        if not df_v3.empty:
            for mode in MODES_PRO:
                results.extend(
                    self._compute_mode_pro_emissions_v3(df_v3, mode, apply_reco))

        # finalize totals
        for emission in results:
            emission.total = len(df_v3)
            # round distances, emissions
            emission.distances = round(emission.distances, 3)
            emission.emissions = round(emission.emissions, 3)
        # filter out emissions with zero emissions
        results = [e for e in results if e.emissions > 0]

        return results

    def compute_modes_pro_emission_reductions(
        self, 
        include_negative: bool = False
    ) -> list[EmissionReductions]:
        """
        Compute CO2 emission reductions for professional travel.
        
        Calculates savings when professional travel recommendations are applied,
        grouped by recommended mode.
        
        Key differences from commute reductions:
        - Uses per-journey recommendations (typo.reco_pro.reco_pros.{i})
        - No intermodality (professional travel is single-mode)
        - Annual frequency (days * 2, not days * 2 * 45)
        - Distances calculated to H3 hex locations
        - 'avoid' recommendations have 0 emissions (maximum savings)
        
        Args:
            include_negative: If True, includes cases where recommendations
                             increase emissions. If False (default), only
                             includes positive reductions.
        
        Returns:
            List of EmissionReductions objects, one per recommended mode
            
        Example:
            If someone has:
            - Journey 0: plane (12 kgCO2) → train (1 kgCO2) = 11 kg saved
            - Journey 1: car (5 kgCO2) → train (0.2 kgCO2) = 4.8 kg saved
            Results: [EmissionReductions(mode='train', reduced=15.8)]
        """
        df_v3 = self._get_records_v3()
        if df_v3.empty:
            return []

        results = self._compute_mode_pro_emission_reductions_v3(
            df_v3, include_negative
        )

        # Finalize totals
        for reduction in results:
            reduction.total = len(df_v3)
            reduction.reduced = round(reduction.reduced, 3)
        
        # Filter based on include_negative parameter
        if include_negative:
            results = [e for e in results if e.reduced != 0]
        else:
            results = [e for e in results if e.reduced > 0]
        
        return results

    #
    # Internal functions
    #

    #
    # Shared Journey Processing Pipeline
    #

    def _build_journey_dataframe(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Extract journey data from freq_mod_journeys columns.
        
        Extracts journey information from data.freq_mod_journeys.*.days columns
        and returns a DataFrame with journey-level information.
        
        Args:
            df: DataFrame with v3 records containing freq_mod_journeys data
            
        Returns:
            DataFrame with columns ['token', 'journey', 'days', 'dist'] or None if no data
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

        return pd.DataFrame({
            'token': token_series.loc[row_idx].to_numpy(),
            'journey': col_idx.map(journey_id_by_col).to_numpy(),
            'days': stacked.to_numpy(),
            'dist': df['distance_km'].loc[row_idx].to_numpy(),
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
            df: DataFrame with v3 records containing freq_mod_journeys data
            
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
            DataFrame with added columns: ['has_train', 'n_modes', 'is_intermodal']
        """
        combined_df['is_train'] = combined_df['mode'] == 'train'
        combined_df['is_walking'] = combined_df['mode'].isin(['walking', 'marche'])
        
        journey_info = combined_df.groupby(['token', 'journey']).agg({
            'is_train': 'any',
            'mode': 'count',
            'is_walking': 'sum'
        }).rename(columns={'is_train': 'has_train', 'mode': 'n_modes', 'is_walking': 'n_walking'}).reset_index()
        
        # is_intermodal = n_modes - sum(is_walking) > 1
        journey_info['is_intermodal'] = (journey_info['n_modes'] - journey_info['n_walking']) > 1
        
        # Join back to combined df
        combined_df = combined_df.merge(
            journey_info[['token', 'journey', 'has_train', 'n_modes', 'is_intermodal']], 
            on=['token', 'journey'], 
            how='left'
        )
        
        return combined_df

    def _calculate_mode_fractions(self, combined_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the fraction of distance attributed to each mode in a journey.
        
        For intermodal journeys:
        - If train is present: train gets 80%, other modes split 20%
        - Otherwise: equal split among all modes
        For single-mode journeys: 100% to that mode
        
        Args:
            combined_df: DataFrame with intermodality attributes
            
        Returns:
            DataFrame with added columns: ['mode_fraction', 'dist_mode']
        """
        with np.errstate(divide='ignore', invalid='ignore'):
            # 0.2 / (n_modes - 1) where n_modes includes walking
            train_other_fraction = 0.2 / (combined_df['n_modes'] - 1)
            # Equal split among all modes
            equal_split_fraction = 1.0 / combined_df['n_modes']

        combined_df['mode_fraction'] = np.where(
            combined_df['is_intermodal'],
            np.where(combined_df['has_train'],
                     np.where(combined_df['is_train'], 0.8, train_other_fraction),
                     equal_split_fraction),
            1.0
        )
        
        # Apply to distance
        combined_df['dist_mode'] = combined_df['dist'] * combined_df['mode_fraction']
        
        return combined_df

    def _build_journey_attributes(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Orchestrator function to build complete journey attributes dataframe.
        
        Combines journey extraction, mode extraction, intermodality calculation,
        and mode fraction calculation into a single enriched dataframe.
        
        Args:
            df: DataFrame with v3 records
            
        Returns:
            Enriched DataFrame with all journey attributes or None if no data
            Columns: ['token', 'journey', 'days', 'dist', 'mode', 'is_train',
                     'is_walking', 'has_train', 'n_modes', 'is_intermodal',
                     'mode_fraction', 'dist_mode']

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
        combined_df = journeys_df.merge(modes_df, on=['token', 'journey'], how='inner')

        if len(combined_df) == 0:
            self._journey_attributes_cache[cache_key] = None
            return None

        # Step 4: Calculate intermodality attributes
        combined_df = self._calculate_intermodality_attributes(combined_df)

        # Step 5: Calculate mode fractions
        combined_df = self._calculate_mode_fractions(combined_df)

        self._journey_attributes_cache[cache_key] = combined_df
        return combined_df.copy()

    def _calculate_journey_metrics(
        self, 
        journey_df: pd.DataFrame, 
        metric_factors: dict[str, float], 
        metric_name: str,
        frequency_weeks: int = 45
    ) -> pd.DataFrame:
        """
        Generic function to calculate any metric (CO2, MET, etc.) for journeys.
        
        Applies metric factors to journey distances and frequencies using the formula:
        metric_value = metric_factor / 1000 * dist_mode * days * 2 * frequency_weeks
        
        Args:
            journey_df: DataFrame with journey attributes (must have 'mode', 'dist_mode', 'days')
            metric_factors: Dictionary mapping mode names to metric factors
            metric_name: Name for the metric (used for column naming)
            frequency_weeks: Number of weeks per year for frequency calculation (default: 45)
            
        Returns:
            DataFrame with added column: '{metric_name}_value'
            
        Example:
            # Calculate CO2 emissions
            df = _calculate_journey_metrics(df, MODE_EMISSIONS, 'co2')
            # Adds column: 'co2_value'
            
            # Calculate MET values (future)
            df = _calculate_journey_metrics(df, MODE_MET, 'met')
            # Adds column: 'met_value'
        """
        journey_df['emissions_factor'] = journey_df['mode'].map(metric_factors)
        journey_df[f'{metric_name}_value'] = (
            journey_df['emissions_factor'] / 1000 *
            journey_df['dist_mode'] * journey_df['days'] * 2 * frequency_weeks
        )
        
        return journey_df

    def _build_pro_journey_dataframe(self, df: pd.DataFrame, target_mode: str | None = None) -> pd.DataFrame | None:
        """
        Extract professional journey data from freq_mod_pro_journeys columns.
        
        Professional journeys are simpler than daily commutes - no intermodality,
        and distances are calculated to H3 hex locations.
        
        Args:
            df: DataFrame with v3 records containing freq_mod_pro_journeys data
            target_mode: Optional mode to filter by (if None, returns all modes)
            
        Returns:
            DataFrame with columns ['token', 'journey_idx', 'mode', 'days', 'hex_id',
                                   'workplace_lat', 'workplace_lon', 'distance_km']
            or None if no data

        Cached per (instance, df identity): compute_modes_pro_emissions() calls
        this once per professional mode (~10x) with the same df. Building the
        full (unfiltered) frame once and filtering it per mode avoids
        rescanning every row x journey column for each mode.
        """
        cache_key = id(df)
        if cache_key not in self._pro_journey_cache:
            self._pro_journey_cache[cache_key] = self._build_pro_journey_dataframe_uncached(df)

        full = self._pro_journey_cache[cache_key]
        if full is None:
            return None
        if target_mode is not None:
            full = full[full['mode'] == target_mode]
            if full.empty:
                return None
        return full.copy()

    def _build_pro_journey_dataframe_uncached(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """All professional journeys across all modes, vectorized (no target_mode filter)."""
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_pro_journeys\..*\.days$', regex=True)]

        if len(col_days) == 0:
            return None
        if 'data.workplace.lat' not in df.columns or 'data.workplace.lon' not in df.columns:
            return None

        token_series = df['token'] if 'token' in df.columns else pd.Series(
            df.index, index=df.index)
        workplace_lat_series = df['data.workplace.lat']
        workplace_lon_series = df['data.workplace.lon']
        has_workplace = workplace_lat_series.notna() & workplace_lon_series.notna()

        frames = []
        for i in range(len(col_days)):
            col_mode_i = f'data.freq_mod_pro_journeys.{str(i)}.mode'
            if col_mode_i not in df.columns:
                continue
            col_hexid_i = f'data.freq_mod_pro_journeys.{str(i)}.hex_id'
            if col_hexid_i not in df.columns:
                continue
            col_days_i = col_days[i]
            col_days_per_i = f'data.freq_mod_pro_journeys.{str(i)}.days_per'

            mode_s = df[col_mode_i]
            # Coerce before comparing/using: some records have this field
            # stored as a non-numeric string, which would otherwise raise on
            # `> 0` (invalid values are treated as missing).
            days_s = pd.to_numeric(df[col_days_i], errors='coerce')
            hexid_s = df[col_hexid_i]
            days_per_s = df[col_days_per_i] if col_days_per_i in df.columns else pd.Series(
                None, index=df.index)

            mask = mode_s.notna() & days_s.notna() & (
                days_s > 0) & hexid_s.notna() & has_workplace
            if not mask.any():
                continue

            sub_idx = df.index[mask]
            frames.append(pd.DataFrame({
                'token': token_series.loc[sub_idx].to_numpy(),
                'journey_idx': i,
                'mode': mode_s.loc[sub_idx].to_numpy(),
                'days_raw': days_s.loc[sub_idx].to_numpy(),
                'days_per': days_per_s.loc[sub_idx].to_numpy(),
                'hex_id': hexid_s.loc[sub_idx].to_numpy(),
                'workplace_lat': workplace_lat_series.loc[sub_idx].to_numpy(),
                'workplace_lon': workplace_lon_series.loc[sub_idx].to_numpy(),
            }))

        if not frames:
            return None

        combined = pd.concat(frames, ignore_index=True)

        # Small pure-Python helper applied only to surviving (record, journey)
        # pairs, not the full rows x journeys space.
        combined['days'] = combined.apply(
            lambda r: normalize_pro_days_to_yearly(r['days_raw'], r['days_per']), axis=1)

        # h3 has no bulk/vectorized distance API, so this stays a per-row
        # apply -- but now computed exactly once per valid pair instead of
        # once per pair per professional mode.
        combined['distance_km'] = combined.apply(
            lambda r: self._calculate_distance_to_h3(
                float(r['workplace_lat']), float(r['workplace_lon']), r['hex_id'], r['mode']),
            axis=1)

        return combined[['token', 'journey_idx', 'mode', 'days', 'hex_id',
                          'workplace_lat', 'workplace_lon', 'distance_km']]

    def _compute_journey_emissions_by_label(
        self, df: pd.DataFrame, label_prefix: str, apply_reco: bool = False,
        merge_labels: dict[str, str] | None = None,
    ) -> list[Emissions]:
        """
        Aggregate journey-level CO2 emissions by a per-journey label column
        (typo.reco.simple_labels.N or typo.reco.complex_labels.N), crediting
        each journey's full emissions/distance to exactly one label bucket
        instead of splitting across its raw modes.

        Journeys are always grouped by their current label (there is no
        "recommended label" in the data). When apply_reco is True, the value
        reported per label is what those journeys would emit by following
        their recommendation, instead of their current emissions -- distances
        and journey counts are unaffected since only the mode/emission factor
        changes, not the trip itself.

        Reuses the same journey/mode-fraction pipeline as commute emissions
        (_build_journey_attributes, _calculate_journey_metrics), which is
        version-agnostic, then collapses per-mode rows back to one row per
        journey before grouping by label.

        Args:
            df: DataFrame of records already filtered to the relevant version
                (e.g. v3), containing data.freq_mod_journeys.* and the given
                label columns
            label_prefix: column prefix without the trailing journey index,
                e.g. 'typo.reco.simple_labels'
            apply_reco: if True, report recommended (post-reco) emissions
                instead of current emissions; only journeys with a
                recommendation are included
            merge_labels: optional {raw_label: target_label} remap applied
                component-wise (via merge_label_components) to observed
                labels before grouping, so several raw labels -- and any
                '+'-joined intermodal combination containing them -- fold
                into a single bucket (e.g. merging "pub" and "train" into "tp"
                also folds "car+pub" into "car+tp")

        Returns:
            List of Emissions objects (one per observed label)
        """
        if df.empty:
            return []

        if apply_reco:
            # Only journeys with a recommendation can report a post-reco
            # emissions value; reuses the same current-vs-recommended
            # pipeline as the emission-reduction-by-label variant.
            journey_df = self._build_journey_emission_savings(df)
            if journey_df is None:
                return []
            journey_df = journey_df.rename(
                columns={'reco_emissions': 'emissions'})[['token', 'journey', 'dist', 'days', 'emissions']]
        else:
            combined_df = self._build_journey_attributes(df)
            if combined_df is None:
                return []

            combined_df = self._calculate_journey_metrics(combined_df, MODE_EMISSIONS, 'co2')

            # Collapse per-mode rows back to one row per journey: sum co2
            # across modes in an intermodal journey, dist/days are the same
            # for every mode row of a given journey.
            journey_df = combined_df.groupby(['token', 'journey']).agg(
                emissions=('co2_value', 'sum'), dist=('dist', 'first'), days=('days', 'first')
            ).reset_index()

        label_frame = self._build_label_frame(df, label_prefix)
        if label_frame is None:
            return []

        if merge_labels:
            label_frame = label_frame.assign(
                label=label_frame['label'].map(
                    lambda label: merge_label_components(str(label), merge_labels)))

        merged = journey_df.merge(label_frame, on=['token', 'journey'], how='inner')

        results = []
        for label in merged['label'].unique():
            dfl = merged[merged['label'] == label]
            results.append(Emissions(
                mode=str(label),
                total=len(df),
                distances=round(float((dfl['dist'] * dfl['days'] * 2 * 45).sum()), 3),
                journeys=int((dfl['days'] * 2 * 45).sum()),
                emissions=round(float(dfl['emissions'].sum()), 3),
            ))

        # filter out labels with zero emissions
        return [e for e in results if e.emissions > 0]

    def _build_journey_emission_savings(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Build a per-(token, journey, recommendation) DataFrame with both
        current and potential recommended CO2 emissions, shared by every
        emission-reduction grouping (by recommended mode, or by the
        journey's own v3 typology label).

        Based on R implementation (Untitled.R lines 223-227):
        - Calculates emissions_dt (current) and reco_emissions (recommended)
        - saved_emissions = emissions_dt - reco_emissions

        Args:
            df: DataFrame of records (v3) containing
                data.freq_mod_journeys.* and recommendation columns

        Returns:
            DataFrame with columns ['token', 'journey', 'dist', 'days',
            'is_intermodal', 'emissions_dt', 'reco_mode', 'reco_emissions',
            'saved_emissions'], or None if no data / no recommendations
        """
        if len(df) == 0:
            return None

        # Step 1: Build journey attributes using shared pipeline
        df_combined = self._build_journey_attributes(df)
        if df_combined is None:
            return None

        # Step 2: Calculate current CO2 emissions
        df_combined = self._calculate_journey_metrics(df_combined, MODE_EMISSIONS, 'co2')
        df_combined['emissions_dt'] = df_combined['co2_value']

        # Step 3: Aggregate by journey to get total emissions per journey
        # (needed because we have one row per mode, but need journey-level aggregation)
        journey_emissions = df_combined.groupby(['token', 'journey']).agg({
            'emissions_dt': 'sum',
            'dist': 'first',
            'days': 'first',
            'is_intermodal': 'first'
        }).reset_index()

        # Step 4: Get recommendation(s) for each journey. New-style
        # typo.reco.reco_inter.N is that specific journey's own recommendation
        # (matched by index); legacy typo.reco.reco_dt2.0/.1 general
        # recommendations (not tied to a specific journey) apply independently to
        # every journey of the person, as originally computed.
        token_series = df['token'] if 'token' in df.columns else pd.Series(
            df.index, index=df.index)

        new_frames = []
        for col in self._reco_inter_columns(df):
            journey_id = col.rsplit('.', 1)[1]
            reco_s = df[col].dropna()
            if reco_s.empty:
                continue
            new_frames.append(pd.DataFrame({
                'token': token_series.loc[reco_s.index].to_numpy(),
                'journey': journey_id,
                'reco_mode': reco_s.to_numpy(),
            }))
        new_reco_df = pd.concat(new_frames, ignore_index=True) if new_frames else pd.DataFrame(
            columns=['token', 'journey', 'reco_mode'])

        legacy_frames = []
        for col in self._reco_legacy_columns(df):
            reco_s = df[col].dropna()
            if reco_s.empty:
                continue
            legacy_frames.append(pd.DataFrame({
                'token': token_series.loc[reco_s.index].to_numpy(),
                'reco_mode': reco_s.to_numpy(),
            }))
        legacy_reco_df = pd.concat(legacy_frames, ignore_index=True) if legacy_frames else pd.DataFrame(
            columns=['token', 'reco_mode'])

        if new_reco_df.empty and legacy_reco_df.empty:
            return None

        frames = []
        if not new_reco_df.empty:
            frames.append(journey_emissions.merge(
                new_reco_df, on=['token', 'journey'], how='inner'))
        if not legacy_reco_df.empty:
            frames.append(journey_emissions.merge(
                legacy_reco_df, on='token', how='inner'))
        journey_emissions = pd.concat(frames, ignore_index=True)

        # Normalize mode names
        journey_emissions['reco_mode'] = self._normalize_mode_name(journey_emissions, 'reco_mode')

        reco_mode = journey_emissions['reco_mode']
        valid_mode = reco_mode.notna() & reco_mode.isin(MODE_EMISSIONS.keys())
        # If already intermodal and recommended mode is "inter", keep current emissions
        keep_current = journey_emissions['is_intermodal'] & (reco_mode == 'inter')

        reco_em = (
            journey_emissions['dist'] * reco_mode.map(MODE_EMISSIONS) *
            journey_emissions['days'] * 2 * 45 / 1000
        )
        emissions_dt = journey_emissions['emissions_dt']
        # Only return the recommended emissions if it's a reduction compared to current emissions
        reco_em_capped = np.where(
            emissions_dt.notna(), np.minimum(reco_em, emissions_dt), reco_em)

        journey_emissions['reco_emissions'] = np.where(
            ~valid_mode, np.nan,
            np.where(keep_current, emissions_dt, reco_em_capped)
        )

        # Step 7: Calculate reductions per recommended mode (R lines 223-227)
        journey_emissions['saved_emissions'] = journey_emissions['emissions_dt'] - journey_emissions['reco_emissions']

        return journey_emissions

    def _compute_journey_emission_reductions_by_label(
        self, df: pd.DataFrame, label_prefix: str,
        merge_labels: dict[str, str] | None = None,
    ) -> list[EmissionReductions]:
        """
        Aggregate potential CO2 emission reductions by each journey's own v3
        typology label (typo.reco.simple_labels.N / typo.reco.complex_labels.N)
        instead of by the recommended mode: "how much could journeys
        currently labeled X save by following their recommendation?"

        Args:
            df: DataFrame of records already filtered to v3
            label_prefix: column prefix without the trailing journey index,
                e.g. 'typo.reco.simple_labels'
            merge_labels: optional {raw_label: target_label} remap applied
                component-wise (via merge_label_components) to observed
                labels before grouping, so several raw labels -- and any
                '+'-joined intermodal combination containing them -- fold
                into a single bucket (e.g. merging "pub" and "train" into "tp"
                also folds "car+pub" into "car+tp")

        Returns:
            List of EmissionReductions objects (one per observed label)
        """
        journey_emissions = self._build_journey_emission_savings(df)
        if journey_emissions is None:
            return []

        label_frame = self._build_label_frame(df, label_prefix)
        if label_frame is None:
            return []

        if merge_labels:
            label_frame = label_frame.assign(
                label=label_frame['label'].map(
                    lambda label: merge_label_components(str(label), merge_labels)))

        merged = journey_emissions.merge(label_frame, on=['token', 'journey'], how='inner')

        results = []
        for label in merged['label'].unique():
            dfl = merged[merged['label'] == label]
            reduction_total = float(dfl[dfl['saved_emissions'] > 0]['saved_emissions'].sum())
            results.append(EmissionReductions(
                mode=str(label),
                total=len(df),
                reduced=round(reduction_total, 3)
            ))

        return [e for e in results if e.reduced > 0]

    def _compute_mode_pro_emission_reductions_v3(
        self, 
        df: pd.DataFrame, 
        include_negative: bool = False
    ) -> list[EmissionReductions]:
        """
        Compute professional travel CO2 emission reductions for v3 data.
        
        Based on viz_v2.ipynb logic (cells 31-32):
        - For each professional journey: calculate current vs reco emissions
        - Accumulate savings per recommended mode
        - Professional journeys use annual frequency (no * 45 multiplier)
        
        Formula per journey:
            current_emissions = distance * MODE_EMISSIONS[current_mode] * days * 2 / 1000
            reco_emissions = distance * MODE_EMISSIONS[reco_mode] * days * 2 / 1000
            savings = current_emissions - reco_emissions
        
        Args:
            df: DataFrame with v3 records
            include_negative: Whether to include negative savings
            
        Returns:
            List of EmissionReductions objects
        """
        if len(df) == 0:
            return []

        # Extract professional journey columns
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_pro_journeys\..*\.days$', regex=True)]

        if len(col_days) == 0:
            return []
        if 'data.workplace.lat' not in df.columns or 'data.workplace.lon' not in df.columns:
            return []

        workplace_lat_series = df['data.workplace.lat']
        workplace_lon_series = df['data.workplace.lon']
        has_workplace = workplace_lat_series.notna() & workplace_lon_series.notna()

        # Process each journey index (0, 1, 2, ...), vectorized across rows
        # instead of a Python-level iterrows loop.
        frames = []
        for i in range(len(col_days)):
            col_mode_i = f'data.freq_mod_pro_journeys.{i}.mode'
            col_reco_i = f'typo.reco_pro.reco_pros.{i}'
            col_hexid_i = f'data.freq_mod_pro_journeys.{i}.hex_id'
            col_days_i = f'data.freq_mod_pro_journeys.{i}.days'
            col_days_per_i = f'data.freq_mod_pro_journeys.{i}.days_per'

            # Skip if columns don't exist
            if (col_mode_i not in df.columns or
                col_reco_i not in df.columns or
                col_hexid_i not in df.columns or
                col_days_i not in df.columns):
                continue

            mode_s = df[col_mode_i]
            reco_s = df[col_reco_i]
            hexid_s = df[col_hexid_i]
            # Coerce before using: some records have this field stored as a
            # non-numeric string, which would otherwise raise downstream
            # (normalize_pro_days_to_yearly's multiplication, or `> 0` below).
            days_raw_s = pd.to_numeric(df[col_days_i], errors='coerce')
            days_per_s = df[col_days_per_i] if col_days_per_i in df.columns else pd.Series(
                None, index=df.index)

            mask = mode_s.notna() & reco_s.notna() & days_raw_s.notna(
            ) & hexid_s.notna() & has_workplace
            if not mask.any():
                continue

            sub_idx = df.index[mask]
            frames.append(pd.DataFrame({
                'mode': mode_s.loc[sub_idx].to_numpy(),
                'reco_mode': reco_s.loc[sub_idx].to_numpy(),
                'hex_id': hexid_s.loc[sub_idx].to_numpy(),
                'days_raw': days_raw_s.loc[sub_idx].to_numpy(),
                'days_per': days_per_s.loc[sub_idx].to_numpy(),
                'workplace_lat': workplace_lat_series.loc[sub_idx].to_numpy(),
                'workplace_lon': workplace_lon_series.loc[sub_idx].to_numpy(),
            }))

        if not frames:
            return []

        combined = pd.concat(frames, ignore_index=True)

        combined['days'] = combined.apply(
            lambda r: normalize_pro_days_to_yearly(r['days_raw'], r['days_per']), axis=1)
        # Skip if missing data or no recommendation (per user requirement #3)
        combined = combined[combined['days'] > 0]
        if combined.empty:
            return []

        # h3 has no bulk/vectorized distance API, so this stays a per-row
        # apply, but only over surviving (record, journey) pairs.
        combined['distance_km'] = combined.apply(
            lambda r: self._calculate_distance_to_h3(
                float(r['workplace_lat']), float(r['workplace_lon']), r['hex_id'], r['mode']),
            axis=1)

        # Get emission factors with mode name normalization (per user requirement #1)
        mode_map = {
            'covoit': 'carpool', 'velo': 'bike', 'marche': 'walking',
            'tpu': 'pub', 'vae': 'ebike'
        }
        combined['current_mode_normalized'] = combined['mode'].replace(mode_map)
        combined['reco_mode_normalized'] = combined['reco_mode'].replace(mode_map)
        current_emission_factor = combined['current_mode_normalized'].map(
            MODE_EMISSIONS).fillna(0)
        reco_emission_factor = combined['reco_mode_normalized'].map(
            MODE_EMISSIONS).fillna(0)

        # Formula: distance * emission_factor * days * 2 / 1000
        # Note: No * 45 for professional travel (annual frequency, not weekly)
        savings = (
            combined['distance_km'] * current_emission_factor * combined['days'] * 2 / 1000
            - combined['distance_km'] * reco_emission_factor * combined['days'] * 2 / 1000
        )
        savings_by_reco = savings.groupby(combined['reco_mode_normalized']).sum()

        # Convert to EmissionReductions objects
        return [
            EmissionReductions(mode=mode, total=len(df), reduced=float(reduced))
            for mode, reduced in savings_by_reco.items()
        ]

    def _compute_mode_pro_emissions_v3(self, df: pd.DataFrame, mode: str, apply_reco: bool = False) -> list[Emissions]:
        """
        Compute all CO2 emissions from professional travel for a specific mode.
        
        Professional travel is simpler than daily commutes:
        - No intermodality (single mode per journey)
        - Distances calculated to H3 hex locations
        - Uses same emission factors as daily commutes
        
        Args:
            df: DataFrame with v3 records containing freq_mod_pro_journeys data
            mode: Mode to calculate emissions for
            apply_reco: Currently unused for professional travel (no recommendations yet)
            
        Returns:
            List with single Emissions object for the specified mode
        """
        if len(df) == 0:
            return [Emissions(mode=mode, total=0, distances=0, journeys=0, emissions=0)]
        
        # Build professional journey dataframe for this mode
        journey_df = self._build_pro_journey_dataframe(df, target_mode=mode)
        
        if journey_df is None or len(journey_df) == 0:
            return [Emissions(mode=mode, total=len(df), distances=0, journeys=0, emissions=0)]
        
        # Professional travel uses simple metric calculation (no mode fractions/intermodality)
        # Add dist_mode column (same as distance_km for pro travel)
        journey_df['dist_mode'] = journey_df['distance_km']
        
        # Calculate CO2 emissions using generic framework
        # Note: Professional travel uses weeks=1 instead of 45 (annual vs weekly frequency)
        journey_df['emissions_factor'] = journey_df['mode'].map(MODE_EMISSIONS)
        journey_df['co2_value'] = (
            journey_df['emissions_factor'] / 1000 *
            journey_df['dist_mode'] * journey_df['days'] * 2  # Note: no * 45 for pro travel
        )
        
        # Aggregate results
        total_distances = float((journey_df['distance_km'] * journey_df['days'] * 2).sum())
        total_journeys = int((journey_df['days'] * 2).sum())
        total_emissions = float(journey_df['co2_value'].sum())
        
        return [Emissions(
            mode=mode,
            total=len(df),
            distances=total_distances,
            journeys=total_journeys,
            emissions=total_emissions
        )]

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

    def _normalize_mode_value(self, mode_value: str) -> str:
        """
        Normalize a single mode value.
        
        Helper for normalizing mode names without needing a DataFrame column.
        Applies same mapping as _normalize_mode_name for consistency.
        
        Args:
            mode_value: Raw mode string (e.g., 'velo', 'tpu', 'marche')
            
        Returns:
            Normalized mode string (e.g., 'bike', 'pub', 'walking')
        """
        mode_map = {
            'covoit': 'carpool',
            'velo': 'bike',
            'marche': 'walking',
            'tpu': 'pub',
            'vae': 'ebike'
        }
        return mode_map.get(mode_value, mode_value)


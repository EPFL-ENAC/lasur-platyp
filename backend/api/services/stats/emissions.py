import re
import pandas as pd
from api.models.query import EmissionReductions, Emissions
from api.services.stats.commons import BaseStatsService, MODES_PRO, normalize_pro_days_to_yearly

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
        # Calculate distance_km to workplace for each record
        if self.df.empty:
            self.df['distance_km'] = pd.Series(dtype=float)
        else:
            self.df['distance_km'] = self.df.apply(
                self._calculate_distance_home_to_work, axis=1)

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
        """
        return self._compute_journey_emissions_by_label(
            self._get_records_v3(), 'typo.reco.complex_labels', apply_reco)

    def compute_modes_emission_reductions_simple_labels(self) -> list[EmissionReductions]:
        """Compute potential CO2 emission reductions grouped by typo.reco.simple_labels (v3 records only)."""
        return self._compute_journey_emission_reductions_by_label(
            self._get_records_v3(), 'typo.reco.simple_labels')

    def compute_modes_emission_reductions_complex_labels(self) -> list[EmissionReductions]:
        """Compute potential CO2 emission reductions grouped by typo.reco.complex_labels (v3 records only)."""
        return self._compute_journey_emission_reductions_by_label(
            self._get_records_v3(), 'typo.reco.complex_labels')

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
                        'dist': row['distance_km']
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
            df: DataFrame with v3 records containing freq_mod_journeys data
            
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
        def calc_mode_fraction(row):
            if row['is_intermodal']:
                if row['has_train']:
                    if row['is_train']:
                        return 0.8
                    else:
                        # 0.2 / (n_modes - 1) where n_modes includes walking
                        return 0.2 / (row['n_modes'] - 1)
                else:
                    # Equal split among all modes
                    return 1.0 / row['n_modes']
            else:
                return 1.0
        
        combined_df['mode_fraction'] = combined_df.apply(calc_mode_fraction, axis=1)
        
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
        combined_df = journeys_df.merge(modes_df, on=['token', 'journey'], how='inner')
        
        if len(combined_df) == 0:
            return None
        
        # Step 4: Calculate intermodality attributes
        combined_df = self._calculate_intermodality_attributes(combined_df)
        
        # Step 5: Calculate mode fractions
        combined_df = self._calculate_mode_fractions(combined_df)
        
        return combined_df

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
        """
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_pro_journeys\..*\.days$', regex=True)]
        
        if len(col_days) == 0:
            return None
        
        journeys_list = []
        
        for i in range(len(col_days)):
            col_mode_i = f'data.freq_mod_pro_journeys.{str(i)}.mode'
            if col_mode_i not in df.columns:
                continue
            col_hexid_i = f'data.freq_mod_pro_journeys.{str(i)}.hex_id'
            if col_hexid_i not in df.columns:
                continue
            col_days_i = col_days[i]
            col_days_per_i = f'data.freq_mod_pro_journeys.{str(i)}.days_per'

            for idx, row in df.iterrows():
                mode = row.get(col_mode_i)
                days_raw = row.get(col_days_i)
                hex_id = row.get(col_hexid_i)

                # Filter by mode if specified
                if target_mode is not None and mode != target_mode:
                    continue

                if pd.notna(mode) and pd.notna(days_raw) and days_raw > 0 and pd.notna(hex_id):
                    workplace_lat = row.get('data.workplace.lat')
                    workplace_lon = row.get('data.workplace.lon')

                    if pd.notna(workplace_lat) and pd.notna(workplace_lon):
                        # Calculate distance to H3 hex
                        distance_km = self._calculate_distance_to_h3(
                            float(workplace_lat),
                            float(workplace_lon),
                            hex_id,
                            mode
                        )

                        days_per = row.get(col_days_per_i) if col_days_per_i in df.columns else None
                        days = normalize_pro_days_to_yearly(days_raw, days_per)

                        journeys_list.append({
                            'token': row.get('token', idx),
                            'journey_idx': i,
                            'mode': mode,
                            'days': days,
                            'hex_id': hex_id,
                            'workplace_lat': workplace_lat,
                            'workplace_lon': workplace_lon,
                            'distance_km': distance_km
                        })
        
        if len(journeys_list) == 0:
            return None
        
        return pd.DataFrame(journeys_list)

    def _compute_journey_emissions_by_label(self, df: pd.DataFrame, label_prefix: str, apply_reco: bool = False) -> list[Emissions]:
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

        # Label per (token, journey), built the same explicit-suffix way as
        # _reco_inter_columns/_build_reco_weighted in commons.py.
        label_pattern = re.compile(rf'^{re.escape(label_prefix)}\.(\d+)$')
        label_cols = [c for c in df.columns if label_pattern.match(c)]
        rows = []
        for col in label_cols:
            journey_id = label_pattern.match(col).group(1)
            for idx, label in df[col].dropna().items():
                token = df.at[idx, 'token'] if 'token' in df.columns else idx
                rows.append({'token': token, 'journey': journey_id, 'label': label})
        if not rows:
            return []

        merged = journey_df.merge(pd.DataFrame(rows), on=['token', 'journey'], how='inner')

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
        new_reco_rows = []
        for col in self._reco_inter_columns(df):
            journey_id = col.rsplit('.', 1)[1]
            for idx, reco in df[col].dropna().items():
                token = df.at[idx, 'token'] if 'token' in df.columns else idx
                new_reco_rows.append(
                    {'token': token, 'journey': journey_id, 'reco_mode': reco})
        new_reco_df = pd.DataFrame(
            new_reco_rows, columns=['token', 'journey', 'reco_mode'])

        legacy_reco_rows = []
        for col in self._reco_legacy_columns(df):
            for idx, reco in df[col].dropna().items():
                token = df.at[idx, 'token'] if 'token' in df.columns else idx
                legacy_reco_rows.append({'token': token, 'reco_mode': reco})
        legacy_reco_df = pd.DataFrame(
            legacy_reco_rows, columns=['token', 'reco_mode'])

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

        def calc_reco_emissions(row):
            reco_mode = row['reco_mode']
            if pd.isna(reco_mode) or reco_mode not in MODE_EMISSIONS:
                return None

            if row['is_intermodal'] and reco_mode == 'inter':
                # If already intermodal and recommended mode is "inter", keep current emissions
                return row['emissions_dt']

            reco_em = row['dist'] * MODE_EMISSIONS[reco_mode] * row['days'] * 2 * 45 / 1000

            # Only return the recommended emissions if it's a reduction compared to current emissions
            if pd.notna(row['emissions_dt']):
                return min(reco_em, row['emissions_dt'])

            return reco_em

        journey_emissions['reco_emissions'] = journey_emissions.apply(calc_reco_emissions, axis=1)

        # Step 7: Calculate reductions per recommended mode (R lines 223-227)
        journey_emissions['saved_emissions'] = journey_emissions['emissions_dt'] - journey_emissions['reco_emissions']

        return journey_emissions

    def _compute_journey_emission_reductions_by_label(self, df: pd.DataFrame, label_prefix: str) -> list[EmissionReductions]:
        """
        Aggregate potential CO2 emission reductions by each journey's own v3
        typology label (typo.reco.simple_labels.N / typo.reco.complex_labels.N)
        instead of by the recommended mode: "how much could journeys
        currently labeled X save by following their recommendation?"

        Args:
            df: DataFrame of records already filtered to v3
            label_prefix: column prefix without the trailing journey index,
                e.g. 'typo.reco.simple_labels'

        Returns:
            List of EmissionReductions objects (one per observed label)
        """
        journey_emissions = self._build_journey_emission_savings(df)
        if journey_emissions is None:
            return []

        # Label per (token, journey), built the same explicit-suffix way as
        # _compute_journey_emissions_by_label.
        label_pattern = re.compile(rf'^{re.escape(label_prefix)}\.(\d+)$')
        label_cols = [c for c in df.columns if label_pattern.match(c)]
        rows = []
        for col in label_cols:
            journey_id = label_pattern.match(col).group(1)
            for idx, label in df[col].dropna().items():
                token = df.at[idx, 'token'] if 'token' in df.columns else idx
                rows.append({'token': token, 'journey': journey_id, 'label': label})
        if not rows:
            return []

        merged = journey_emissions.merge(pd.DataFrame(rows), on=['token', 'journey'], how='inner')

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
        
        # Dictionary to accumulate savings per recommended mode
        savings_by_reco = {}
        
        # Process each journey index (0, 1, 2, ...)
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

            # Process each row (person)
            for idx, row in df.iterrows():
                current_mode = row.get(col_mode_i)
                reco_mode = row.get(col_reco_i)
                days_raw = row.get(col_days_i)
                hex_id = row.get(col_hexid_i)
                days_per = row.get(col_days_per_i) if col_days_per_i in df.columns else None
                days = normalize_pro_days_to_yearly(days_raw, days_per) if pd.notna(days_raw) else days_raw
                
                # Skip if missing data or no recommendation (per user requirement #3)
                if (pd.isna(current_mode) or 
                    pd.isna(reco_mode) or 
                    pd.isna(days) or 
                    days <= 0 or 
                    pd.isna(hex_id)):
                    continue
                
                # Get workplace coordinates
                workplace_lat = row.get('data.workplace.lat')
                workplace_lon = row.get('data.workplace.lon')
                
                if pd.isna(workplace_lat) or pd.isna(workplace_lon):
                    continue
                
                # Calculate distance to H3 hex (uses existing method)
                distance_km = self._calculate_distance_to_h3(
                    float(workplace_lat),
                    float(workplace_lon),
                    hex_id,
                    current_mode
                )
                
                # Get emission factors with mode name normalization (per user requirement #1)
                current_mode_normalized = self._normalize_mode_value(current_mode)
                reco_mode_normalized = self._normalize_mode_value(reco_mode)
                
                current_emission_factor = MODE_EMISSIONS.get(current_mode_normalized, 0)
                reco_emission_factor = MODE_EMISSIONS.get(reco_mode_normalized, 0)
                
                # Calculate emissions
                # Formula: distance * emission_factor * days * 2 / 1000
                # Note: No * 45 for professional travel (annual frequency, not weekly)
                current_emissions = (
                    distance_km * current_emission_factor * days * 2 / 1000
                )
                reco_emissions = (
                    distance_km * reco_emission_factor * days * 2 / 1000
                )
                
                # Calculate savings (positive = reduction, negative = increase)
                savings = current_emissions - reco_emissions
                
                # Accumulate by recommended mode
                if reco_mode_normalized not in savings_by_reco:
                    savings_by_reco[reco_mode_normalized] = 0.0
                savings_by_reco[reco_mode_normalized] += savings
        
        # Convert to EmissionReductions objects
        results = []
        for mode, reduced in savings_by_reco.items():
            results.append(EmissionReductions(
                mode=mode,
                total=len(df),
                reduced=float(reduced)
            ))
        
        return results

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


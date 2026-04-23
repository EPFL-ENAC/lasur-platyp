import pandas as pd
from api.models.query import EmissionReductions, Emissions
from api.services.stats.commons import BaseStatsService, MODES, MODES_PRO

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

    def compute_modes_emissions(self, apply_reco: bool = False) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records."""

        # v1: count emissions from legacy fields
        df_v1 = self._get_records_v1()
        results_v1 = self._compute_mode_emissions_v1(df_v1, apply_reco)
        results = self._merge_emissions([], results_v1)

        # v2: count emissions from data.freq_mod_journeys
        df_v2 = self._get_records_v2()
        if not df_v2.empty:
            results_v2 = self._compute_mode_emissions_v2(df_v2, apply_reco)
            # merge v1 and v2 results
            for em_v2 in results_v2:
                # find in results the one with same mode
                em_v1 = next(
                    (e for e in results if e.mode == em_v2.mode), None)
                if em_v1 is None:
                    results.append(em_v2)
                else:
                    em_v1.total += em_v2.total
                    em_v1.distances += em_v2.distances
                    em_v1.journeys += em_v2.journeys
                    em_v1.emissions += em_v2.emissions

        # finalize totals
        for emission in results:
            emission.total = len(self.df)
            # round distances, emissions
            emission.distances = round(emission.distances, 3)
            emission.emissions = round(emission.emissions, 3)
        # filter out emissions with zero emissions
        results = [e for e in results if e.emissions > 0]

        return results

    def compute_modes_emission_reductions(self) -> list[EmissionReductions]:
        """Compute all CO2 emission reductions from a DataFrame of records."""
        df_v2 = self._get_records_v2()
        results = []
        if not df_v2.empty:
            for mode in MODES:
                results.extend(
                    self._compute_mode_emission_reductions_v2(df_v2, mode))
        # finalize totals
        for reduction in results:
            reduction.total = len(df_v2)
            # round reduced
            reduction.reduced = round(reduction.reduced, 3)
        # filter out reductions with zero reduced emissions
        results = [e for e in results if e.reduced > 0]
        return results

    def compute_modes_pro_emissions(self, apply_reco: bool = False) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records for pro journeys."""
        # v1: cannot compute pro emissions from v1 data

        # v2: count emissions from data.freq_mod_pro_journeys
        df_v2 = self._get_records_v2()
        results = []
        if not df_v2.empty:
            for mode in MODES_PRO:
                results.extend(
                    self._compute_mode_pro_emissions_v2(df_v2, mode, apply_reco))

        # finalize totals
        for emission in results:
            emission.total = len(df_v2)
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
        df_v2 = self._get_records_v2()
        if df_v2.empty:
            return []
        
        results = self._compute_mode_pro_emission_reductions_v2(
            df_v2, include_negative
        )
        
        # Finalize totals
        for reduction in results:
            reduction.total = len(df_v2)
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
            df: DataFrame with V2 records containing freq_mod_journeys data
            
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
            df: DataFrame with V2 records
            
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
            df: DataFrame with V2 records containing freq_mod_pro_journeys data
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
            
            for idx, row in df.iterrows():
                mode = row.get(col_mode_i)
                days = row.get(col_days_i)
                hex_id = row.get(col_hexid_i)
                
                # Filter by mode if specified
                if target_mode is not None and mode != target_mode:
                    continue
                
                if pd.notna(mode) and pd.notna(days) and days > 0 and pd.notna(hex_id):
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

    #
    # V1 and V2 Emissions Calculations
    #

    def _compute_mode_emissions_v1(self, df: pd.DataFrame, apply_reco: bool = False) -> list[Emissions]:
        """
        Compute all CO2 emissions from a DataFrame of records for V1 data.
        
        Based on R implementation (Untitled.R lines 40-69):
        - For current emissions: Calculate weighted sum of emissions across ALL modes per person,
          then multiply by distance. Return per-mode breakdown.
        - For recommendations: Use total frequency across all modes and apply recommended mode emissions.
        
        Args:
            df: DataFrame with V1 records
            apply_reco: If True, calculate emissions with recommendations applied
            
        Returns:
            List of Emissions objects (one per mode)
        """
        if len(df) == 0:
            return []
        
        # Get available mode columns
        mode_columns = [f'data.freq_mod_{m}' for m in MODES]
        available_mode_cols = [col for col in mode_columns if col in df.columns]
        
        if len(available_mode_cols) == 0:
            return []
        
        if apply_reco:
            # R implementation lines 62-69: Recommendation emissions
            # Calculate freq_all_mod = sum of all mode frequencies
            # Use recommended mode's emissions
            # Formula: MODE_EMISSIONS[reco] / 1000 * dist * 45 * 2 * freq_all_mod
            
            df_reco = df.copy()
            
            # Calculate total frequency across all modes per person
            df_reco['freq_all_mod'] = df_reco[available_mode_cols].fillna(0).sum(axis=1)
            
            # Filter out records with no mode frequencies
            df_reco = df_reco[df_reco['freq_all_mod'] > 0]
            
            if len(df_reco) == 0:
                return []
            
            # Get recommended mode and normalize naming
            if 'typo.reco.reco_dt2.0' not in df_reco.columns:
                return []
            
            df_reco['reco_mode'] = df_reco['typo.reco.reco_dt2.0']
            df_reco = df_reco[df_reco['reco_mode'].notna()]
            
            if len(df_reco) == 0:
                return []
            
            # Normalize mode names
            df_reco['reco_mode'] = self._normalize_mode_name(df_reco, 'reco_mode')
            
            # Map to emissions factors (use em_reco mapping from R)
            em_reco_map = {
                'vae': 11, 'ebike': 11, 'cargo': 11, 'train': 8,
                'tpu': 25, 'pub': 25, 'velo': 6, 'bike': 6,
                'marche': 0, 'walking': 0, 'elec': 90,
                'covoit': 93, 'carpool': 93, 'inter': 56.72391025641025
            }
            df_reco['emissions_factor'] = df_reco['reco_mode'].map(em_reco_map)
            
            # Calculate emissions: emissions / 1000 * dist * 45 * 2 * freq_all_mod
            df_reco['reco_emissions'] = (
                df_reco['emissions_factor'] / 1000 *
                df_reco['distance_km'] * 45 * 2 * df_reco['freq_all_mod']
            )
            
            # Aggregate by recommended mode
            results = []
            for reco_mode in df_reco['reco_mode'].unique():
                if pd.isna(reco_mode):
                    continue
                df_mode = df_reco[df_reco['reco_mode'] == reco_mode]
                results.append(Emissions(
                    mode=reco_mode,
                    total=len(df),
                    distances=float((df_mode['distance_km'] * df_mode['freq_all_mod']).sum()),
                    journeys=int((df_mode['freq_all_mod'] * 45 * 2).sum()),
                    emissions=float(df_mode['reco_emissions'].sum())
                ))
            
            return results
        
        else:
            # R implementation lines 40-56: Current mode emissions
            # Calculate weighted sum: sum(freq_mod_i * emissions_i) for ALL modes per person
            # Then multiply by: distance * 45 * 2 / 1000
            # Return per-mode breakdown
            
            # Step 1: Create long dataframe (pivot longer equivalent)
            records_long = []
            for _, row in df.iterrows():
                for col in available_mode_cols:
                    mode_name = col.replace('data.freq_mod_', '')
                    freq = row[col]
                    if pd.notna(freq) and freq > 0:
                        records_long.append({
                            'token': row.get('token', ''),
                            'mode': mode_name,
                            'freq_mod': freq,
                            'distance_km': row['distance_km'],
                            'emissions_factor': MODE_EMISSIONS.get(mode_name, 0)
                        })
            
            if len(records_long) == 0:
                return []
            
            df_long = pd.DataFrame(records_long)
            
            # Step 2: Calculate weighted sum per person (R line 52)
            # Group by token and calculate sum(emissions * freq_mod)
            df_person = df_long.groupby('token').agg({
                'distance_km': 'first',  # Distance is same for all modes per person
                'freq_mod': lambda x: (df_long.loc[x.index, 'freq_mod'] * df_long.loc[x.index, 'emissions_factor']).sum()
            }).rename(columns={'freq_mod': 'weighted_emissions'})
            
            # Step 3: Calculate total emissions per person (R line 56)
            # initial_emissions = initial_emissions * 45 * 2 * dist / 1000
            df_person['total_emissions'] = (
                df_person['weighted_emissions'] * 
                df_person['distance_km'] * 45 * 2 / 1000
            )
            
            # Step 4: Expand to get per-mode contributions
            # We need to distribute each person's total emissions proportionally to modes
            df_long_with_totals = df_long.merge(
                df_person[['total_emissions', 'weighted_emissions']].reset_index(), 
                on='token'
            )
            
            # Calculate each mode's contribution to the person's total
            df_long_with_totals['mode_contribution'] = (
                df_long_with_totals['freq_mod'] * df_long_with_totals['emissions_factor']
            ) / df_long_with_totals['weighted_emissions']
            
            df_long_with_totals['mode_emissions'] = (
                df_long_with_totals['total_emissions'] * df_long_with_totals['mode_contribution']
            )
            
            # Step 5: Aggregate by mode
            results = []
            for mode_name in df_long_with_totals['mode'].unique():
                df_mode = df_long_with_totals[df_long_with_totals['mode'] == mode_name]
                results.append(Emissions(
                    mode=mode_name,
                    total=len(df),
                    distances=float(df_mode['distance_km'].sum()),
                    journeys=int((df_mode['freq_mod'] * 45 * 2).sum()),
                    emissions=float(df_mode['mode_emissions'].sum())
                ))
            
            return results

    def _compute_mode_emissions_v2(self, df: pd.DataFrame, apply_reco: bool = False) -> list[Emissions]:
        """
        Compute all CO2 emissions from a DataFrame of records for V2 data.
        
        Based on R implementation (Untitled.R lines 74-210):
        - Build journey-level dataframe with proper intermodality detection
        - Calculate mode_fraction based on journey composition (train gets 80% if present)
        - Apply mode_fraction to distance BEFORE emissions calculation
        - For recommendations: use typo.reco.reco_dt2.0 and apply intermodal min logic
        
        Args:
            df: DataFrame with V2 records
            apply_reco: If True, calculate emissions with recommendations applied
            
        Returns:
            List of Emissions objects (one per mode)
        """
        if len(df) == 0:
            return []
        
        # Step 1: Build journey attributes using shared pipeline
        df_combined = self._build_journey_attributes(df)
        if df_combined is None:
            return []
        
        # Step 2: Calculate CO2 emissions for current modes
        df_combined = self._calculate_journey_metrics(df_combined, MODE_EMISSIONS, 'co2')
        # Rename to match existing logic
        df_combined['emissions_dt'] = df_combined['co2_value']
        
        if not apply_reco:
            # Normalize mode names AFTER calculation (to preserve intermodality logic with raw names)
            df_combined['mode_normalized'] = self._normalize_mode_name(df_combined, 'mode')
            
            # Aggregate by normalized mode
            results = []
            for mode_name in df_combined['mode_normalized'].unique():
                df_mode = df_combined[df_combined['mode_normalized'] == mode_name]
                results.append(Emissions(
                    mode=mode_name,
                    total=len(df),
                    distances=float((df_mode['dist_mode'] * df_mode['days'] * 2 * 45).sum()),
                    journeys=int((df_mode.groupby(['token', 'journey'])['days'].first() * 2 * 45).sum()),
                    emissions=float(df_mode['emissions_dt'].sum())
                ))
            
            return results
        
        else:
            # Calculate recommendation emissions (R lines 171-210)
            # Use typo.reco.reco_dt2.0 for v2 records
            
            # Build journeys df for aggregation (need total_days per token)
            journeys_df = self._build_journey_dataframe(df)
            
            # Step 1: Get unique tokens with total_days and recommendation
            token_data = []
            for token in df['token'].unique() if 'token' in df.columns else range(len(df)):
                token_journeys = journeys_df[journeys_df['token'] == token]
                token_combined = df_combined[df_combined['token'] == token]
                
                if 'token' in df.columns:
                    token_row = df[df['token'] == token].iloc[0]
                else:
                    token_row = df.iloc[token]
                
                reco_field = 'typo.reco.reco_dt2.0'
                
                reco_mode = token_row[reco_field]
                if pd.isna(reco_mode):
                    continue
                
                token_data.append({
                    'token': token,
                    'dist': token_row['distance_km'],
                    'total_days': token_journeys['days'].sum(),
                    'reco_mode': reco_mode,
                    'is_intermodal': token_combined['is_intermodal'].any() if len(token_combined) > 0 else False
                })
            
            if len(token_data) == 0:
                return []
            
            reco_df = pd.DataFrame(token_data)
            
            # Step 2: Normalize mode names
            reco_df['reco_mode'] = self._normalize_mode_name(reco_df, 'reco_mode')
            
            # Step 3: Map to emissions factors (use em_reco from R)
            em_reco_map = {
                'vae': 11, 'ebike': 11, 'cargo': 11, 'train': 8,
                'tpu': 25, 'pub': 25, 'velo': 6, 'bike': 6,
                'marche': 0, 'walking': 0, 'elec': 90,
                'covoit': 93, 'carpool': 93, 'inter': 56.72391025641025
            }
            reco_df['emissions_factor'] = reco_df['reco_mode'].map(em_reco_map)
            
            # Step 4: Calculate reco emissions (R line 186)
            # emissions / 1000 * dist * total_days * 2 * 45
            reco_df['reco_emissions'] = (
                reco_df['emissions_factor'] / 1000 *
                reco_df['dist'] * reco_df['total_days'] * 2 * 45
            )
            
            # Step 5: Get current emissions per token
            current_emissions_by_token = df_combined.groupby('token')['emissions_dt'].sum().reset_index()
            current_emissions_by_token = current_emissions_by_token.rename(columns={'emissions_dt': 'current_emissions'})

            reco_df = reco_df.merge(
                current_emissions_by_token,
                on='token',
                how='left'
            )
            reco_df['current_emissions'] = reco_df['current_emissions'].fillna(0)
            
            # Step 6: Apply intermodal logic (R lines 200-209)
            # If is_intermodal AND reco == 'inter': use min(reco_emissions, current_emissions)
            def apply_inter_logic(row):
                if row['is_intermodal'] and row['reco_mode'] == 'inter':
                    return min(row['reco_emissions'], row['current_emissions'])
                return row['reco_emissions']
            
            reco_df['final_emissions'] = reco_df.apply(apply_inter_logic, axis=1)
            
            # Step 7: Aggregate by reco_mode
            results = []
            for reco_mode in reco_df['reco_mode'].unique():
                if pd.isna(reco_mode):
                    continue
                df_mode = reco_df[reco_df['reco_mode'] == reco_mode]
                results.append(Emissions(
                    mode=reco_mode,
                    total=len(df),
                    distances=float((df_mode['dist'] * df_mode['total_days'] * 2 * 45).sum()),
                    journeys=int((df_mode['total_days'] * 2 * 45).sum()),
                    emissions=float(df_mode['final_emissions'].sum())
                ))
            
            return results

    def _compute_mode_emission_reductions_v2(self, df: pd.DataFrame, mode: str) -> list[EmissionReductions]:
        """
        Compute all CO2 emission reductions from a DataFrame of records for V2 data.
        
        Based on R implementation (Untitled.R lines 223-227):
        - Uses the same journey-level logic as _compute_mode_emissions_v2
        - Calculates emissions_dt (current) and reco_emissions (recommended)
        - Returns saved_emissions = emissions_dt - reco_emissions, grouped by recommended mode
        
        Args:
            df: DataFrame with V2 records
            mode: Mode to calculate reductions for (the recommended mode)
            
        Returns:
            List of EmissionReductions objects
        """
        if len(df) == 0:
            return []
        
        # Step 1: Build journey attributes using shared pipeline
        df_combined = self._build_journey_attributes(df)
        if df_combined is None:
            return []
        
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
        
        # Step 4: Get recommendation for each token
        reco_data = []
        for idx, row in df.iterrows():
            token = row.get('token', idx)
            reco_mode = row.get('typo.reco.reco_dt2.0', None)
            
            if pd.notna(reco_mode):
                reco_data.append({
                    'token': token,
                    'reco_mode': reco_mode
                })
        
        if len(reco_data) == 0:
            return []
        
        reco_df = pd.DataFrame(reco_data)
        
        # Normalize mode names
        reco_df['reco_mode'] = self._normalize_mode_name(reco_df, 'reco_mode')
        
        # Step 5: Join recommendations with journey emissions
        journey_emissions = journey_emissions.merge(reco_df, on='token', how='left')

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
        
        # Filter for the specific mode and sum positive reductions
        mode_df = journey_emissions[journey_emissions['reco_mode'] == mode]
        reduction_total = float(mode_df[mode_df['saved_emissions'] > 0]['saved_emissions'].sum())
        
        return [EmissionReductions(
            mode=mode,
            total=len(df),
            reduced=reduction_total
        )]

    def _compute_mode_pro_emission_reductions_v2(
        self, 
        df: pd.DataFrame, 
        include_negative: bool = False
    ) -> list[EmissionReductions]:
        """
        Compute professional travel CO2 emission reductions for V2 data.
        
        Based on viz_v2.ipynb logic (cells 31-32):
        - For each professional journey: calculate current vs reco emissions
        - Accumulate savings per recommended mode
        - Professional journeys use annual frequency (no * 45 multiplier)
        
        Formula per journey:
            current_emissions = distance * MODE_EMISSIONS[current_mode] * days * 2 / 1000
            reco_emissions = distance * MODE_EMISSIONS[reco_mode] * days * 2 / 1000
            savings = current_emissions - reco_emissions
        
        Args:
            df: DataFrame with V2 records
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
                days = row.get(col_days_i)
                hex_id = row.get(col_hexid_i)
                
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

    def _compute_mode_pro_emissions_v2(self, df: pd.DataFrame, mode: str, apply_reco: bool = False) -> list[Emissions]:
        """
        Compute all CO2 emissions from professional travel for a specific mode.
        
        Professional travel is simpler than daily commutes:
        - No intermodality (single mode per journey)
        - Distances calculated to H3 hex locations
        - Uses same emission factors as daily commutes
        
        Args:
            df: DataFrame with V2 records containing freq_mod_pro_journeys data
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

    def _merge_emissions(self, emissions1: list[Emissions], emissions2: list[Emissions]) -> list[Emissions]:
        """Merge each Emissions into a list of Emissions."""
        for em2 in emissions2:
            em1 = next(
                (e for e in emissions1 if e.mode == em2.mode), None)
            if not em1:
                emissions1.append(em2)
                continue
            em = Emissions(
                mode=em1.mode,
                total=em1.total + em2.total,
                distances=em1.distances + em2.distances,
                journeys=em1.journeys + em2.journeys,
                emissions=em1.emissions + em2.emissions
            )
            # replace in emissions1
            for i in range(len(emissions1)):
                if emissions1[i].mode == em.mode:
                    emissions1[i] = em
                    break

        return emissions1

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


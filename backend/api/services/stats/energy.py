import pandas as pd
import numpy as np
from api.models.query import EnergyExpenditure, JourneyEnergyGains, JourneyEnergyGainsByMode, JourneyEnergyLeg, EnergyByJourney, JourneyEnergyStats
from api.services.stats.commons import BaseStatsService, MODES
from pydantic import BaseModel, Field

# MET values (Metabolic Equivalent of Task) in kcal/hr for 70kg average person
# Based on Compendium of Physical Activities: https://pacompendium.com/adult-compendium/
# Values are MET factor * 70kg body weight
MODE_MET = {
    'walking': 3.5 * 70,     # 245 kcal/hr - light walking
    'bike': 8.0 * 70,        # 560 kcal/hr - moderate/vigorous cycling
    'ebike': 6.8 * 70,       # 476 kcal/hr - moderate effort with electric assist
    'pub': 1.3 * 70,         # 91 kcal/hr - sedentary (sitting)
    'moto': 2.8 * 70,        # 196 kcal/hr - light activity
    'carpool': 1.3 * 70,     # 91 kcal/hr - sedentary (passenger)
    'car': 1.3 * 70,         # 91 kcal/hr - sedentary (driver)
    'train': 1.3 * 70,       # 91 kcal/hr - sedentary (sitting)
    'elec': 1.3 * 70,        # 91 kcal/hr - electric car (sedentary)
    # French equivalents
    'marche': 3.5 * 70,      # walking
    'velo': 8.0 * 70,        # bike
    'vae': 6.8 * 70,         # ebike
    'tpu': 1.3 * 70,         # public transport
    'covoit': 1.3 * 70,      # carpool
    # Cargo bike (similar effort to ebike)
    'cargo': 6.8 * 70,
    # Intermodal - calculated dynamically
    'inter': 0.0, # Will be set during initialization
    'other': 2.8 * 70  # Light activity for unclassified modes
}

class EnergyService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        # Calculate distance_km to workplace for each record
        if self.df.empty:
            self.df['distance_km'] = pd.Series(dtype=float)
        else:
            self.df['distance_km'] = self.df.apply(
                self._calculate_distance_home_to_work, axis=1)
        # Calculate dynamic intermodal MET value from dataset
        self._calculate_intermodal_met()

    def _calculate_intermodal_met(self):
        """
        Calculate mean MET for intermodal journeys from the dataset.
        
        This follows the notebook logic (cell 69-70) where intermodal MET
        is computed as the weighted average of MET factors from actual
        intermodal journeys in the data.
        """
        df_v2 = self._get_records_v2()
        
        if df_v2.empty:
            # Fallback to a reasonable average if no V2 data
            MODE_MET['inter'] = 3.0 * 70  # Moderate activity
            return 3.0 * 70
        
        # Build journey attributes to identify intermodal journeys
        df_combined = self._build_journey_attributes(df_v2)
        
        if df_combined is None or df_combined.empty:
            MODE_MET['inter'] = 3.0 * 70
            return 3.0 * 70
        
        # Filter for intermodal journeys only
        df_inter = df_combined[df_combined['is_intermodal']].copy()
        
        if df_inter.empty:
            MODE_MET['inter'] = 3.0 * 70
            return 3.0 * 70
        
        # Calculate time fractions for intermodal journeys
        df_inter = self._calculate_intermodal_time_fractions(df_inter)
        
        # Map MET values to modes
        df_inter['met_value'] = df_inter['mode'].map(MODE_MET).fillna(3.0 * 70)
        
        # Calculate weighted MET: sum of (MET * time_fraction) for each journey
        journey_mets = []
        for (token, journey), group in df_inter.groupby(['token', 'journey']):
            # Weighted average MET for this journey
            weighted_met = (group['met_value'] * group['time_fraction']).sum()
            journey_mets.append(weighted_met)
        
        # Mean of all intermodal journey METs
        if journey_mets:
            mean_inter_met = np.mean(journey_mets)
            MODE_MET['inter'] = round(mean_inter_met, 2)
            return round(mean_inter_met, 2)
        else:
            MODE_MET['inter'] = 3.0 * 70
            return 3.0 * 70

    def compute_modes_energy(self, apply_reco: bool = False) -> list[EnergyExpenditure]:
        """
        Compute aggregated energy expenditure per mode.
        
        Args:
            apply_reco: If True, calculate for recommended modes; otherwise current modes
            
        Returns:
            List of EnergyExpenditure objects, one per mode
        """
        df_v2 = self._get_records_v2()
        results = []
        
        if not df_v2.empty:
            if apply_reco:
                results = self._compute_mode_energy_reco_v2(df_v2)
            else:
                results = self._compute_mode_energy_v2(df_v2)
        
        # Finalize totals and round values
        for energy in results:
            energy.total = len(self.df)
            energy.energy_kcal = round(energy.energy_kcal, 2)
            energy.avg_daily_kcal = round(energy.avg_daily_kcal, 2)
            energy.total_time = round(energy.total_time, 2)
        
        # Filter out modes with zero energy
        results = [e for e in results if e.energy_kcal > 0]
        
        return results

    def compute_journey_energy(self, apply_reco: bool = False) -> EnergyByJourney:
        """
        Compute energy expenditure per journey leg (for stacked barplot).
        
        Args:
            apply_reco: If True, calculate for recommended modes; otherwise current modes
            
        Returns:
            EnergyByJourney object with per-leg breakdown
        """
        df_v2 = self._get_records_v2()
        
        if df_v2.empty:
            return EnergyByJourney(total=len(self.df), data=[])
        
        if apply_reco:
            return self._compute_journey_energy_reco_v2(df_v2)
        else:
            return self._compute_journey_energy_v2(df_v2)
    
    def compute_journey_energy_stats(self) -> JourneyEnergyStats:
        """
        Compute energy for current and recommended modes to calculate gains.
        
        Returns:
            JourneyEnergyStats object with current, recommended, and gain information
        """
        df_v2 = self._get_records_v2()
        
        if df_v2.empty:
            empty_result = EnergyByJourney(total=len(self.df), data=[])
            return JourneyEnergyStats(
                current=empty_result,
                reco=empty_result,
                gains=JourneyEnergyGains(total=0, gains_per_mode=[])
            )
        
        current_energy = self._compute_journey_energy_v2(df_v2)
        reco_energy = self._compute_journey_energy_reco_v2(df_v2)
        
        return JourneyEnergyStats(
            current=current_energy,
            reco=reco_energy,
            gains=self._compute_journey_energy_gains(current_energy, reco_energy)
        )

    #
    # Internal functions
    #

    def _calculate_intermodal_time_fractions(self, combined_df: pd.DataFrame) -> pd.DataFrame:
        """
        Allocate travel time to modes in intermodal journeys.
        
        Logic from notebook (cell 69):
        1. Walking legs: Fixed 10 minutes per leg
        2. Train (if present): start with 50% of remaining time
        3. All non-walking modes: Equal split of remaining time
        
        Args:
            combined_df: DataFrame with journey and mode information
            
        Returns:
            DataFrame with added 'time_fraction' column
        """
        def calc_time_fraction(row):
            if not row['is_intermodal'] and not row.get('is_walking_intermodal', False):
                return 1.0
            
            total_time = row.get('travel_time', 0)
            if total_time == 0:
                return 0.0
            
            # Walking: 10 min per leg
            if row['is_walking']:
                walk_time_min = min(10, total_time)
                return walk_time_min / total_time
            
            # Calculate remaining time after walking legs
            walk_legs = row.get('n_walking', 0)
            walk_total_min = min(walk_legs * 10, total_time)
            remaining_time = total_time - walk_total_min
            
            if remaining_time <= 0:
                return 0.0
            
            remaining_fraction = remaining_time / total_time
            
            non_walk_modes = row.get('n_modes', 1) - row.get('n_walking', 0)
            # Train gets at least 50% of remaining time
            if row.get('has_train', False):

                if row['mode'] == 'train':
                    return remaining_fraction * (0.5 + 0.5 / non_walk_modes)
                else:
                    return remaining_fraction * 0.5 / non_walk_modes
            else:
                return remaining_fraction / non_walk_modes
        
        combined_df['time_fraction'] = combined_df.apply(calc_time_fraction, axis=1)
        return combined_df

    def _calculate_journey_energy(
        self, 
        journey_df: pd.DataFrame, 
        met_factors: dict[str, float],
    ) -> pd.DataFrame:
        """
        Calculate energy expenditure for journeys.
        
        Formula: kcal = MET_value * (travel_time_minutes / 60) * days * 2 / 5
        Where:
        - MET_value: kcal/hr for the mode
        - travel_time/60: converts minutes to hours
        - days: frequency per week
        - * 2: round trip
        - / 5: average per weekday
        
        Args:
            journey_df: DataFrame with journey attributes
            met_factors: Dictionary mapping mode names to MET values
            
        Returns:
            DataFrame with added 'energy_kcal' column
        """
        # Ensure travel_time column exists
        if 'travel_time' not in journey_df.columns:
            journey_df['travel_time'] = 0
        
        journey_df['met_factor'] = journey_df['mode'].map(met_factors).fillna(0)
        
        journey_df['energy_kcal'] = (
            journey_df['met_factor'] *
            journey_df['time_fraction'] *
            journey_df['travel_time'] / 60 *  # minutes to hours
            journey_df['days'] * 2 / 5
        )
        
        return journey_df

    def _compute_mode_energy_v2(self, df: pd.DataFrame) -> list[EnergyExpenditure]:
        """
        Compute energy for current modes (V2 data) - aggregated by mode.
        
        Args:
            df: DataFrame with V2 records
            
        Returns:
            List of EnergyExpenditure objects
        """
        if len(df) == 0:
            return []
        
        # Step 1: Build journey attributes using shared pipeline
        df_combined = self._build_journey_attributes(df)
        if df_combined is None or df_combined.empty:
            return []
        
        # Ensure travel_time column exists
        if 'travel_time' not in df_combined.columns:
            # Try to get from original df
            if 'data.travel_time' in df.columns:
                # Map travel_time from original df to combined df by token
                travel_time_map = df.set_index('token')['data.travel_time'].to_dict()
                df_combined['travel_time'] = df_combined['token'].map(travel_time_map).fillna(0)
            else:
                df_combined['travel_time'] = 0
        
        # Step 2: Calculate time-based fractions for intermodal journeys
        df_combined = self._calculate_intermodal_time_fractions(df_combined)
        
        # Step 3: Calculate energy expenditure
        df_combined = self._calculate_journey_energy(df_combined, MODE_MET)
        
        # Step 4: Normalize mode names
        df_combined['mode_normalized'] = self._normalize_mode_name(df_combined, 'mode')
        
        # Step 5: Aggregate by mode
        results = []
        for mode_name in df_combined['mode_normalized'].unique():
            if pd.isna(mode_name):
                continue
            
            df_mode = df_combined[df_combined['mode_normalized'] == mode_name]
            
            total_energy = float(df_mode['energy_kcal'].sum())
            total_time = float((df_mode['travel_time'] * df_mode['time_fraction'] * df_mode['days'] * 2 * 45 / 5).sum())
            total_journeys = int((df_mode.groupby(['token', 'journey'])['days'].first() * 2 * 45 / 5).sum())
            
            # Calculate average daily kcal per person
            avg_daily = total_energy / len(df) if len(df) > 0 else 0
            
            results.append(EnergyExpenditure(
                mode=mode_name,
                total=len(df),
                total_time=total_time,
                journeys=total_journeys,
                energy_kcal=total_energy,
                avg_daily_kcal=avg_daily
            ))
        
        return results

    def _compute_mode_energy_reco_v2(self, df: pd.DataFrame) -> list[EnergyExpenditure]:
        """
        Compute energy for recommended modes (V2 data) - aggregated by mode.

        Each recommendation is taken into account, weighted by the days of the
        journey(s) it applies to: new-style typo.reco.reco_inter.N is weighted by
        its own matching journey's days, legacy typo.reco.reco_dt2.0/.1 (general
        recommendations, not tied to a specific journey) by the sum of the
        person's journey days.

        Args:
            df: DataFrame with V2 records

        Returns:
            List of EnergyExpenditure objects
        """
        if len(df) == 0:
            return []

        # Ensure travel_time exists in df
        if 'data.travel_time' not in df.columns:
            return []

        # One row per recommendation instance, weighted by its journey(s)' days
        reco_df = self._build_reco_weighted(df)
        if reco_df is None:
            return []

        travel_time_by_token = df.set_index(
            'token')['data.travel_time'] if 'token' in df.columns else pd.Series(dtype=float)
        reco_df['travel_time'] = reco_df['token'].map(
            travel_time_by_token).fillna(0)

        # Normalize mode names
        reco_df['reco_mode'] = self._normalize_mode_name(reco_df, 'reco_mode')

        # Map to MET factors
        reco_df['met_factor'] = reco_df['reco_mode'].map(MODE_MET).fillna(0)

        # Calculate energy: MET * travel_time/60 * days * 2 / 5
        reco_df['energy_kcal'] = (
            reco_df['met_factor'] *
            reco_df['travel_time'] / 60 *
            reco_df['days'] * 2 / 5
        )

        # Aggregate by recommended mode
        results = []
        for reco_mode in reco_df['reco_mode'].unique():
            if pd.isna(reco_mode):
                continue

            df_mode = reco_df[reco_df['reco_mode'] == reco_mode]

            total_energy = float(df_mode['energy_kcal'].sum())
            total_time = float((df_mode['travel_time'] * df_mode['days'] * 2 * 45 / 5).sum())
            total_journeys = int((df_mode['days'] * 2 * 45 / 5).sum())

            # Average daily kcal per person
            avg_daily = total_energy / len(df) if len(df) > 0 else 0

            results.append(EnergyExpenditure(
                mode=reco_mode,
                total=len(df),
                total_time=total_time,
                journeys=total_journeys,
                energy_kcal=total_energy,
                avg_daily_kcal=avg_daily
            ))

        return results

    def _compute_journey_energy_v2(self, df: pd.DataFrame) -> EnergyByJourney:
        """
        Compute energy per journey leg for current modes (for stacked barplot).
        
        Args:
            df: DataFrame with V2 records
            
        Returns:
            EnergyByJourney object with per-leg breakdown
        """
        if len(df) == 0:
            return EnergyByJourney(total=len(df), data=[])
        
        # Build journey attributes
        df_combined = self._build_journey_attributes(df)
        
        if df_combined is None or df_combined.empty:
            return EnergyByJourney(total=len(df), data=[])
        
        # Ensure travel_time column exists
        if 'travel_time' not in df_combined.columns:
            if 'data.travel_time' in df.columns:
                travel_time_map = df.set_index('token')['data.travel_time'].to_dict()
                df_combined['travel_time'] = df_combined['token'].map(travel_time_map).fillna(0)
            else:
                df_combined['travel_time'] = 0
        
        # Calculate time fractions and energy
        df_combined = self._calculate_intermodal_time_fractions(df_combined)
        df_combined = self._calculate_journey_energy(df_combined, MODE_MET)
        df_combined['mode_normalized'] = self._normalize_mode_name(df_combined, 'mode')
        
        # Build journey legs list
        legs = []
        for _, row in df_combined.iterrows():
            energy_kcal = float(row['energy_kcal'])
            
            legs.append(JourneyEnergyLeg(
                token=str(row['token']),
                journey_id=str(row['journey']),
                mode=row['mode_normalized'],
                days=int(row['days']),
                travel_time=float(row['travel_time'] * row['time_fraction']),
                energy_kcal=energy_kcal,
                is_intermodal=bool(row['is_intermodal'])
            ))
        
        energy_grouped_summed = df_combined.groupby('token')['energy_kcal'].sum().reset_index() if not df_combined.empty else None
        average_energy_per_unique_token = energy_grouped_summed['energy_kcal'].mean() if energy_grouped_summed is not None and not energy_grouped_summed.empty else None
        
        return EnergyByJourney(
            total=len(df),
            average_energy_per_unique_token=average_energy_per_unique_token,
            data=legs
        )

    def _compute_journey_energy_reco_v2(self, df: pd.DataFrame) -> EnergyByJourney:
        """
        Compute energy per journey leg for recommended modes (for stacked barplot).

        Creates one synthetic leg per recommendation instance that should be taken
        into account: one per journey for new-style typo.reco.reco_inter.N (weighted
        by that journey's own days), or per legacy typo.reco.reco_dt2.0/.1 general
        recommendation (weighted by the sum of the person's journey days).

        Args:
            df: DataFrame with V2 records

        Returns:
            EnergyByJourney object with per-leg breakdown
        """
        if len(df) == 0:
            return EnergyByJourney(total=len(df), data=[])

        if 'data.travel_time' not in df.columns:
            return EnergyByJourney(total=len(df), data=[])

        reco_df = self._build_reco_weighted(df)
        if reco_df is None:
            return EnergyByJourney(total=len(df), data=[])

        travel_time_by_token = df.set_index(
            'token')['data.travel_time'] if 'token' in df.columns else pd.Series(dtype=float)
        reco_df['travel_time'] = reco_df['token'].map(
            travel_time_by_token).fillna(0)
        reco_df['reco_mode'] = self._normalize_mode_name(reco_df, 'reco_mode')
        reco_df['met_factor'] = reco_df['reco_mode'].map(MODE_MET).fillna(0)
        reco_df['energy_kcal'] = (
            reco_df['met_factor'] * reco_df['travel_time'] / 60 *
            reco_df['days'] * 2 / 5
        )

        legs = [
            JourneyEnergyLeg(
                token=str(row.token),
                journey_id=f"reco_{row.journey}",
                mode=row.reco_mode,
                days=int(row.days),
                travel_time=float(row.travel_time),
                energy_kcal=float(row.energy_kcal),
                is_intermodal=False  # Recommendations are single-mode
            )
            for row in reco_df.itertuples()
        ]

        energy_grouped_summed = reco_df.groupby('token')['energy_kcal'].sum()
        average_energy_per_unique_token = float(
            energy_grouped_summed.mean()) if not energy_grouped_summed.empty else None

        return EnergyByJourney(
            total=len(df),
            average_energy_per_unique_token=average_energy_per_unique_token,
            data=legs
        )
    
    def _compute_journey_energy_gains(self, current: EnergyByJourney, reco: EnergyByJourney) -> JourneyEnergyGains:
        """
        Compute energy gains (reductions) for each mode by comparing current and recommended journeys.

        New-style recommendations (one per journey) are complementary: each is
        compared against that same journey's current energy, and gains are summed
        across journeys. Legacy recommendations (typo.reco.reco_dt2.0/.1) are
        alternatives, not complementary — only the first one is used, compared
        against the person's total current energy, matching how they were
        originally applied.

        Args:
            current: EnergyByJourney for current modes
            reco: EnergyByJourney for recommended modes
        Returns:
            JourneyEnergyGains object with total gain and breakdown by mode
        """

        who_recommendation = 150

        legs_by_token = {}
        for leg in current.data:
            if leg.token not in legs_by_token:
                legs_by_token[leg.token] = LegPerToken(token=leg.token)
            legs_by_token[leg.token].current_legs.append(leg)

        for leg in reco.data:
            if leg.token not in legs_by_token:
                legs_by_token[leg.token] = LegPerToken(token=leg.token)
            legs_by_token[leg.token].reco_legs.append(leg)

        current_above_who_count = sum(1 for leg in legs_by_token.values() if leg.current_energy() >= who_recommendation)
        reco_above_who_count = sum(1 for leg in legs_by_token.values() if leg.reco_energy() >= who_recommendation)

        gains_per_mode_dict = {}
        for lpt in legs_by_token.values():
            journey_legs = [l for l in lpt.reco_legs if not l.journey_id.startswith('reco_legacy_')]
            if journey_legs:
                for reco_leg in journey_legs:
                    journey_id = reco_leg.journey_id[len('reco_'):]
                    baseline = lpt.current_energy_for_journey(journey_id)
                    gain = reco_leg.energy_kcal - baseline
                    gains_per_mode_dict[reco_leg.mode] = gains_per_mode_dict.get(reco_leg.mode, 0) + gain
            elif lpt.reco_legs:
                reco_leg = lpt.reco_legs[0]
                gain = reco_leg.energy_kcal - lpt.current_energy()
                gains_per_mode_dict[reco_leg.mode] = gains_per_mode_dict.get(reco_leg.mode, 0) + gain

        gains_per_mode = [JourneyEnergyGainsByMode(mode=mode, added_kcal=gain) for mode, gain in gains_per_mode_dict.items()]

        total_gain = sum(g.added_kcal for g in gains_per_mode)

        return JourneyEnergyGains(
            total=total_gain,
            gains_per_mode=gains_per_mode,
            current_above_who_count=current_above_who_count,
            reco_above_who_count=reco_above_who_count
        )


class LegPerToken(BaseModel):
    token: str
    current_legs: list[JourneyEnergyLeg] = Field(default_factory=list)
    # New-style: one leg per journey (complementary). Legacy: up to two
    # alternative general recommendations (typo.reco.reco_dt2.0/.1).
    reco_legs: list[JourneyEnergyLeg] = Field(default_factory=list)

    def current_energy(self):
        return sum(leg.energy_kcal for leg in self.current_legs)

    def current_energy_for_journey(self, journey_id: str):
        return sum(leg.energy_kcal for leg in self.current_legs if leg.journey_id == journey_id)

    def reco_energy(self):
        journey_legs = [l for l in self.reco_legs if not l.journey_id.startswith('reco_legacy_')]
        if journey_legs:
            return sum(leg.energy_kcal for leg in journey_legs)
        if self.reco_legs:
            return self.reco_legs[0].energy_kcal
        return 0

    def gain(self):
        return self.reco_energy() - self.current_energy()

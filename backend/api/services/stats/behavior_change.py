from typing import List, Dict, Tuple
import pandas as pd
from api.models.query import (
    BehaviorChangeByModeLever, BehaviorChangeByModeMotivation, BehaviorChangeStats,
    BehaviorChangeLever, BehaviorChangeMotivation, BehaviorChangeStatsLever, BehaviorChangeStatsMotivation
)
from api.services.stats.commons import BaseStatsService


class BehaviorChangeService(BaseStatsService):
    """Service for computing behavior change statistics (motivation and levers)."""
    
    LEVER_CATEGORIES = ['finance', 'flexibility', 'collective', 'environment', 'other']    
    MOTIVATION_LEVELS = [5, 4, 3, 2, 1]
    
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.reco_col = 'typo.reco.reco_dt2.0'
    
    def compute_behavior_change_stats(self) -> BehaviorChangeStats:
        """Main entry point for computing behavior change statistics."""
        
        # Filter to rows with valid recommendation
        df_filtered = self._filter_valid_data()
        
        if len(df_filtered) == 0:
            return BehaviorChangeStats(
                levers=BehaviorChangeStatsLever(by_mode_levers=[], total_responses=0, aggregation_type='all_aggregated'),
                motivation=BehaviorChangeStatsMotivation(by_mode_motivation=[], total_responses=0, aggregation_type='all_aggregated'),
                other_levers=[]
            )
        
        # Count actual responses per mode (not just recommendations)
        lever_counts_per_mode = self._count_lever_responses_per_mode(df_filtered)
        motivation_counts_per_mode = self._count_motivation_responses_per_mode(df_filtered)
        
        total_lever_responses = sum(lever_counts_per_mode.values())
        total_motivation_responses = sum(motivation_counts_per_mode.values())
        
        # Determine unified aggregation strategy based on EITHER metric reaching threshold
        agg_type, mode_groups = self._determine_unified_aggregation_strategy(
            df_filtered, lever_counts_per_mode, motivation_counts_per_mode
        )
        
        # Compute stats for each metric using the unified aggregation
        by_mode_levers = self._compute_mode_stats_for_levers(
            df_filtered, mode_groups, agg_type
        )
        by_mode_motivation = self._compute_mode_stats_for_motivation(
            df_filtered, mode_groups, agg_type
        )
        
        # Extract all other_levers text responses
        other_levers = self._extract_other_levers(df_filtered)
        
        return BehaviorChangeStats(
            levers=BehaviorChangeStatsLever(
                by_mode_levers=by_mode_levers,
                total_responses=total_lever_responses,
                aggregation_type=agg_type
            ),
            motivation=BehaviorChangeStatsMotivation(
                by_mode_motivation=by_mode_motivation,
                total_responses=total_motivation_responses,
                aggregation_type=agg_type
            ),
            other_levers=other_levers
        )
    
    def _filter_valid_data(self) -> pd.DataFrame:
        """Filter to rows with valid recommendation."""
        if self.reco_col not in self.df.columns:
            return pd.DataFrame()
        return self.df[self.df[self.reco_col].notna()].copy()
    
    def _count_lever_responses_per_mode(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Count how many people per mode answered at least one lever question.
        
        Returns:
            Dict mapping mode name to count of people who answered lever questions
        """
        lever_cols = [col for col in df.columns if col.startswith('data.change.levers.')]
        
        if not lever_cols:
            return {}
        
        # For each row, check if they answered at least one lever question
        def has_lever_response(row):
            for col in lever_cols:
                val = row[col]
                if pd.notna(val) and val != '' and val != 0.0 and val != '0.0':
                    return True
            return False
        
        df_with_lever = df[df.apply(has_lever_response, axis=1)]
        
        if len(df_with_lever) == 0:
            return {}
        
        return df_with_lever[self.reco_col].value_counts().to_dict()
    
    def _count_motivation_responses_per_mode(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Count how many people per mode answered the motivation question.
        
        Returns:
            Dict mapping mode name to count of people who answered motivation
        """
        if 'data.change.motivation' not in df.columns:
            return {}
        
        motivation_series = df['data.change.motivation']
        # Filter out empty values
        mask = motivation_series.notna() & (motivation_series != 0.0)
        df_with_motivation = df[mask]
        
        if len(df_with_motivation) == 0:
            return {}
        
        return df_with_motivation[self.reco_col].value_counts().to_dict()
    
    def _determine_unified_aggregation_strategy(
        self,
        df: pd.DataFrame,
        lever_counts: Dict[str, int],
        motivation_counts: Dict[str, int]
    ) -> Tuple[str, Dict[str, pd.DataFrame]]:
        """
        Determine unified aggregation strategy based on EITHER metric reaching threshold.
        
        A mode is shown individually if it has >=10 responses for EITHER levers OR motivation.
        
        Args:
            df: Full dataframe
            lever_counts: Dict of mode -> lever response count
            motivation_counts: Dict of mode -> motivation response count
        
        Returns:
            aggregation_type: 'all_aggregated', 'mode_split', or 'mixed'
            mode_groups: dict mapping mode name to filtered dataframe
        """
        # Combine all modes that appear in either count dict
        all_modes = set(lever_counts.keys()) | set(motivation_counts.keys())
        
        if not all_modes:
            return 'all_aggregated', {'allModes': df}
        
        # Calculate total responses (use max to avoid double-counting)
        total_lever = sum(lever_counts.values())
        total_motivation = sum(motivation_counts.values())
        total_responses = max(total_lever, total_motivation)
        
        # Case 1: Less than 10 total responses in either metric - aggregate everything
        if total_responses < 10:
            return 'all_aggregated', {'allModes': df}
        
        # Case 2: Check which modes meet threshold (>=10 in EITHER metric)
        modes_above_threshold = {}
        for mode in all_modes:
            lever_count = lever_counts.get(mode, 0)
            motivation_count = motivation_counts.get(mode, 0)
            # Mode qualifies if EITHER metric has >=10 responses
            if lever_count >= 10 or motivation_count >= 10:
                modes_above_threshold[mode] = max(lever_count, motivation_count)
        
        if len(modes_above_threshold) == 0:
            # No individual mode has 10+ responses in either metric
            return 'all_aggregated', {'allModes': df}
        
        # Case 3: Mixed - some modes above, some below threshold
        mode_groups = {}
        
        # Add individual modes with >= 10 responses in either metric
        for mode in modes_above_threshold.keys():
            mode_groups[mode] = df[df[self.reco_col] == mode]
        
        # Aggregate remaining modes into "Autres"
        modes_below = all_modes - set(modes_above_threshold.keys())
        if len(modes_below) > 0:
            other_df = df[df[self.reco_col].isin(list(modes_below))]
            mode_groups['Autres'] = other_df
        
        return 'mixed', mode_groups
    
    def _determine_aggregation_strategy(
        self, df: pd.DataFrame, mode_counts: Dict[str, int]
    ) -> Tuple[str, Dict[str, pd.DataFrame]]:
        """
        Determine how to aggregate data based on response counts.
        
        Args:
            df: Full dataframe
            mode_counts: Dict of mode -> response count for this metric
        
        Returns:
            aggregation_type: 'all_aggregated', 'mode_split', or 'mixed'
            mode_groups: dict mapping mode name to filtered dataframe
        """
        if not mode_counts:
            return 'all_aggregated', {'allModes': df}
        
        total = sum(mode_counts.values())
        
        # Case 1: Less than 10 total responses - aggregate everything
        if total < 10:
            return 'all_aggregated', {'allModes': df}
        
        # Case 2: At least 10 responses total
        modes_above_threshold = {mode: count for mode, count in mode_counts.items() if count >= 10}
        
        if len(modes_above_threshold) == 0:
            # No individual mode has 10+ responses
            return 'all_aggregated', {'allModes': df}
        
        # Case 3: Mixed - some modes above, some below threshold
        mode_groups = {}
        
        # Add individual modes with >= 10 responses
        for mode in modes_above_threshold.keys():
            mode_groups[mode] = df[df[self.reco_col] == mode]
        
        # Aggregate remaining modes into "Autres"
        modes_below = [mode for mode, count in mode_counts.items() if count < 10]
        if len(modes_below) > 0:
            other_df = df[df[self.reco_col].isin(modes_below)]
            mode_groups['Autres'] = other_df
        
        return 'mixed', mode_groups
    
    def _compute_mode_stats_for_levers(
        self, df: pd.DataFrame, mode_groups: Dict[str, pd.DataFrame], agg_type: str
    ) -> List[BehaviorChangeByModeLever]:
        """Compute lever statistics for each mode group."""
        
        by_mode = []
        for mode_name, mode_df in mode_groups.items():
            levers, response_count = self._compute_levers(mode_df)
            by_mode.append(BehaviorChangeByModeLever(
                mode=mode_name,
                response_count=response_count,
                levers=levers,
            ))
        
        # Add Total summary if we're splitting by mode
        if agg_type in ['mode_split', 'mixed']:
            levers, response_count = self._compute_levers(df)
            by_mode.append(BehaviorChangeByModeLever(
                mode='Total',
                response_count=response_count,
                levers=levers,
            ))
        
        return by_mode
    
    def _compute_mode_stats_for_motivation(
        self, df: pd.DataFrame, mode_groups: Dict[str, pd.DataFrame], agg_type: str
    ) -> List[BehaviorChangeByModeMotivation]:
        """Compute motivation statistics for each mode group."""
        by_mode = []
        for mode_name, mode_df in mode_groups.items():
            motivations, response_count = self._compute_motivation(mode_df)
            by_mode.append(BehaviorChangeByModeMotivation(
                mode=mode_name,
                response_count=response_count,
                motivations=motivations
            ))
        
        # Add Total summary if we're splitting by mode
        if agg_type in ['mode_split', 'mixed']:
            motivations, response_count = self._compute_motivation(df)
            by_mode.append(BehaviorChangeByModeMotivation(
                mode='Total',
                response_count=response_count,
                motivations=motivations
            ))
        
        return by_mode
    
    def _compute_levers(
        self, df: pd.DataFrame
    ) -> Tuple[List[BehaviorChangeLever], int]:
        """
        Extract and count lever categories from data.change.levers columns.
        
        Returns:
            levers: List of BehaviorChangeLever objects
            response_count: Number of people who answered at least one lever question
        """
        lever_cols = [col for col in df.columns if col.startswith('data.change.levers.')]
        
        # Count unique people who answered at least one lever
        def has_lever_response(row):
            for col in lever_cols:
                val = row[col]
                if pd.notna(val) and val != '' and val != 0.0 and val != '0.0':
                    return True
            return False
        
        people_with_levers = df[df.apply(has_lever_response, axis=1)]
        response_count = len(people_with_levers)
        
        # Collect all lever selections for percentages
        all_levers = []
        for col in lever_cols:
            selections = df[col].dropna()
            # Filter out 0.0 values (empty placeholders)
            selections = selections[selections != '0.0']
            selections = selections[selections != 0.0]
            selections = selections[selections != '']
            all_levers.extend(selections.tolist())
        
        if len(all_levers) == 0:
            # No lever data - return empty list with 0 counts
            return [
                BehaviorChangeLever(
                    category=cat,
                    count=0,
                    percentage=0.0
                )
                for cat in self.LEVER_CATEGORIES
            ], 0
        
        lever_counts = pd.Series(all_levers).value_counts()
        total = len(all_levers)
        
        levers = []
        for category in self.LEVER_CATEGORIES:
            count = lever_counts.get(category, 0)
            percentage = round((count / total * 100), 2) if total > 0 else 0.0
            levers.append(BehaviorChangeLever(
                category=category,
                count=int(count),
                percentage=percentage
            ))
        
        return levers, response_count
    
    def _compute_motivation(
        self, df: pd.DataFrame
    ) -> Tuple[List[BehaviorChangeMotivation], int]:
        """
        Extract and count motivation levels from data.change.motivation.
        
        Returns:
            motivation: List of BehaviorChangeMotivation objects
            response_count: Number of people who answered the motivation question
        """
        if 'data.change.motivation' not in df.columns:
            return [
                BehaviorChangeMotivation(
                    level=level,
                    count=0,
                    percentage=0.0
                )
                for level in self.MOTIVATION_LEVELS
            ], 0
        
        motivation_series = df['data.change.motivation'].dropna()
        # Filter out 0.0 values (empty placeholders)
        motivation_series = motivation_series[motivation_series != 0.0]
        
        response_count = len(motivation_series)
        
        if response_count == 0:
            return [
                BehaviorChangeMotivation(
                    level=level,
                    count=0,
                    percentage=0.0
                )
                for level in self.MOTIVATION_LEVELS
            ], 0
        
        motivation_series = motivation_series.astype(int)
        motivation_counts = motivation_series.value_counts()
        
        motivation_list = []
        for level in self.MOTIVATION_LEVELS:
            count = motivation_counts.get(level, 0)
            percentage = round((count / response_count * 100), 2) if response_count > 0 else 0.0
            motivation_list.append(BehaviorChangeMotivation(
                level=level,
                count=int(count),
                percentage=percentage
            ))
        
        return motivation_list, response_count
    
    def _extract_other_levers(self, df: pd.DataFrame) -> List[str]:
        """Extract free-text responses from data.change.other_levers."""
        if 'data.change.other_levers' not in df.columns:
            return []
        
        other_levers = df['data.change.other_levers'].dropna()
        # Filter out empty strings
        other_levers = other_levers[other_levers != '']
        return other_levers.tolist()

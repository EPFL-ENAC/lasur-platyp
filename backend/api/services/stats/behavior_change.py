from typing import List, Dict, Tuple
import pandas as pd
from api.models.query import (
    BehaviorChangeStats, BehaviorChangeByMode,
    BehaviorChangeLever, BehaviorChangeMotivation
)
from api.services.stats.commons import BaseStatsService


class BehaviorChangeService(BaseStatsService):
    """Service for computing behavior change statistics (motivation and levers)."""
    
    # Lever categories and their French labels
    LEVER_CATEGORIES = ['finance', 'flexibility', 'collective', 'environment', 'other']
    LEVER_LABELS = {
        'finance': 'Aide financière',
        'flexibility': 'Flexibilité',
        'collective': 'Changement collectif',
        'environment': 'Aménagement environnement',
        'other': 'Autre'
    }
    
    # Motivation levels and French labels (in reverse order like notebook)
    MOTIVATION_LEVELS = [5, 4, 3, 2, 1]
    MOTIVATION_LABELS = {
        1: 'Pas intéressé·e',
        2: 'Plutôt pas',
        3: 'Neutre',
        4: 'Plutôt motivé·e',
        5: 'Très motivé·e'
    }
    
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.reco_col = 'typo.reco.reco_dt2.0'
    
    def compute_behavior_change_stats(self) -> BehaviorChangeStats:
        """Main entry point for computing behavior change statistics."""
        
        # Filter to rows with valid recommendation
        df_filtered = self._filter_valid_data()
        
        if len(df_filtered) == 0:
            return BehaviorChangeStats(
                total_responses=0,
                aggregation_type='all_aggregated',
                by_mode=[]
            )
        
        total_responses = len(df_filtered)
        
        # Determine aggregation strategy based on the 10-answer threshold
        aggregation_type, mode_groups = self._determine_aggregation_strategy(df_filtered)
        
        # Compute stats for each group
        by_mode = []
        for mode_name, mode_df in mode_groups.items():
            by_mode.append(self._compute_mode_stats(mode_name, mode_df))
        
        # Add total summary if we're splitting by mode
        if aggregation_type in ['mode_split', 'mixed']:
            by_mode.append(self._compute_mode_stats('Total', df_filtered))
        
        return BehaviorChangeStats(
            total_responses=total_responses,
            aggregation_type=aggregation_type,
            by_mode=by_mode
        )
    
    def _filter_valid_data(self) -> pd.DataFrame:
        """Filter to rows with valid recommendation (already done by preprocessing)."""
        if self.reco_col not in self.df.columns:
            return pd.DataFrame()
        return self.df[self.df[self.reco_col].notna()].copy()
    
    def _determine_aggregation_strategy(
        self, df: pd.DataFrame
    ) -> Tuple[str, Dict[str, pd.DataFrame]]:
        """
        Determine how to aggregate the data based on response counts.
        
        Returns:
            aggregation_type: 'all_aggregated', 'mode_split', or 'mixed'
            mode_groups: dict mapping mode name to filtered dataframe
        """
        mode_counts = df[self.reco_col].value_counts()
        total = len(df)
        
        # Case 1: Less than 10 total responses - aggregate everything
        if total < 10:
            return 'all_aggregated', {'Tous modes': df}
        
        # Case 2: At least 10 responses total
        modes_above_threshold = mode_counts[mode_counts >= 10]
        
        if len(modes_above_threshold) == 0:
            # No individual mode has 10+ responses
            return 'all_aggregated', {'Tous modes': df}
        
        # Case 3: Mixed - some modes above, some below threshold
        mode_groups = {}
        
        # Add individual modes with >= 10 responses
        for mode in modes_above_threshold.index:
            mode_groups[mode] = df[df[self.reco_col] == mode]
        
        # Aggregate remaining modes into "Autres"
        modes_below = mode_counts[mode_counts < 10].index
        if len(modes_below) > 0:
            other_df = df[df[self.reco_col].isin(modes_below)]
            mode_groups['Autres'] = other_df
        
        return 'mixed', mode_groups
    
    def _compute_mode_stats(
        self, mode_name: str, df: pd.DataFrame
    ) -> BehaviorChangeByMode:
        """Compute behavior change stats for a given mode/group."""
        
        levers, levers_responses = self._compute_levers(df)
        motivation, motivation_responses = self._compute_motivation(df)
        other_levers = self._extract_other_levers(df)
        
        return BehaviorChangeByMode(
            mode=mode_name,
            total_responses=len(df),
            motivation_responses=motivation_responses,
            levers_responses=levers_responses,
            levers=levers,
            motivation=motivation,
            other_levers=other_levers
        )
    
    def _compute_levers(
        self, df: pd.DataFrame
    ) -> Tuple[List[BehaviorChangeLever], int]:
        """
        Extract and count lever categories from data.change.levers columns.
        
        Returns:
            levers: List of BehaviorChangeLever objects
            total_selections: Total number of lever selections (not unique responses)
        """
        lever_cols = [col for col in df.columns if col.startswith('data.change.levers.')]
        
        # Collect all lever selections
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
                    label=self.LEVER_LABELS[cat],
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
                label=self.LEVER_LABELS[category],
                count=int(count),
                percentage=percentage
            ))
        
        return levers, total
    
    def _compute_motivation(
        self, df: pd.DataFrame
    ) -> Tuple[List[BehaviorChangeMotivation], int]:
        """
        Extract and count motivation levels from data.change.motivation.
        
        Returns:
            motivation: List of BehaviorChangeMotivation objects
            total_responses: Total number of motivation responses
        """
        if 'data.change.motivation' not in df.columns:
            return [
                BehaviorChangeMotivation(
                    level=level,
                    label=self.MOTIVATION_LABELS[level],
                    count=0,
                    percentage=0.0
                )
                for level in self.MOTIVATION_LEVELS
            ], 0
        
        motivation_series = df['data.change.motivation'].dropna()
        # Filter out 0.0 values (empty placeholders)
        motivation_series = motivation_series[motivation_series != 0.0]
        
        if len(motivation_series) == 0:
            return [
                BehaviorChangeMotivation(
                    level=level,
                    label=self.MOTIVATION_LABELS[level],
                    count=0,
                    percentage=0.0
                )
                for level in self.MOTIVATION_LEVELS
            ], 0
        
        motivation_series = motivation_series.astype(int)
        motivation_counts = motivation_series.value_counts()
        total = len(motivation_series)
        
        motivation_list = []
        for level in self.MOTIVATION_LEVELS:
            count = motivation_counts.get(level, 0)
            percentage = round((count / total * 100), 2) if total > 0 else 0.0
            motivation_list.append(BehaviorChangeMotivation(
                level=level,
                label=self.MOTIVATION_LABELS[level],
                count=int(count),
                percentage=percentage
            ))
        
        return motivation_list, total
    
    def _extract_other_levers(self, df: pd.DataFrame) -> List[str]:
        """Extract free-text responses from data.change.other_levers."""
        if 'data.change.other_levers' not in df.columns:
            return []
        
        other_levers = df['data.change.other_levers'].dropna()
        # Filter out empty strings
        other_levers = other_levers[other_levers != '']
        return other_levers.tolist()

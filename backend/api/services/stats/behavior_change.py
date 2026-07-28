import re
from typing import List, Dict, Tuple
import pandas as pd
from api.models.query import (
    BehaviorChangeByModeLever, BehaviorChangeByModeMotivation, BehaviorChangeStats,
    BehaviorChangeLever, BehaviorChangeMotivation, BehaviorChangeStatsLever, BehaviorChangeStatsMotivation
)
from api.services.stats.commons import BaseStatsService


class BehaviorChangeService(BaseStatsService):
    """Service for computing behavior change statistics (motivation and levers)."""

    LEVER_CATEGORIES = ['finance', 'flexibility',
                        'collective', 'environment', 'other']
    MOTIVATION_LEVELS = [5, 4, 3, 2, 1]

    # Older records stored a single `change` object, then a `change`/`change2` pair,
    # instead of a `changes` array (one entry per recommendation). Map them onto the
    # equivalent `changes` indices so they feed into the same aggregation.
    LEGACY_CHANGE_PREFIXES = {'data.change.': 0, 'data.change2.': 1}

    # Older records stored up to two general recommendations in reco_dt2.0/.1,
    # not tied to a specific journey, instead of one reco_inter.N per journey.
    # Map them onto the equivalent reco_inter indices so they feed into the same
    # aggregation.
    LEGACY_RECO_COLUMNS = {
        'typo.reco.reco_dt2.0': 0, 'typo.reco.reco_dt2.1': 1}

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        self.reco_prefix = 'typo.reco.reco_inter.'
        self.change_prefix = 'data.changes.'

    def compute_behavior_change_stats(self) -> BehaviorChangeStats:
        """Main entry point for computing behavior change statistics."""

        # Reshape to one row per (person, recommendation index) pair, so any number
        # of recommendations/changes can be aggregated per mode.
        df_long = self._build_long_dataframe()

        if len(df_long) == 0:
            return BehaviorChangeStats(
                levers=BehaviorChangeStatsLever(
                    by_mode_levers=[], total_responses=0, aggregation_type='all_aggregated'),
                motivation=BehaviorChangeStatsMotivation(
                    by_mode_motivation=[], total_responses=0, aggregation_type='all_aggregated'),
                other_levers=[]
            )

        # Count actual responses per mode (not just recommendations)
        lever_counts_per_mode = self._count_lever_responses_per_mode(df_long)
        motivation_counts_per_mode = self._count_motivation_responses_per_mode(
            df_long)

        total_lever_responses = sum(lever_counts_per_mode.values())
        total_motivation_responses = sum(motivation_counts_per_mode.values())

        # Determine unified aggregation strategy based on EITHER metric reaching threshold
        agg_type, mode_groups = self._determine_unified_aggregation_strategy(
            df_long, lever_counts_per_mode, motivation_counts_per_mode
        )

        # Compute stats for each metric using the unified aggregation
        by_mode_levers = self._compute_mode_stats_for_levers(
            df_long, mode_groups, agg_type
        )
        by_mode_motivation = self._compute_mode_stats_for_motivation(
            df_long, mode_groups, agg_type
        )

        # Extract all other_levers text responses
        other_levers = self._extract_other_levers(df_long)

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

    def _normalize_legacy_change_columns(self) -> pd.DataFrame:
        """Map legacy `data.change` / `data.change2` columns onto `data.changes.0.*` /
        `data.changes.1.*`, so both old and new record shapes feed into the same
        per-index aggregation."""
        df = self.df.copy()
        for legacy_prefix, index in self.LEGACY_CHANGE_PREFIXES.items():
            for col in list(df.columns):
                if not col.startswith(legacy_prefix):
                    continue
                new_col = f'{self.change_prefix}{index}.{col[len(legacy_prefix):]}'
                if new_col in df.columns:
                    df[new_col] = df[new_col].combine_first(df[col])
                else:
                    df[new_col] = df[col]
        return df

    def _normalize_legacy_reco_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map legacy `typo.reco.reco_dt2.0` / `.1` onto `typo.reco.reco_inter.0` /
        `.1`, so both old and new recommendation shapes feed into the same
        per-index aggregation."""
        df = df.copy()
        for legacy_col, index in self.LEGACY_RECO_COLUMNS.items():
            if legacy_col not in df.columns:
                continue
            new_col = f'{self.reco_prefix}{index}'
            if new_col in df.columns:
                df[new_col] = df[new_col].combine_first(df[legacy_col])
            else:
                df[new_col] = df[legacy_col]
        return df

    def _reco_indices(self, df: pd.DataFrame) -> List[int]:
        """Indices of recommendations present in the DataFrame, from either the
        reco_dt2 or the changes columns."""
        indices = set()
        reco_pattern = re.compile(rf'^{re.escape(self.reco_prefix)}(\d+)$')
        change_pattern = re.compile(
            rf'^{re.escape(self.change_prefix)}(\d+)\.')
        for col in df.columns:
            m = reco_pattern.match(col) or change_pattern.match(col)
            if m:
                indices.add(int(m.group(1)))
        return sorted(indices)

    def _lever_indices(self, df: pd.DataFrame) -> List[int]:
        """Indices of the lever choice columns (data.changes.<i>.levers.<j>)."""
        pattern = re.compile(
            rf'^{re.escape(self.change_prefix)}\d+\.levers\.(\d+)$')
        indices = {int(m.group(1))
                   for col in df.columns for m in [pattern.match(col)] if m}
        return sorted(indices)

    def _build_long_dataframe(self) -> pd.DataFrame:
        """
        Reshape the wide per-record DataFrame into one row per (person, recommendation
        index) pair: 'reco_mode', 'motivation', 'levers.<j>', 'other_levers'. Only
        rows with an actual recommended mode at that index are kept.
        """
        df = self._normalize_legacy_change_columns()
        df = self._normalize_legacy_reco_columns(df)
        indices = self._reco_indices(df)
        if not indices:
            return pd.DataFrame(columns=['reco_mode'])

        lever_indices = self._lever_indices(df)

        frames = []
        for i in indices:
            reco_col = f'{self.reco_prefix}{i}'
            if reco_col not in df.columns:
                continue
            empty_col = pd.Series(pd.NA, index=df.index, dtype=object)
            part = pd.DataFrame({'reco_mode': df[reco_col]})
            motivation_col = f'{self.change_prefix}{i}.motivation'
            part['motivation'] = df[motivation_col] if motivation_col in df.columns else empty_col
            for j in lever_indices:
                lever_col = f'{self.change_prefix}{i}.levers.{j}'
                part[f'levers.{j}'] = df[lever_col] if lever_col in df.columns else empty_col
            other_col = f'{self.change_prefix}{i}.other_levers'
            part['other_levers'] = df[other_col] if other_col in df.columns else empty_col
            part = part[part['reco_mode'].notna()]
            if len(part) > 0:
                frames.append(part)

        if not frames:
            return pd.DataFrame(columns=['reco_mode'])
        return pd.concat(frames, ignore_index=True)

    def _count_lever_responses_per_mode(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Count how many people per mode answered at least one lever question.

        Returns:
            Dict mapping mode name to count of people who answered lever questions
        """
        lever_cols = [col for col in df.columns if col.startswith('levers.')]

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

        return df_with_lever['reco_mode'].value_counts().to_dict()

    def _count_motivation_responses_per_mode(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Count how many people per mode answered the motivation question.

        Returns:
            Dict mapping mode name to count of people who answered motivation
        """
        if 'motivation' not in df.columns:
            return {}

        motivation_series = df['motivation']
        # Filter out empty values
        mask = motivation_series.notna() & (motivation_series != 0.0)
        df_with_motivation = df[mask]

        if len(df_with_motivation) == 0:
            return {}

        return df_with_motivation['reco_mode'].value_counts().to_dict()

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
                modes_above_threshold[mode] = max(
                    lever_count, motivation_count)

        if len(modes_above_threshold) == 0:
            # No individual mode has 10+ responses in either metric
            return 'all_aggregated', {'allModes': df}

        # Case 3: Mixed - some modes above, some below threshold
        mode_groups = {}

        # Add individual modes with >= 10 responses in either metric
        for mode in modes_above_threshold.keys():
            mode_groups[mode] = df[df['reco_mode'] == mode]

        # Aggregate remaining modes into "Autres"
        modes_below = all_modes - set(modes_above_threshold.keys())
        if len(modes_below) > 0:
            other_df = df[df['reco_mode'].isin(list(modes_below))]
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
        Extract and count lever categories from levers.* columns.

        Returns:
            levers: List of BehaviorChangeLever objects
            response_count: Number of people who answered at least one lever question
        """
        lever_cols = [col for col in df.columns if col.startswith('levers.')]

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
        Extract and count motivation levels from the motivation column.

        Returns:
            motivation: List of BehaviorChangeMotivation objects
            response_count: Number of people who answered the motivation question
        """
        if 'motivation' not in df.columns:
            return [
                BehaviorChangeMotivation(
                    level=level,
                    count=0,
                    percentage=0.0
                )
                for level in self.MOTIVATION_LEVELS
            ], 0

        motivation_series = df['motivation'].dropna()
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
            percentage = round((count / response_count * 100),
                               2) if response_count > 0 else 0.0
            motivation_list.append(BehaviorChangeMotivation(
                level=level,
                count=int(count),
                percentage=percentage
            ))

        return motivation_list, response_count

    def _extract_other_levers(self, df: pd.DataFrame) -> List[str]:
        """Extract free-text responses from the other_levers column."""
        if 'other_levers' not in df.columns:
            return []

        other_levers = df['other_levers'].dropna()
        # Filter out empty strings
        other_levers = other_levers[other_levers != '']
        return other_levers.tolist()

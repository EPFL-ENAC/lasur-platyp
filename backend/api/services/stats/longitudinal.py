import re
from typing import List

import pandas as pd

from api.models.query import CampaignGroup, ModeTransition


class LongitudinalService:
    SIMPLE_LABEL_PATTERN = re.compile(r"^typo\.reco\.simple_labels\.\d+$")

    @staticmethod
    def _campaign_to_group_index(groups: List[CampaignGroup]) -> dict:
        """Map campaign_id -> position of the group it belongs to in `groups`."""
        mapping = {}
        for index, group in enumerate(groups):
            for campaign_id in group.campaign_ids:
                mapping[campaign_id] = index
        return mapping

    @staticmethod
    def filter_longitudinal(df: pd.DataFrame, groups: List[CampaignGroup]) -> pd.DataFrame:
        """Filter records to participants (by email_hash) present in 2+ groups.

        Records with a NULL email_hash are silently excluded, since they cannot be
        tracked across campaigns.
        """
        if 'email_hash' not in df.columns or 'campaign_id' not in df.columns:
            return df.iloc[0:0]

        df = df[df['email_hash'].notna()].copy()
        if df.empty:
            return df

        campaign_to_group = LongitudinalService._campaign_to_group_index(
            groups)
        df['_group_idx'] = df['campaign_id'].map(campaign_to_group)
        df = df[df['_group_idx'].notna()]
        if df.empty:
            return df.drop(columns=['_group_idx'])

        group_counts = df.groupby('email_hash')['_group_idx'].nunique()
        eligible_hashes = group_counts[group_counts >= 2].index
        return df[df['email_hash'].isin(eligible_hashes)].drop(columns=['_group_idx'])

    @staticmethod
    def _primary_mode_by_participant(df: pd.DataFrame) -> pd.Series:
        """Most-frequent typo.reco.simple_labels.N value per participant (email_hash).

        Tie-break: first encountered, in row-major then column order (i.e. all
        of a row's label columns before moving to the next row).

        Vectorized: reshapes to one row per (participant, observed label)
        via stack() -- which preserves that exact row-major/column-minor
        traversal order -- instead of a groupby -> iterrows -> column loop.
        Per participant, picks the label with the highest count, breaking
        ties by earliest first-seen position (a groupby-sort instead of a
        Python-level max(..., key=...) over a running dict).
        """
        if df.empty or 'email_hash' not in df.columns:
            return pd.Series(dtype=object)

        label_cols = sorted(
            (c for c in df.columns if LongitudinalService.SIMPLE_LABEL_PATTERN.match(c)),
            key=lambda c: int(c.rsplit('.', 1)[1])
        )
        if not label_cols:
            return pd.Series(dtype=object)

        stacked = df[label_cols].stack()  # (row_idx, col) -> value, drops NaN by default
        if stacked.empty:
            return pd.Series(dtype=object)

        row_idx = stacked.index.get_level_values(0)
        long_df = pd.DataFrame({
            'email_hash': df['email_hash'].loc[row_idx].to_numpy(),
            'value': stacked.to_numpy(),
            # global row-major, column-minor encounter order
            'seq': range(len(stacked)),
        })

        agg = long_df.groupby(['email_hash', 'value']).agg(
            count=('seq', 'size'), first_seq=('seq', 'min')
        ).reset_index()
        agg = agg.sort_values(
            ['email_hash', 'count', 'first_seq'], ascending=[True, False, True])

        return agg.groupby('email_hash').first()['value']

    @staticmethod
    def compute_mode_transitions(df: pd.DataFrame, groups: List[CampaignGroup]) -> List[ModeTransition]:
        """Per-participant mode transitions between consecutive groups (A->B, B->C, ...).

        `groups` must be the full, originally-ordered group list so that positions
        stay stable: if a group has no data in `df` (e.g. it was dropped for privacy),
        its adjacent transitions are simply omitted rather than bridging across it.
        """
        if 'campaign_id' not in df.columns:
            return []

        campaign_to_group = LongitudinalService._campaign_to_group_index(
            groups)
        df = df.copy()
        df['_group_idx'] = df['campaign_id'].map(campaign_to_group)

        primary_by_group = {
            index: LongitudinalService._primary_mode_by_participant(
                df[df['_group_idx'] == index])
            for index in range(len(groups))
        }

        transitions = []
        for index in range(len(groups) - 1):
            source = primary_by_group.get(index)
            target = primary_by_group.get(index + 1)
            if source is None or target is None or source.empty or target.empty:
                continue
            joined = pd.DataFrame(
                {'source': source, 'target': target}).dropna()
            if joined.empty:
                continue
            counts = joined.groupby(['source', 'target']).size()
            for (source_mode, target_mode), count in counts.items():
                transitions.append(ModeTransition(
                    source_group=groups[index].name,
                    target_group=groups[index + 1].name,
                    source_mode=source_mode,
                    target_mode=target_mode,
                    count=int(count)
                ))

        return transitions

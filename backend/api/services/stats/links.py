import numpy as np
import pandas as pd
from api.models.query import Link, Links, Recommendation, StatLinks
from api.services.stats.commons import BaseStatsService


class LinksService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_mode_reco_links(self) -> StatLinks:
        """Compute all mode recommendation links from a DataFrame of records (v3 only)."""
        df_v3 = self._get_records_v3()
        links = Links(total=0, data=[])
        if not df_v3.empty:
            links = self._compute_mode_reco_links_v3(df_v3)

        return self._compute_stats_for_links(links)

    def compute_mode_reco_pro_links(self) -> StatLinks:
        """Compute all mode recommendation links from a DataFrame of records (v3 only)."""
        df_v3 = self._get_records_v3()
        links = Links(total=0, data=[])
        if not df_v3.empty:
            links = self._compute_mode_reco_pro_links_v3(df_v3)

        return self._compute_stats_for_links(links)

    #
    # Internal functions
    #

    def _compute_mode_reco_links_v3(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records.

        New-style records: link each journey's mode(s) to that same journey's own
        recommendation (typo.reco.reco_inter.<journey index>), weighted by that
        journey's `days`.
        Legacy records (typo.reco.reco_dt2.0 / .1, not tied to a specific journey):
        link every journey's mode(s) to each legacy recommendation, weighted by the
        sum of the person's journey days (as originally computed).
        """
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]
        # Coerce before summing/comparing: some records have this field
        # stored as a non-numeric string, which would otherwise raise on
        # `> 0` (or silently string-concatenate in the .sum() below).
        col_days_numeric = df[col_days].apply(pd.to_numeric, errors='coerce')
        legacy_cols = self._reco_legacy_columns(df)
        total_days_by_token = col_days_numeric.sum(
            axis=1) if len(col_days) and legacy_cols else None

        # (mode, reco, weight) triples, accumulated via groupby-sum at the end
        # instead of a Python-level dict built row by row.
        frames = []

        for i in range(len(col_days)):
            col_modes_i = df.columns[df.columns.str.startswith(
                f'data.freq_mod_journeys.{str(i)}.modes.')]
            if col_modes_i.empty:
                continue
            col_days_i = col_days[i]
            reco_col_i = f'typo.reco.reco_inter.{str(i)}'

            # int(days) <= 0 truncates toward zero, same as np.trunc for floats
            days_trunc = np.trunc(col_days_numeric[col_days_i])
            valid_days = col_days_numeric[col_days_i].notna() & (days_trunc > 0)
            if not valid_days.any():
                continue

            own_reco = df[reco_col_i] if reco_col_i in df.columns else pd.Series(
                np.nan, index=df.index)
            has_own_reco = own_reco.notna()

            modes_sub = df.loc[valid_days, col_modes_i.tolist()]
            stacked_modes = modes_sub.stack()  # drops NaN modes by default
            if stacked_modes.empty:
                continue
            row_idx = stacked_modes.index.get_level_values(0)
            modes_arr = stacked_modes.to_numpy()
            weight_days = days_trunc.loc[row_idx].to_numpy()
            has_own_arr = has_own_reco.loc[row_idx].to_numpy()

            # New-style: this journey's own recommendation, weighted by this
            # journey's own days
            if has_own_arr.any():
                frames.append(pd.DataFrame({
                    'mode': modes_arr[has_own_arr],
                    'reco': own_reco.loc[row_idx].to_numpy()[has_own_arr],
                    'weight': weight_days[has_own_arr],
                }))

            # Legacy: general recommendation(s), weighted by the person's
            # total journey days, one entry per legacy column
            legacy_mask = ~has_own_arr
            if legacy_mask.any() and legacy_cols and total_days_by_token is not None:
                legacy_row_idx = row_idx[legacy_mask]
                legacy_modes = modes_arr[legacy_mask]
                token_days = total_days_by_token.loc[legacy_row_idx].to_numpy()
                for legacy_col in legacy_cols:
                    frames.append(pd.DataFrame({
                        'mode': legacy_modes,
                        'reco': df[legacy_col].loc[legacy_row_idx].to_numpy(),
                        'weight': token_days,
                    }))

        if not frames:
            return Links(total=len(df), data=[])

        combined = pd.concat(frames, ignore_index=True)
        combined = combined[combined['reco'].notna() & combined['weight'].notna()]
        if combined.empty:
            return Links(total=len(df), data=[])
        combined['weight'] = combined['weight'].astype(int)

        grouped = combined.groupby(['mode', 'reco'])['weight'].sum()
        data = [Link(source=mode, target=reco, value=int(value))
                for (mode, reco), value in grouped.items()]
        return Links(total=len(df), data=data)

    def _compute_mode_reco_pro_links_v3(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""

        # New data version: get the series from data.freq_mod_pro_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_pro_journeys\..*\.days$', regex=True)]
        frames = []
        for i in range(len(col_days)):
            col_mode_i = f'data.freq_mod_pro_journeys.{str(i)}.mode'
            if col_mode_i not in df.columns:
                continue
            col_reco_i = f"typo.reco_pro.reco_pros.{str(i)}"
            if col_reco_i not in df.columns:
                continue
            mode_s = df[col_mode_i]
            reco_s = df[col_reco_i]
            mask = mode_s.notna() & reco_s.notna()
            if not mask.any():
                continue
            frames.append(pd.DataFrame({
                'mode': mode_s[mask].to_numpy(),
                'reco': reco_s[mask].to_numpy(),
            }))

        if not frames:
            return Links(total=len(df), data=[])

        combined = pd.concat(frames, ignore_index=True)
        grouped = combined.groupby(['mode', 'reco']).size()
        data = [Link(source=mode, target=reco, value=int(value))
                for (mode, reco), value in grouped.items()]
        return Links(total=len(df), data=data)

    def _compute_stats_for_links(self, links: Links) -> StatLinks:
        value_per_target: dict[str, int] = {}
        for link in links.data:
            value_per_target[link.target] = value_per_target.get(link.target, 0) + link.value
        
        if not value_per_target:
            return StatLinks(
                data=links.data,
                total=links.total,
                most_recommended_target=None,
            )

        most_recommended_target = max(value_per_target, key=value_per_target.get)
        most_recommended = Recommendation(
            target=most_recommended_target,
            value=value_per_target[most_recommended_target]
        )
        
        return StatLinks(
            data=links.data,
            total=links.total,
            most_recommended_target=most_recommended
        )

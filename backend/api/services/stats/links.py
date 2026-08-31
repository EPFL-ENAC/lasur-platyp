import numpy as np
import pandas as pd
from api.models.query import Link, Links, Recommendation, StatLinks
from api.services.stats.commons import COMPLEX_LABEL_MERGE, BaseStatsService, merge_label_components


class LinksService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_mode_reco_links_simple_labels(self) -> StatLinks:
        """Compute all mode recommendation links from typo.reco.simple_labels (v3 only)."""
        return self._compute_mode_reco_links("typo.reco.simple_labels")

    def compute_mode_reco_links_complex_labels(self) -> StatLinks:
        """Compute all mode recommendation links from typo.reco.complex_labels (v3 only).

        COMPLEX_LABEL_MERGE values are folded into their target bucket
        component-wise, so both a plain label (e.g. "pub") and any '+'-joined
        intermodal combination containing it (e.g. "car+pub") fold into the
        matching target (e.g. "tp", "car+tp"), as in the complex label
        frequencies and emissions.
        """
        return self._compute_mode_reco_links(
            "typo.reco.complex_labels", COMPLEX_LABEL_MERGE)

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

    def _compute_mode_reco_links(
        self, label_col_prefix: str, merge_map: dict[str, str] | None = None
    ) -> StatLinks:
        df_v3 = self._get_records_v3()
        links = Links(total=0, data=[])
        if not df_v3.empty:
            links = self._compute_mode_reco_links_v3(
                df_v3, label_col_prefix, merge_map)

        return self._compute_stats_for_links(links)

    def _compute_mode_reco_links_v3(
        self, df: pd.DataFrame, label_col_prefix: str,
        merge_map: dict[str, str] | None = None,
    ) -> Links:
        """Compute all mode recommendation links from a DataFrame of records.

        Journeys are sourced by their aggregated typology label
        (typo.reco.{simple,complex}_labels.{i}) instead of their raw modes.*
        list, so each journey's days are credited to exactly one source label.

        New-style records: link each journey's label to that same journey's own
        recommendation (typo.reco.reco_inter.<journey index>), weighted by that
        journey's `days`.
        Legacy records (typo.reco.reco_dt2.0 / .1, not tied to a specific journey):
        link every journey's label to each legacy recommendation, weighted by the
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

        # (label, reco, weight) triples, accumulated via groupby-sum at the end
        # instead of a Python-level dict built row by row.
        frames = []

        for i in range(len(col_days)):
            col_label_i = f'{label_col_prefix}.{str(i)}'
            if col_label_i not in df.columns:
                continue
            col_days_i = col_days[i]
            reco_col_i = f'typo.reco.reco_inter.{str(i)}'

            # int(days) <= 0 truncates toward zero, same as np.trunc for floats
            days_trunc = np.trunc(col_days_numeric[col_days_i])
            label_s = df[col_label_i]
            valid = (col_days_numeric[col_days_i].notna()
                     & (days_trunc > 0) & label_s.notna())
            if not valid.any():
                continue

            labels = label_s[valid].astype(str)
            if merge_map:
                labels = labels.map(
                    lambda label: merge_label_components(label, merge_map))
            weight_days = days_trunc[valid]

            own_reco = df[reco_col_i][valid] if reco_col_i in df.columns else pd.Series(
                np.nan, index=labels.index)
            has_own_reco = own_reco.notna()

            # New-style: this journey's own recommendation, weighted by this
            # journey's own days
            if has_own_reco.any():
                frames.append(pd.DataFrame({
                    'mode': labels[has_own_reco].to_numpy(),
                    'reco': own_reco[has_own_reco].to_numpy(),
                    'weight': weight_days[has_own_reco].to_numpy(),
                }))

            # Legacy: general recommendation(s), weighted by the person's
            # total journey days, one entry per legacy column
            legacy_mask = ~has_own_reco
            if legacy_mask.any() and legacy_cols and total_days_by_token is not None:
                legacy_idx = labels.index[legacy_mask]
                token_days = total_days_by_token.loc[legacy_idx].to_numpy()
                legacy_labels = labels.loc[legacy_idx].to_numpy()
                for legacy_col in legacy_cols:
                    frames.append(pd.DataFrame({
                        'mode': legacy_labels,
                        'reco': df[legacy_col].loc[legacy_idx].to_numpy(),
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

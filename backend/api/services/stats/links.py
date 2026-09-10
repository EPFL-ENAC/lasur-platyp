import numpy as np
import pandas as pd
from api.models.query import Link, Links, Recommendation, StatLinks
from api.services.stats.commons import COMPLEX_LABEL_MERGE, BaseStatsService, merge_label_components


class LinksService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_mode_reco_links_simple_labels(self) -> StatLinks:
        """Compute mode recommendation links from typo.reco.simple_labels to the
        simple recommendation of the same journey, typo.reco.reco_simple.{i}
        (v3 only): both ends are simple typology labels.
        """
        return self._compute_mode_reco_links(
            "typo.reco.simple_labels", "typo.reco.reco_simple")

    def compute_mode_reco_links_complex_labels(self) -> StatLinks:
        """Compute mode recommendation links from typo.reco.complex_labels to the
        recommended mode of the same journey, typo.reco.reco_inter.{i} (v3 only).

        COMPLEX_LABEL_MERGE values are folded into their target bucket
        component-wise, so both a plain label (e.g. "pub") and any '+'-joined
        intermodal combination containing it (e.g. "car+pub") fold into the
        matching target (e.g. "tp", "car+tp"), as in the complex label
        frequencies and emissions.
        """
        return self._compute_mode_reco_links(
            "typo.reco.complex_labels", "typo.reco.reco_inter",
            merge_map=COMPLEX_LABEL_MERGE, legacy_recos=True)

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
        self, label_col_prefix: str, reco_col_prefix: str,
        merge_map: dict[str, str] | None = None, legacy_recos: bool = False,
    ) -> StatLinks:
        df_v3 = self._get_records_v3()
        links = Links(total=0, data=[])
        if not df_v3.empty:
            links = self._compute_mode_reco_links_v3(
                df_v3, label_col_prefix, reco_col_prefix, merge_map, legacy_recos)

        return self._compute_stats_for_links(links)

    def _compute_mode_reco_links_v3(
        self, df: pd.DataFrame, label_col_prefix: str, reco_col_prefix: str,
        merge_map: dict[str, str] | None = None, legacy_recos: bool = False,
    ) -> Links:
        """Compute all mode recommendation links from a DataFrame of records.

        The home-to-work modal shift chart is person-centric: each person
        contributes exactly one link, from the typology label of their main
        journey (the most frequent one, ties broken by the first entered) to the
        recommendation made for that same journey
        (`{reco_col_prefix}.<journey index>`), whatever the number of journeys
        they declared and how often they make them.

        Journeys are sourced by their aggregated typology label
        (typo.reco.{simple,complex}_labels.{i}) instead of their raw modes.*
        list, so a person is credited to exactly one source label.

        When `legacy_recos` is set, persons of records collected before the
        per-journey recommendations (typo.reco.reco_dt2.0 / .1, not tied to a
        specific journey) are linked to the first legacy recommendation entered,
        so that they too count exactly once.
        """
        main = self._main_journey_labels(df, label_col_prefix)
        if main.empty:
            return Links(total=len(df), data=[])

        labels = main['value'].astype(str)
        if merge_map:
            labels = labels.map(
                lambda label: merge_label_components(label, merge_map))

        # recommendation of each person's main journey, resolved per journey
        # index rather than row by row
        recos = pd.Series(np.nan, index=main.index, dtype=object)
        for journey_id, group in main.groupby('journey'):
            reco_col = f'{reco_col_prefix}.{journey_id}'
            if reco_col not in df.columns:
                continue
            recos.loc[group.index] = df[reco_col].loc[group['row']].to_numpy()

        legacy_cols = self._reco_legacy_columns(df) if legacy_recos else []
        if legacy_cols:
            missing = recos.isna()
            if missing.any():
                rows = main['row'][missing]
                legacy = df[legacy_cols].loc[rows].bfill(axis=1).iloc[:, 0]
                recos.loc[missing] = legacy.to_numpy()

        combined = pd.DataFrame({'mode': labels.to_numpy(), 'reco': recos.to_numpy()})
        combined = combined[combined['reco'].notna()]
        if combined.empty:
            return Links(total=len(df), data=[])

        grouped = combined.groupby(['mode', 'reco']).size()
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

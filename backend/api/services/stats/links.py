import pandas as pd
from api.models.query import Link, Links
from api.services.stats.commons import BaseStatsService, MODES, MODES_PRO_V1


class LinksService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_mode_reco_links(self) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""
        # v1: legacy data version
        df_v1 = self._get_records_v1()
        links_v1 = self._compute_mode_reco_links_v1(df_v1)

        # v2: new data version
        df_v2 = self._get_records_v2()
        links_v2 = Links(total=0, data=[])
        if not df_v2.empty:
            links_v2 = self._compute_mode_reco_links_v2(df_v2)

        # merge links of same source and target
        return self._merge_links(links_v1, links_v2)

    def compute_mode_reco_pro_links(self) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""
        # v1: legacy data version
        df_v1 = self._get_records_v1()
        links_v1 = self._compute_mode_reco_pro_links_v1(df_v1)

        # v2: new data version
        df_v2 = self._get_records_v2()
        links_v2 = Links(total=0, data=[])
        if not df_v2.empty:
            links_v2 = self._compute_mode_reco_pro_links_v2(df_v2)

        # merge links of same source and target
        return self._merge_links(links_v1, links_v2)

    #
    # Internal functions
    #

    def _compute_mode_reco_links_v1(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""
        counts = {}
        for mode in MODES:
            col_name = f'data.freq_mod_{mode}'
            if col_name not in df.columns:
                continue
            df_mode = df[df[col_name].notna()]
            for _, row in df_mode.iterrows():
                reco = row['typo.reco.reco_dt2.0']
                mod_count = int(row[col_name])
                if mod_count <= 0:
                    continue
                mod_counts = counts.get(mode, {})
                mod_counts[reco] = mod_counts.get(reco, 0) + 1
                counts[mode] = mod_counts
        links = [Link(source=mod, target=reco, value=int(count)) for mod,
                 reco_counts in counts.items() for reco, count in reco_counts.items()]
        return Links(total=len(df), data=links)

    def _compute_mode_reco_links_v2(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""

        # New data version: get the series from data.freq_mod_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]
        counts = {}
        for i in range(len(col_days)):
            col_modes_i = df.columns[df.columns.str.startswith(
                f'data.freq_mod_journeys.{str(i)}.modes.')]
            if col_modes_i.empty:
                continue
            col_days_i = col_days[i]
            # make a dataframe with only i columns
            df_i = df[[col_days_i] + col_modes_i.tolist() +
                      ['typo.reco.reco_dt2.0']].copy()
            # iterate rows
            for _, row in df_i.iterrows():
                days = row[col_days_i]
                if pd.isna(days) or int(days) <= 0:
                    continue
                for col in col_modes_i:
                    mode = row[col]
                    if pd.isna(mode):
                        continue
                    reco = row['typo.reco.reco_dt2.0']
                    mod_counts = counts.get(mode, {})
                    mod_counts[reco] = mod_counts.get(reco, 0) + 1
                    counts[mode] = mod_counts
        data = [Link(source=mod, target=reco, value=int(count)) for mod,
                reco_counts in counts.items() for reco, count in reco_counts.items()]
        links = Links(total=len(df), data=data)
        return links

    def _compute_mode_reco_pro_links_v1(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""
        area_reco = {
            'local': 'typo.reco_pro.reco_pro_loc',
            'region': 'typo.reco_pro.reco_pro_reg',
            'europe': 'typo.reco_pro.reco_pro_reg',
            'inter': 'typo.reco_pro.reco_pro_int'
        }
        counts = {}
        for area_mode in MODES_PRO_V1:
          # split mode into area and transport mode
            area, mode = area_mode.split('_', 1)
            col_name = f'data.freq_mod_{area}_{mode}'
            if col_name not in df.columns:
                continue
            df_mode = df[df[col_name].notna()]
            for _, row in df_mode.iterrows():
                mod_count = int(row[col_name])
                if mod_count <= 0:
                    continue
                if area not in area_reco:
                    continue
                reco = row[area_reco[area]]
                mod_counts = counts.get(mode, {})
                mod_counts[reco] = mod_counts.get(reco, 0) + 1
                counts[mode] = mod_counts
        links = [Link(source=mod, target=reco, value=int(count)) for mod,
                 reco_counts in counts.items() for reco, count in reco_counts.items()]
        return Links(total=len(df), data=links)

    def _compute_mode_reco_pro_links_v2(self, df: pd.DataFrame) -> Links:
        """Compute all mode recommendation links from a DataFrame of records."""

        # New data version: get the series from data.freq_mod_pro_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_pro_journeys\..*\.days$', regex=True)]
        counts = {}
        for i in range(len(col_days)):
            col_mode_i = f'data.freq_mod_pro_journeys.{str(i)}.mode'
            if col_mode_i not in df.columns:
                continue
            col_reco_i = f"typo.reco_pro.reco_pros.{str(i)}"
            if col_reco_i not in df.columns:
                continue
            # make a dataframe with only i columns
            df_i = df[[col_mode_i, col_reco_i]].copy()
            # iterate rows
            for _, row in df_i.iterrows():
                mode = row[col_mode_i]
                reco = row[col_reco_i]
                if pd.isna(mode) or pd.isna(reco):
                    continue
                mod_counts = counts.get(mode, {})
                mod_counts[reco] = mod_counts.get(reco, 0) + 1
                counts[mode] = mod_counts
        data = [Link(source=mod, target=reco, value=int(count)) for mod,
                reco_counts in counts.items() for reco, count in reco_counts.items()]
        links = Links(total=len(df), data=data)
        return links

    def _merge_links(self, links1: Links, links2: Links) -> Links:
        """Merge two Links into one Links."""
        # merge links of same source and target
        merged_data = links1.data.copy()
        for link in links2.data:
            existing_link = next(
                (l for l in merged_data if l.source == link.source and l.target == link.target), None)
            if existing_link:
                existing_link.value += link.value
            else:
                merged_data.append(link)
        merged_links = Links(
            total=links1.total + links2.total,
            data=merged_data
        )
        return merged_links

import pandas as pd
import h3
from api.models.query import Emissions
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
    'elec': 90,
    'covoit': 93,
    'avoid': 0,
    'inter': 25
}


class EmissionsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_modes_emissions(self, apply_reco: bool = False) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records."""

        def calculate_distance_home_to_work(row):
            origin_lat = float(row['data.origin.lat'])
            origin_lon = float(row['data.origin.lon'])
            work_lat = float(row['data.workplace.lat'])
            work_lon = float(row['data.workplace.lon'])
            return self._calculate_distance(origin_lat, origin_lon, work_lat, work_lon)

        # Calculate distance_km to workplace for each record
        self.df['distance_km'] = self.df.apply(
            lambda row: calculate_distance_home_to_work(row), axis=1)

        # v1: count emissions from legacy fields
        df_v1 = self._get_records_v1()
        results_v1 = []
        for mode in MODES:
            results_v1.extend(self._compute_mode_emissions_v1(
                df_v1, mode, apply_reco))
        results = self._merge_emissions([], results_v1)

        # v2: count emissions from data.freq_mod_journeys
        df_v2 = self._get_records_v2()
        if not df_v2.empty:
            results_v2 = []
            for mode in MODES:
                results_v2.extend(self._compute_mode_emissions_v2(
                    df_v2, mode, apply_reco))
            # merge v1 and v2 results
            for em_v2 in results_v2:
                # find in results the one with same field
                em_v1 = next(
                    (e for e in results if e.field == em_v2.field), None)
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

    #
    # Internal functions
    #

    def _compute_mode_emissions_v1(self, df: pd.DataFrame, mode: str, apply_reco: bool = False) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records."""
        emissions = Emissions(
            field=mode, total=len(df), distances=0, journeys=0, emissions=0)
        # Find the column name for the mode
        col_name = f'data.freq_mod_{mode}'
        if col_name not in df.columns:
            return [emissions]

        # Subset the dataframe for the specific mode, filtered by colname not na
        df_mode = df[df[col_name].notna()]
        if len(df_mode) == 0:
            return [emissions]

        if apply_reco:
            # replace non sustainable modes (car, moto) by recommended mode
            df_mode = df_mode.copy()
            df_mode['applied_mode'] = df_mode.apply(
                lambda row: row['typo.reco.reco_dt2.0']
                if mode in ['car', 'moto'] else mode,
                axis=1
            )
            # change covoit for carpool
            df_mode['applied_mode'] = df_mode['applied_mode'].replace(
                'covoit', 'carpool')
            # make Emissions per applied_mode
            emissions_list = []
            for applied_mode in df_mode['applied_mode'].unique():
                df_applied_mode = df_mode[df_mode['applied_mode']
                                          == applied_mode]
                em = Emissions(
                    field=applied_mode,
                    total=len(df_applied_mode),
                    distances=float(sum(df_applied_mode['distance_km'])),
                    journeys=int(sum(
                        df_applied_mode[col_name] * 45 * 2)),
                    emissions=float(sum(
                        df_applied_mode['distance_km'] * df_applied_mode[col_name] * 45 * 2 * MODE_EMISSIONS[applied_mode] / 1000))
                )
                emissions_list.append(em)
            return emissions_list
        else:
            emissions.distances = float(df_mode['distance_km'].sum())
            emissions.journeys = int(df_mode[col_name].sum() * 45 * 2)
            emissions.emissions = float(sum(
                df_mode['distance_km'] * df_mode[col_name] * 45 * 2 * MODE_EMISSIONS[mode] / 1000))
            return [emissions]

    def _compute_mode_emissions_v2(self, df: pd.DataFrame, mode: str, apply_reco: bool = False) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records."""
        def compute_mode_emissions(row, mode, i):
            modes = []
            for col in row.index:
                if col.startswith(f'data.freq_mod_journeys.{i}.modes.'):
                    val = row[col]
                    if not pd.isna(val):
                        modes.append(val)
            modes = set(modes)

            # if the train is one of the modes, consider that 80% of the distance is done by train,
            # then split the rest equally among the other modes used.
            days = row[f'data.freq_mod_journeys.{i}.days']
            dist = row['distance_km']
            co2 = 0
            if 'train' in modes:
                if mode == 'train':
                    co2 += 0.8 * 45 * 2 * \
                        (days * dist * MODE_EMISSIONS['train'] / 1000)
                elif mode in modes:
                    co2 += 0.2 / (len(modes) - 1) * 45 * 2 * \
                        (days * dist * MODE_EMISSIONS[mode] / 1000)
            elif mode in modes:
                co2 += 1 / len(modes) * 45 * 2 * \
                    (days * dist * MODE_EMISSIONS[mode] / 1000)
            em_factor = co2 * 1000 / (45 * 2 * days * dist)
            return [co2, em_factor]

        # New data version: get the series from data.freq_mod_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_journeys\..*\.days$', regex=True)]

        all_emissions = []
        for i in range(len(col_days)):
            # print("journey:", i)
            col_modes_i = df.columns[df.columns.str.startswith(
                f'data.freq_mod_journeys.{str(i)}.modes.')]
            if col_modes_i.empty:
                continue
            col_days_i = col_days[i]
            # make a dataframe with only i columns
            df_i = df[['distance_km', col_days_i, 'typo.reco.reco_dt2.0'] +
                      col_modes_i.tolist()].copy()
            if apply_reco:
                # Emissions for recommended modes replacing non sustainable modes
                # replace non sustainable modes (car, moto) by recommended mode
                df_i['applied_mode'] = df_i.apply(
                    lambda row: row['typo.reco.reco_dt2.0']
                    if mode in ['car', 'moto'] else mode,
                    axis=1
                )
                # make emissions per applied_mode
                emissions_dict = {}
                for idx, row in df_i.iterrows():
                    applied_mode = row['applied_mode']
                    co2, em_factor = compute_mode_emissions(
                        row, applied_mode, i)
                    if applied_mode not in emissions_dict:
                        emissions_dict[applied_mode] = Emissions(
                            field=applied_mode,
                            total=len(df),
                            distances=0,
                            journeys=0,
                            emissions=0
                        )
                    emissions_entry = emissions_dict[applied_mode]
                    if co2 > 0:
                        emissions_entry.distances += float(
                            row['distance_km'] * row[col_days_i] * 45 * 2)
                        emissions_entry.journeys += int(
                            row[col_days_i] * 45 * 2)
                        emissions_entry.emissions += float(co2)
                return list(emissions_dict.values())
            else:
                # Emissions for requested mode only
                emissions = Emissions(
                    field=mode,
                    total=len(df),
                    distances=0,
                    journeys=0,
                    emissions=0
                )
                # compute emissions factor
                df_i[['mode_emissions', 'em_factor']] = df_i.apply(
                    lambda row: compute_mode_emissions(row, mode, i), axis=1, result_type='expand')
                # filter only positive emissions
                df_i = df_i[df_i['mode_emissions'] > 0]
                # print(df_i)
                emissions.distances += float(sum(
                    df_i['distance_km'] * df_i[col_days_i] * 45 * 2))
                emissions.journeys += int(sum(
                    df_i[col_days_i] * 45 * 2))
                emissions.emissions += float(sum(df_i['mode_emissions']))
                all_emissions.append(emissions)

        return all_emissions

    def _compute_mode_pro_emissions_v2(self, df: pd.DataFrame, mode: str, apply_reco: bool = False) -> list[Emissions]:
        """Compute all CO2 emissions from a DataFrame of records."""

        def calculate_distance(row, i):
            lat = float(row['data.workplace.lat'])
            lon = float(row['data.workplace.lon'])
            h3_index = row[f'data.freq_mod_pro_journeys.{str(i)}.hex_id']
            mode = row[f'data.freq_mod_pro_journeys.{str(i)}.mode']
            return self._calculate_distance_to_h3(lat, lon, h3_index, mode)

        def compute_mode_emissions(row, mode, i):
            # if the train is one of the modes, consider that 80% of the distance is done by train,
            # then split the rest equally among the other modes used.
            days = row[f'data.freq_mod_pro_journeys.{i}.days']
            dist = row['distance_km']
            co2 = 2 * (days * dist * MODE_EMISSIONS[mode] / 1000)
            em_factor = co2 * 1000 / (2 * days * dist)
            return [co2, em_factor]

        # New data version: get the series from data.freq_mod_journeys
        col_days = df.columns[df.columns.str.contains(
            r'^data\.freq_mod_pro_journeys\..*\.days$', regex=True)]
        emissions = Emissions(
            field=mode,
            total=len(df),
            distances=0,
            journeys=0,
            emissions=0
        )
        for i in range(len(col_days)):
            # print("journey:", i)
            col_mode_i = f'data.freq_mod_pro_journeys.{str(i)}.mode'
            if col_mode_i not in df.columns:
                continue
            col_hexid_i = f'data.freq_mod_pro_journeys.{str(i)}.hex_id'
            if col_hexid_i not in df.columns:
                continue
            col_days_i = col_days[i]
            # filter only rows where mode matches
            df_i = df[df[col_mode_i] == mode]
            if len(df_i) == 0:
                continue
            # make a dataframe with only i columns and workplace lat/lon
            df_i = df_i[['data.workplace.lat', 'data.workplace.lon',
                         col_days_i, col_mode_i, col_hexid_i]].copy()
            # Calculate distance_km to pro travel destination for each record
            df_i['distance_km'] = df.apply(
                lambda row: calculate_distance(row, i), axis=1)
            # compute emissions factor
            df_i[['mode_emissions', 'em_factor']] = df_i.apply(
                lambda row: compute_mode_emissions(row, mode, i), axis=1, result_type='expand')
            # filter only positive emissions
            df_i = df_i[df_i['mode_emissions'] > 0]
            # print(df_i)
            emissions.distances += float(
                sum(df_i['distance_km'] * df_i[col_days_i] * 2))
            emissions.journeys += int(sum(df_i[col_days_i] * 2))
            emissions.emissions += float(sum(df_i['mode_emissions']))

        return [emissions]

    def _merge_emissions(self, emissions1: list[Emissions], emissions2: list[Emissions]) -> list[Emissions]:
        """Merge each Emissions into a list of Emissions."""
        for em2 in emissions2:
            em1 = next(
                (e for e in emissions1 if e.field == em2.field), None)
            if not em1:
                emissions1.append(em2)
                continue
            em = Emissions(
                field=em1.field,
                total=em1.total + em2.total,
                distances=em1.distances + em2.distances,
                journeys=em1.journeys + em2.journeys,
                emissions=em1.emissions + em2.emissions
            )
            # replace in emissions1
            for i in range(len(emissions1)):
                if emissions1[i].field == em.field:
                    emissions1[i] = em
                    break

        return emissions1

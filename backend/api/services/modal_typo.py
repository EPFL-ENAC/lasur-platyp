from api.config import config
from api.models.domain import Record, Company, Campaign, CompanyAction
import requests


class ModalTypoService:

    def __init__(self):
        self.url = config.LASUR_API_URL
        self.key = config.LASUR_API_KEY
        self.headers = {
            "x-api-key": self.key,
            "Content-Type": "application/json"
        }

    def get_recommendation(self, record: Record) -> dict:
        """Get typo suggestions for a record"""
        url = f"{self.url}/modal-typo/reco"
        freq_mods = self.get_freq_mod_params(record)
        data = {
            "o_lon": record.data["origin"]["lon"],
            "o_lat": record.data["origin"]["lat"],
            "d_lon": record.data["workplace"]["lon"],
            "d_lat": record.data["workplace"]["lat"],
            "tps_traj": record.data["travel_time"],
            "tx_trav": record.data["employment_rate"],
            "tx_tele": record.data["remote_work_rate"],
            "fm_dt_voit": freq_mods["fm_dt_voit"],
            "fm_dt_moto": freq_mods["fm_dt_moto"],
            "fm_dt_tpu": freq_mods["fm_dt_tpu"],
            "fm_dt_train": freq_mods["fm_dt_train"],
            "fm_dt_velo": freq_mods["fm_dt_velo"],
            "a_voit": record.data["needs_car"],
            "a_moto": record.data["needs_moto"],
            "a_tpu": record.data["needs_pub"],
            "a_train": record.data["needs_train"],
            "a_marc": record.data["needs_walking"],
            "a_velo": record.data["needs_bike"],
            "i_tmps": record.data["importance_time"],
            "i_prix": record.data["importance_cost"],
            "i_flex": record.data["importance_flex"],
            "i_conf": record.data["importance_comfort"],
            "i_fiab": record.data["importance_rel"],
            "i_prof": record.data["importance_most"],
            "i_envi": record.data["importance_env"]
        }
        response = requests.post(
            url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_recommendation_multi(self, record: Record) -> dict:
        """Get multi typo suggestions for a record"""
        url = f"{self.url}/modal-typo/reco-multi"
        freq_mods = self.get_freq_mod_params(record)
        data = {
            "o_lon": record.data["origin"]["lon"],
            "o_lat": record.data["origin"]["lat"],
            "d_lon": record.data["workplace"]["lon"],
            "d_lat": record.data["workplace"]["lat"],
            "tps_traj": record.data["travel_time"],
            "constraints": record.data["constraints"],
            "fm_dt_voit": freq_mods["fm_dt_voit"],
            "fm_dt_moto": freq_mods["fm_dt_moto"],
            "fm_dt_tpu": freq_mods["fm_dt_tpu"],
            "fm_dt_train": freq_mods["fm_dt_train"],
            "fm_dt_velo": freq_mods["fm_dt_velo"],
            "fm_dt_march": freq_mods["fm_dt_march"],
            "fm_dt_inter": freq_mods["fm_dt_inter"],

            "a_voit": record.data["needs_car"],
            "a_moto": record.data["needs_moto"],
            "a_tpu": record.data["needs_pub"],
            "a_train": record.data["needs_train"],
            "a_marc": record.data["needs_walking"],
            "a_velo": record.data["needs_bike"],

            "i_tmps": record.data["importance_time"],
            "i_prix": record.data["importance_cost"],
            "i_flex": record.data["importance_flex"],
            "i_conf": record.data["importance_comfort"],
            "i_fiab": record.data["importance_rel"],
            "i_prof": record.data["importance_most"],
            "i_envi": record.data["importance_env"]
        }
        response = requests.post(
            url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_recommendation_pro(self, record: Record, scores: dict) -> dict:
        """Get typo pro suggestions for a record"""
        record.company_id
        url = f"{self.url}/modal-typo/reco-pro"
        freq_mod_pros = self.get_freq_mod_pro_params(record)
        data = {
            "score_velo": scores["velo"],
            "score_tpu": scores["tpu"],
            "score_train": scores["train"],
            "score_elec": scores["elec"],
            "pro_loc": 'local' in record.data["trav_pro"],
            "pro_reg": 'region' in record.data["trav_pro"],
            "pro_int": 'inter' in record.data["trav_pro"],
            "fm_pro_loc_voit": freq_mod_pros["fm_pro_loc_voit"],
            "fm_pro_loc_moto": freq_mod_pros["fm_pro_loc_moto"],
            "fm_pro_loc_tpu": freq_mod_pros["fm_pro_loc_tpu"],
            "fm_pro_loc_train": freq_mod_pros["fm_pro_loc_train"],
            "fm_pro_loc_velo": freq_mod_pros["fm_pro_loc_velo"],
            "fm_pro_loc_marc": freq_mod_pros["fm_pro_loc_marc"],
            "fm_pro_reg_voit": freq_mod_pros["fm_pro_reg_voit"],
            "fm_pro_reg_moto": freq_mod_pros["fm_pro_reg_moto"],
            "fm_pro_reg_train": freq_mod_pros["fm_pro_reg_train"],
            "fm_pro_reg_avio": freq_mod_pros["fm_pro_reg_avio"],
            "fm_pro_int_voit": freq_mod_pros["fm_pro_int_voit"],
            "fm_pro_int_train": freq_mod_pros["fm_pro_int_train"],
            "fm_pro_int_avio": freq_mod_pros["fm_pro_int_avio"]
        }
        response = requests.post(
            url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_recommendation_employer_actions(self, company: Company, campaign: Campaign, custom_actions: list[CompanyAction], locale: str, reco_dt2: list, reco_pro_loc: str, reco_pro_reg: str, reco_pro_int: str) -> dict:
        """Get employer actions for a record"""
        url = f"{self.url}/modal-typo/empl"

        # get company/campaign actions
        actions = company.actions if company.actions else {}
        if campaign.actions:
            # campaign actions replaces company actions if actions are not empty lists
            has_actions = False
            for key, value in campaign.actions.items():
                if len(value) > 0:
                    has_actions = True
                    break
            if has_actions:
                actions = campaign.actions

        # check if custom actions are applied and change id for locale label
        if custom_actions and len(custom_actions) > 0:
            for group in actions:
                if actions[group]:
                    for i, action in enumerate(actions[group]):
                        # check if action can be parsed as an int
                        if self.is_id(action):
                            # check if action is a custom action
                            for custom_action in custom_actions:
                                if str(custom_action.id) == action:
                                    if custom_action.labels:
                                        # replace action with its label
                                        if locale in custom_action.labels:
                                            actions[group][i] = custom_action.labels[locale]
                                        elif "en" in custom_action.labels:
                                            # if no label for the locale, use the english label
                                            actions[group][i] = custom_action.labels["en"]
                                        else:
                                            # if no label for the locale, use the first label
                                            actions[group][i] = list(
                                                custom_action.labels.values())[0]
                                    break

        data = {
            "empl": {
                "mesures_globa": actions["mesures_globa"] if "mesures_globa" in actions else [],
                "mesures_tpu": actions["mesures_tpu"] if "mesures_tpu" in actions else [],
                "mesures_train": actions["mesures_train"] if "mesures_train" in actions else [],
                "mesures_inter": actions["mesures_inter"] if "mesures_inter" in actions else [],
                "mesures_velo": actions["mesures_velo"] if "mesures_velo" in actions else [],
                "mesures_covoit": actions["mesures_covoit"] if "mesures_covoit" in actions else [],
                "mesures_elec": actions["mesures_elec"] if "mesures_elec" in actions else [],
                "mesures_pro_globa": actions["mesures_pro_globa"] if "mesures_pro_globa" in actions else [],
                "mesures_pro_velo": actions["mesures_pro_velo"] if "mesures_pro_velo" in actions else [],
                "mesures_pro_tpu": actions["mesures_pro_tpu"] if "mesures_pro_tpu" in actions else [],
                "mesures_pro_train": actions["mesures_pro_train"] if "mesures_pro_train" in actions else [],
                "mesures_pro_elec": actions["mesures_pro_elec"] if "mesures_pro_elec" in actions else [],
            },
            "reco_dt2": reco_dt2,
            "reco_pro_loc": reco_pro_loc,
            "reco_pro_reg": reco_pro_reg,
            "reco_pro_int": reco_pro_int
        }
        response = requests.post(
            url, headers=self.headers, json=data)
        response.raise_for_status()
        empl_actions = response.json()
        empl_actions["mesures_globa"] = actions["mesures_globa"] if "mesures_globa" in actions else []
        empl_actions["mesures_pro_globa"] = actions["mesures_pro_globa"] if "mesures_pro_globa" in actions else []
        return empl_actions

    def get_freq_mod_params(self, record: Record) -> dict:
        """Get frequency modes from record data"""
        fm_dt_voit = self.as_int(
            record.data["freq_mod_car"]) if "freq_mod_car" in record.data else 0
        fm_dt_moto = self.as_int(
            record.data["freq_mod_moto"]) if "freq_mod_moto" in record.data else 0
        fm_dt_tpu = self.as_int(
            record.data["freq_mod_pub"]) if "freq_mod_pub" in record.data else 0
        fm_dt_train = self.as_int(
            record.data["freq_mod_train"]) if "freq_mod_train" in record.data else 0
        fm_dt_velo = self.as_int(
            record.data["freq_mod_bike"]) if "freq_mod_bike" in record.data else 0
        fm_dt_march = self.as_int(
            record.data["freq_mod_walking"]) if "freq_mod_walking" in record.data else 0
        fm_dt_inter = 1 if "freq_mod_combined" in record.data else 0
        journeys = record.data["freq_mod_journeys"] if "freq_mod_journeys" in record.data else [
        ]
        # count mode days for each journey
        for journey in journeys:
            modes = journey["modes"] if "modes" in journey else []
            modes = list(set(modes))  # remove duplicates
            if "car" in modes:
                fm_dt_voit += journey.get('days', 1)
            if "moto" in modes:
                fm_dt_moto += journey.get('days', 1)
            if "pub" in modes:
                fm_dt_tpu += journey.get('days', 1)
            if "train" in modes:
                fm_dt_train += journey.get('days', 1)
            if "bike" in modes:
                fm_dt_velo += journey.get('days', 1)
            if "walking" in modes:
                fm_dt_march += journey.get('days', 1)
            if len(modes) > 1:
                fm_dt_inter = 1
        return {
            "fm_dt_voit": fm_dt_voit,
            "fm_dt_moto": fm_dt_moto,
            "fm_dt_tpu": fm_dt_tpu,
            "fm_dt_train": fm_dt_train,
            "fm_dt_velo": fm_dt_velo,
            "fm_dt_march": fm_dt_march,
            "fm_dt_inter": fm_dt_inter,
        }

    def get_freq_mod_pro_params(self, record: Record) -> dict:
        """Get frequency modes professional from record data"""
        fm_pro_loc_voit = self.as_int(
            record.data["freq_mod_pro_local_car"]) if "freq_mod_pro_local_car" in record.data else 0
        fm_pro_loc_moto = self.as_int(
            record.data["freq_mod_pro_local_moto"]) if "freq_mod_pro_local_moto" in record.data else 0
        fm_pro_loc_tpu = self.as_int(
            record.data["freq_mod_pro_local_pub"]) if "freq_mod_pro_local_pub" in record.data else 0
        fm_pro_loc_train = self.as_int(
            record.data["freq_mod_pro_local_train"]) if "freq_mod_pro_local_train" in record.data else 0
        fm_pro_loc_velo = self.as_int(
            record.data["freq_mod_pro_local_bike"]) if "freq_mod_pro_local_bike" in record.data else 0
        fm_pro_loc_marc = self.as_int(
            record.data["freq_mod_pro_local_walking"]) if "freq_mod_pro_local_walking" in record.data else 0
        loc_journeys = record.data["freq_mod_pro_local_journeys"] if "freq_mod_pro_local_journeys" in record.data else [
        ]
        # count mode days for each journey
        for journey in loc_journeys:
            if "car" == journey["mode"]:
                fm_pro_loc_voit += journey.get('days', 1)
            if "moto" == journey["mode"]:
                fm_pro_loc_moto += journey.get('days', 1)
            if "pub" == journey["mode"]:
                fm_pro_loc_tpu += journey.get('days', 1)
            if "train" == journey["mode"]:
                fm_pro_loc_train += journey.get('days', 1)
            if "bike" == journey["mode"]:
                fm_pro_loc_velo += journey.get('days', 1)
            if "walking" == journey["mode"]:
                fm_pro_loc_marc += journey.get('days', 1)

        fm_pro_reg_voit = self.as_int(
            record.data["freq_mod_pro_regional_car"]) if "freq_mod_pro_regional_car" in record.data else 0
        fm_pro_reg_moto = self.as_int(
            record.data["freq_mod_pro_regional_moto"]) if "freq_mod_pro_regional_moto" in record.data else 0
        fm_pro_reg_train = self.as_int(
            record.data["freq_mod_pro_regional_train"]) if "freq_mod_pro_regional_train" in record.data else 0
        fm_pro_reg_avio = self.as_int(
            record.data["freq_mod_pro_regional_plane"]) if "freq_mod_pro_regional_plane" in record.data else 0
        reg_journeys = record.data["freq_mod_pro_regional_journeys"] if "freq_mod_pro_regional_journeys" in record.data else [
        ]
        # count mode days for each journey
        for journey in reg_journeys:
            if "car" == journey["mode"]:
                fm_pro_reg_voit += journey.get('days', 1)
            if "moto" == journey["mode"]:
                fm_pro_reg_moto += journey.get('days', 1)
            if "train" == journey["mode"]:
                fm_pro_reg_train += journey.get('days', 1)
            if "plane" == journey["mode"]:
                fm_pro_reg_avio += journey.get('days', 1)

        fm_pro_eur_voit = self.as_int(
            record.data["freq_mod_pro_europe_car"]) if "freq_mod_pro_europe_car" in record.data else 0
        fm_pro_eur_train = self.as_int(
            record.data["freq_mod_pro_europe_train"]) if "freq_mod_pro_europe_train" in record.data else 0
        fm_pro_eur_avio = self.as_int(
            record.data["freq_mod_pro_europe_plane"]) if "freq_mod_pro_europe_plane" in record.data else 0
        eur_journeys = record.data["freq_mod_pro_europe_journeys"] if "freq_mod_pro_europe_journeys" in record.data else [
        ]
        # count mode days for each journey
        for journey in eur_journeys:
            if "car" == journey["mode"]:
                fm_pro_eur_voit += journey.get('days', 1)
            if "train" == journey["mode"]:
                fm_pro_eur_train += journey.get('days', 1)
            if "plane" == journey["mode"]:
                fm_pro_eur_avio += journey.get('days', 1)

        fm_pro_int_voit = self.as_int(
            record.data["freq_mod_pro_inter_car"]) if "freq_mod_pro_inter_car" in record.data else 0
        fm_pro_int_train = self.as_int(
            record.data["freq_mod_pro_inter_train"]) if "freq_mod_pro_inter_train" in record.data else 0
        fm_pro_int_avio = self.as_int(
            record.data["freq_mod_pro_inter_plane"]) if "freq_mod_pro_inter_plane" in record.data else 0
        int_journeys = record.data["freq_mod_pro_inter_journeys"] if "freq_mod_pro_inter_journeys" in record.data else [
        ]
        # count mode days for each journey
        for journey in int_journeys:
            if "car" == journey["mode"]:
                fm_pro_int_voit += journey.get('days', 1)
            if "train" == journey["mode"]:
                fm_pro_int_train += journey.get('days', 1)
            if "plane" == journey["mode"]:
                fm_pro_int_avio += journey.get('days', 1)

        return {
            "fm_pro_loc_voit": fm_pro_loc_voit,
            "fm_pro_loc_moto": fm_pro_loc_moto,
            "fm_pro_loc_tpu": fm_pro_loc_tpu,
            "fm_pro_loc_train": fm_pro_loc_train,
            "fm_pro_loc_velo": fm_pro_loc_velo,
            "fm_pro_loc_marc": fm_pro_loc_marc,

            "fm_pro_reg_voit": fm_pro_reg_voit,
            "fm_pro_reg_moto": fm_pro_reg_moto,
            "fm_pro_reg_train": fm_pro_reg_train,
            "fm_pro_reg_avio": fm_pro_reg_avio,

            "fm_pro_eur_voit": fm_pro_eur_voit,
            "fm_pro_eur_train": fm_pro_eur_train,
            "fm_pro_eur_avio": fm_pro_eur_avio,

            "fm_pro_int_voit": fm_pro_int_voit,
            "fm_pro_int_train": fm_pro_int_train,
            "fm_pro_int_avio": fm_pro_int_avio
        }

    def is_id(self, s: str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False

    def as_int(self, val: int | tuple) -> int:
        try:
            return int(val[0]) if isinstance(val, tuple) else int(val)
        except (ValueError, TypeError):
            return 0

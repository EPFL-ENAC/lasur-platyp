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
        data = {
            "score_velo": scores["velo"],
            "score_tpu": scores["tpu"],
            "score_train": scores["train"],
            "score_elec": scores["elec"],
            "pro_loc": 'local' in record.data["trav_pro"],
            "pro_reg": 'region' in record.data["trav_pro"],
            "pro_int": 'inter' in record.data["trav_pro"],
            "fm_pro_loc_voit": record.data["freq_mod_pro_local_car"],
            "fm_pro_loc_moto": record.data["freq_mod_pro_local_moto"],
            "fm_pro_loc_tpu": record.data["freq_mod_pro_local_pub"],
            "fm_pro_loc_train": record.data["freq_mod_pro_local_train"],
            "fm_pro_loc_velo": record.data["freq_mod_pro_local_bike"],
            "fm_pro_loc_marc": record.data["freq_mod_pro_local_walking"],
            "fm_pro_reg_voit": record.data["freq_mod_pro_region_car"],
            "fm_pro_reg_moto": record.data["freq_mod_pro_region_moto"],
            "fm_pro_reg_train": record.data["freq_mod_pro_region_train"],
            "fm_pro_reg_avio": record.data["freq_mod_pro_region_plane"],
            "fm_pro_int_voit": record.data["freq_mod_pro_europe_car"],
            "fm_pro_int_train": record.data["freq_mod_pro_europe_train"],
            "fm_pro_int_avio": record.data["freq_mod_pro_europe_plane"],
            "fm_pro_int_voit": record.data["freq_mod_pro_inter_car"],
            "fm_pro_int_train": record.data["freq_mod_pro_inter_train"],
            "fm_pro_int_avio": record.data["freq_mod_pro_inter_plane"]
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
            if "car" in journey["modes"]:
                fm_dt_voit += 1
            if "moto" in journey["modes"]:
                fm_dt_moto += 1
            if "pub" in journey["modes"]:
                fm_dt_tpu += 1
            if "train" in journey["modes"]:
                fm_dt_train += 1
            if "bike" in journey["modes"]:
                fm_dt_velo += 1
            if "walking" in journey["modes"]:
                fm_dt_march += 1
            if len(journey["modes"]) > 1:
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

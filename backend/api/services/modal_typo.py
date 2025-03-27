from api.config import config
from api.models.domain import Record, Company, Campaign
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
        data = {
            "o_lon": record.data["origin"]["lon"],
            "o_lat": record.data["origin"]["lat"],
            "d_lon": record.data["workplace"]["lon"],
            "d_lat": record.data["workplace"]["lat"],
            "tps_traj": record.data["travel_time"],
            "tx_trav": record.data["employment_rate"],
            "tx_tele": record.data["remote_work_rate"],
            "fm_dt_voit": record.data["freq_mod_car"],
            "fm_dt_moto": record.data["freq_mod_moto"],
            "fm_dt_tpu": record.data["freq_mod_pub"],
            "fm_dt_train": record.data["freq_mod_train"],
            "fm_dt_velo": record.data["freq_mod_bike"],
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
        data = {
            "o_lon": record.data["origin"]["lon"],
            "o_lat": record.data["origin"]["lat"],
            "d_lon": record.data["workplace"]["lon"],
            "d_lat": record.data["workplace"]["lat"],
            "tps_traj": record.data["travel_time"],
            "constraints": record.data["constraints"],
            "fm_dt_voit": record.data["freq_mod_car"],
            "fm_dt_moto": record.data["freq_mod_moto"],
            "fm_dt_tpu": record.data["freq_mod_pub"],
            "fm_dt_train": record.data["freq_mod_train"],
            "fm_dt_velo": record.data["freq_mod_bike"],
            "fm_dt_march": record.data["freq_mod_walking"],
            "fm_dt_inter": 1 if record.data["freq_mod_combined"] else 0,

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
            "fr_pro_loc": record.data["freq_trav_pro_local"],
            "fr_pro_reg": record.data["freq_trav_pro_region"],
            "fr_pro_int": record.data["freq_trav_pro_inter"],
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
            "fm_pro_int_voit": record.data["freq_mod_pro_inter_car"],
            "fm_pro_int_train": record.data["freq_mod_pro_inter_train"],
            "fm_pro_int_avio": record.data["freq_mod_pro_inter_plane"]
        }
        response = requests.post(
            url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_recommendation_employer_actions(self, company: Company, campaign: Campaign, reco_dt2: list, reco_pro_loc: str, reco_pro_reg: str, reco_pro_int: str) -> dict:
        """Get employer actions for a record"""
        url = f"{self.url}/modal-typo/empl"
        # check if campaign has actions
        actions = company.actions
        if campaign.actions:
            # campaign actions replaces company actions if actions are not empty lists
            has_actions = False
            for key, value in campaign.actions.items():
                if len(value) > 0:
                    has_actions = True
                    break
            if has_actions:
                actions = campaign.actions
        data = {
            "empl": {
                "mesures_globa": actions["mesures_globa"] if actions and "mesures_globa" in actions else [],
                "mesures_tpu": actions["mesures_tpu"] if actions and "mesures_tpu" in actions else [],
                "mesures_train": actions["mesures_train"] if actions and "mesures_train" in actions else [],
                "mesures_inter": actions["mesures_inter"] if actions and "mesures_inter" in actions else [],
                "mesures_velo": actions["mesures_velo"] if actions and "mesures_velo" in actions else [],
                "mesures_covoit": actions["mesures_covoit"] if actions and "mesures_covoit" in actions else [],
                "mesures_elec": actions["mesures_elec"] if actions and "mesures_elec" in actions else [],
                "mesures_pro_velo": actions["mesures_pro_velo"] if actions and "mesures_pro_velo" in actions else [],
                "mesures_pro_tpu": actions["mesures_pro_tpu"] if actions and "mesures_pro_tpu" in actions else [],
                "mesures_pro_train": actions["mesures_pro_train"] if actions and "mesures_pro_train" in actions else [],
                "mesures_pro_elec": actions["mesures_pro_elec"] if actions and "mesures_pro_elec" in actions else [],
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
        empl_actions["mesures_globa"] = actions["mesures_globa"] if actions and "mesures_globa" in actions else []
        return empl_actions

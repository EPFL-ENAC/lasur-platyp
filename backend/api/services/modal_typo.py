from api.config import config
from api.models.domain import Record, Company
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

    def get_recommendation_employer_actions(self, company: Company, reco_dt2: list, reco_pro_loc: str, reco_pro_reg: str, reco_pro_int: str) -> dict:
        """Get employer actions for a record"""
        url = f"{self.url}/modal-typo/empl"
        data = {
            "empl": {
                "mesures_globa": company.actions["mesures_globa"] if company.actions and "mesures_globa" in company.actions else [],
                "mesures_tpu": company.actions["mesures_tpu"] if company.actions and "mesures_tpu" in company.actions else [],
                "mesures_train": company.actions["mesures_train"] if company.actions and "mesures_train" in company.actions else [],
                "mesures_inter": company.actions["mesures_inter"] if company.actions and "mesures_inter" in company.actions else [],
                "mesures_velo": company.actions["mesures_velo"] if company.actions and "mesures_velo" in company.actions else [],
                "mesures_covoit": company.actions["mesures_covoit"] if company.actions and "mesures_covoit" in company.actions else [],
                "mesures_elec": company.actions["mesures_elec"] if company.actions and "mesures_elec" in company.actions else [],
                "mesures_pro_velo": company.actions["mesures_pro_velo"] if company.actions and "mesures_pro_velo" in company.actions else [],
                "mesures_pro_tpu": company.actions["mesures_pro_tpu"] if company.actions and "mesures_pro_tpu" in company.actions else [],
                "mesures_pro_train": company.actions["mesures_pro_train"] if company.actions and "mesures_pro_train" in company.actions else [],
                "mesures_pro_elec": company.actions["mesures_pro_elec"] if company.actions and "mesures_pro_elec" in company.actions else [],
            },
            "reco_dt2": reco_dt2,
            "reco_pro_loc": reco_pro_loc,
            "reco_pro_reg": reco_pro_reg,
            "reco_pro_int": reco_pro_int
        }
        response = requests.post(
            url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

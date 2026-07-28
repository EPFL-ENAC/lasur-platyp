import pandas as pd
from api.models.query import EquipmentRecommendationMatrix, EquipmentsStats
from api.services.stats.commons import BaseStatsService


class EquipmentsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_equipments_stats(self) -> EquipmentsStats:
        df = self._get_records_v3()

        total = len(df)

        if total == 0:
            return EquipmentsStats(
                total=0,
                equipment_recommendation_matrix=EquipmentRecommendationMatrix()
            )

        equipment_recommendation_matrix = self._compute_equipments_reco_matrix(
            df)

        return EquipmentsStats(
            total=total,
            equipment_recommendation_matrix=equipment_recommendation_matrix
        )

    def _compute_equipments_reco_matrix(self, df) -> EquipmentRecommendationMatrix:
        equip_cols = [
            col for col in df.columns if col.startswith("data.equipments.")]
        # Each recommendation is taken into account: one per journey for new-style
        # typo.reco.reco_inter.N records, plus the legacy typo.reco.reco_dt2.{0,1}
        # general recommendations for records collected before that change.
        rec_cols = self._reco_inter_columns(df) + self._reco_legacy_columns(df)

        matrix = EquipmentRecommendationMatrix()
        reco_totals = {
            reco: 0 for reco in matrix.__class__.model_fields.keys()}

        for row in df.iterrows():
            row_data = row[1]

            for reco_col in rec_cols:
                reco = row_data[reco_col]

                if pd.notna(reco) and reco in reco_totals:
                    reco_totals[reco] += 1
                    for equip_col in equip_cols:
                        equip = row_data[equip_col]
                        if equip in ["train_subs", "upt_subs", "other"]:
                            # Legacy (train_subs, upt_subs) or free-text
                            # (other) equipment, not tracked in the matrix
                            continue

                        if pd.notna(equip):
                            current_value = getattr(
                                getattr(matrix, reco), equip, 0)
                            setattr(getattr(matrix, reco),
                                    equip, current_value + 1)

                    # intermodal equipment
                    has_pt_or_train = any(pd.notna(row_data[col]) and row_data[col] in [
                                          "train_demi_tarif", "train_abo_gen", "tpu_unireso", "tpu_leman_pass"] for col in equip_cols)
                    has_bike_ebike = any(pd.notna(row_data[col]) and row_data[col] in [
                                         "bike", "ebike"] for col in equip_cols)

                    if has_pt_or_train and has_bike_ebike:
                        current_value = getattr(
                            getattr(matrix, reco), "inter", 0)
                        setattr(getattr(matrix, reco),
                                "inter", current_value + 1)

        for recommendation, total_count in reco_totals.items():
            getattr(matrix, recommendation).total = total_count

        return matrix

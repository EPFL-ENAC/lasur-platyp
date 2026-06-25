import pandas as pd
from api.models.query import EquipmentRecommendationMatrix, EquipmentsStats
from api.services.stats.commons import BaseStatsService


class EquipmentsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
    

    def compute_equipments_stats(self) -> EquipmentsStats:
        df = self._get_records_v2()

        total = len(df)

        if total == 0:
            return EquipmentsStats(
                total=0,
                equipment_recommendation_matrix=EquipmentRecommendationMatrix()
            )
        
        equipment_recommendation_matrix = self._compute_equipments_reco_matrix(df)

        return EquipmentsStats(
            total=total,
            equipment_recommendation_matrix=equipment_recommendation_matrix
        )
    
    
    def _compute_equipments_reco_matrix(self, df) -> EquipmentRecommendationMatrix:
        equip_cols = [col for col in df.columns if col.startswith("data.equipments.")]
        rec_cols = [f"typo.reco.reco_dt2.{i}" for i in range(1)]

        matrix = EquipmentRecommendationMatrix()

        for row in df.iterrows():
            row_data = row[1]

            for reco_col in rec_cols:
                reco = row_data[reco_col]

                if pd.notna(reco):
                    for equip_col in equip_cols:
                        equip = row_data[equip_col]

                        if pd.notna(equip):
                            current_value = getattr(getattr(matrix, reco), equip, 0)
                            setattr(getattr(matrix, reco), equip, current_value + 1)
                    
                    # intermodal equipment
                    has_pt_or_train = any(pd.notna(row_data[col]) and row_data[col] in ["train_subs", "upt_subs"] for col in equip_cols)
                    has_bike_ebike = any(pd.notna(row_data[col]) and row_data[col] in ["bike", "ebike"] for col in equip_cols)

                    if has_pt_or_train and has_bike_ebike:
                        current_value = getattr(getattr(matrix, reco), "inter", 0)
                        setattr(getattr(matrix, reco), "inter", current_value + 1)

        for recommendation in matrix.__class__.model_fields.keys():
            total_count = (df[rec_cols] == recommendation).any(axis=1).sum()
            reco_obj = getattr(matrix, recommendation)
            reco_obj.total = int(total_count)
        
        return matrix


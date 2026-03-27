import pandas as pd
from api.models.query import EquipmentRecommendationMatrix, EquipmentsStats
from api.services.stats.commons import BaseStatsService


class EquipmentsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
    

    def compute_equipments_stats(self) -> EquipmentsStats:
        df = self._get_records_v2()

        total = len(df)
        equipment_recommendation_matrix = self._compute_equipments_reco_matrix(df)

        return EquipmentsStats(
            total=total,
            equipment_recommendation_matrix=equipment_recommendation_matrix
        )
    
    
    def _compute_equipments_reco_matrix(self, df) -> EquipmentRecommendationMatrix:
        equip_cols = [f"data.equipments.{i}" for i in range(3)]
        rec_cols = [f"typo.reco.reco_dt2.{i}" for i in range(2)]

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
            
        return matrix


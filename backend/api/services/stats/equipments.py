import pandas as pd
from api.models.query import EquipmentPerRecommendation, EquipmentRecommendationMatrix, EquipmentsStats
from api.services.stats.commons import BaseStatsService

EXCLUDED_EQUIPMENT = {"train_subs", "upt_subs", "other"}
INTERMODAL_PT_OR_TRAIN = {"train_demi_tarif",
                           "train_abo_gen", "tpu_unireso", "tpu_leman_pass"}
INTERMODAL_BIKE = {"bike", "ebike"}


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
        valid_recos = set(matrix.__class__.model_fields.keys())
        reco_totals = {reco: 0 for reco in valid_recos}
        tracked_equip_fields = set(
            EquipmentPerRecommendation.model_fields.keys()) - {'total'}

        if rec_cols:
            # One row per (record, rec_col) where the recommendation is one
            # of the tracked names, built via a single vectorized reshape
            # instead of a Python-level row x rec_col x equip_col triple loop.
            reco_stack = df[rec_cols].stack()  # drops NaN by default
            reco_stack = reco_stack[reco_stack.isin(valid_recos)]
        else:
            reco_stack = pd.Series(dtype=object)

        if not reco_stack.empty:
            reco_row_idx = reco_stack.index.get_level_values(0)
            reco_pairs = pd.DataFrame(
                {'row': reco_row_idx, 'reco': reco_stack.to_numpy()})

            reco_totals_counts = reco_pairs['reco'].value_counts()
            for reco in valid_recos:
                reco_totals[reco] = int(reco_totals_counts.get(reco, 0))

            if equip_cols:
                equip_stack = df[equip_cols].stack()  # drops NaN by default
                # Legacy (train_subs, upt_subs) or free-text (other)
                # equipment, not tracked in the matrix
                equip_stack = equip_stack[~equip_stack.isin(
                    EXCLUDED_EQUIPMENT)]
                if not equip_stack.empty:
                    equip_row_idx = equip_stack.index.get_level_values(0)
                    equip_long = pd.DataFrame(
                        {'row': equip_row_idx, 'equip': equip_stack.to_numpy()})

                    # cross join: every (record, rec_col) combined with every
                    # equipment item held by that same record
                    merged = reco_pairs.merge(equip_long, on='row', how='inner')
                    equip_counts = merged.groupby(['reco', 'equip']).size()
                    for (reco, equip), count in equip_counts.items():
                        if equip in tracked_equip_fields:
                            setattr(getattr(matrix, reco), equip, int(count))

                # intermodal equipment: records holding both a PT/train item
                # and a bike/ebike item
                equip_df = df[equip_cols]
                has_pt_or_train = equip_df.isin(INTERMODAL_PT_OR_TRAIN).any(axis=1)
                has_bike_ebike = equip_df.isin(INTERMODAL_BIKE).any(axis=1)
                inter_rows = set(df.index[has_pt_or_train & has_bike_ebike])
                if inter_rows:
                    inter_reco_counts = reco_pairs[reco_pairs['row'].isin(
                        inter_rows)]['reco'].value_counts()
                    for reco, count in inter_reco_counts.items():
                        setattr(getattr(matrix, reco), 'inter', int(count))

        for recommendation, total_count in reco_totals.items():
            getattr(matrix, recommendation).total = total_count

        return matrix

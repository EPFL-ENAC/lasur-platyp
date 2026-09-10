import pandas as pd
from api.models.query import EquipmentPerRecommendation, EquipmentRecommendationMatrix, EquipmentsStats, PtPassRecommendation
from api.services.stats.commons import BaseStatsService

EXCLUDED_EQUIPMENT = {"train_subs", "upt_subs", "other"}
INTERMODAL_PT_OR_TRAIN = {"train_demi_tarif",
                           "train_abo_gen", "tpu_unireso", "tpu_leman_pass"}
INTERMODAL_BIKE = {"bike", "ebike"}

PT_PASS_COLUMN = "typo.reco.pt_pass"
# Recommendations relying on public transport: the toolkit fills pt_pass for
# every record, but the pass is only suggested to the participant alongside one
# of these. Mirror of ptRecos in collect/src/utils/ptpass.ts.
PT_RECOS = {"tpu", "pub", "train", "inter", "inter_ma_tp", "inter_tim_tp"}
# Pass types the toolkit emits, in chart order; anything else falls into
# "other", as getPtPassKey does in collect/src/utils/ptpass.ts.
PT_PASS_TYPES = ["unireso", "leman", "cff", "sncf", "other"]
# Equipment items proving the participant already holds that pass. Types absent
# from this mapping are not covered by the equipment question -- SNCF sells no
# product listed there, and "other" is a catch-all -- so their already_equipped
# count stays unknown (None) rather than a misleading zero.
PT_PASS_EQUIPMENTS = {
    "unireso": {"tpu_unireso"},
    "leman": {"tpu_leman_pass"},
    "cff": {"train_demi_tarif", "train_abo_gen"},
}


class EquipmentsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_equipments_stats(self) -> EquipmentsStats:
        df = self._get_records_v3()

        total = len(df)

        if total == 0:
            return EquipmentsStats(
                total=0,
                equipment_recommendation_matrix=EquipmentRecommendationMatrix(),
                pt_pass_recommendations=[]
            )

        equipment_recommendation_matrix = self._compute_equipments_reco_matrix(
            df)
        pt_pass_recommendations = self._compute_pt_pass_recommendations(df)

        return EquipmentsStats(
            total=total,
            equipment_recommendation_matrix=equipment_recommendation_matrix,
            pt_pass_recommendations=pt_pass_recommendations
        )

    def _compute_pt_pass_recommendations(self, df) -> list[PtPassRecommendation]:
        """Count, per public transport pass type, the participants it was
        recommended to and those already holding a matching subscription.

        Counted once per participant, not once per recommendation: the toolkit
        derives a single pass from the home-to-work origin/destination, so
        somebody commuting by public transport on two journeys still needs one
        pass.
        """
        if PT_PASS_COLUMN not in df.columns:
            return []

        rec_cols = self._reco_inter_columns(df) + self._reco_legacy_columns(df)
        if not rec_cols:
            return []

        # Only participants who were actually suggested a pass, i.e. who got a
        # public transport recommendation to go with it.
        has_pt_reco = df[rec_cols].isin(PT_RECOS).any(axis=1)
        pass_series = df.loc[has_pt_reco, PT_PASS_COLUMN].dropna()
        pass_types = pass_series.where(
            pass_series.isin(PT_PASS_TYPES), "other")
        recommended_counts = pass_types.value_counts()

        equip_cols = [
            col for col in df.columns if col.startswith("data.equipments.")]

        results = []
        for pass_type in PT_PASS_TYPES:
            recommended = int(recommended_counts.get(pass_type, 0))
            equipments = PT_PASS_EQUIPMENTS.get(pass_type)
            already_equipped = None
            if equipments is not None:
                if not equip_cols or recommended == 0:
                    already_equipped = 0
                else:
                    rows = pass_types.index[pass_types == pass_type]
                    already_equipped = int(
                        df.loc[rows, equip_cols].isin(equipments).any(axis=1).sum())
            results.append(PtPassRecommendation(
                pass_type=pass_type,
                recommended=recommended,
                already_equipped=already_equipped))

        return results

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

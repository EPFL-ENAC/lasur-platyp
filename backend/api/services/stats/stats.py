import pandas as pd
from api.models.query import Stats
from api.services.stats.emissions import EmissionsService
from api.services.stats.frequencies import FrequenciesService
from api.services.stats.links import LinksService


class StatsService:

    def compute_stats(self, df: pd.DataFrame) -> Stats:
        """Compute all statistics for equipments, constraints, travel_time, and recommendations."""
        df = self._preprocess_dataframe(df)

        freq_stats = FrequenciesService(df)
        equipments = freq_stats.compute_equipments_frequencies()
        constraints = freq_stats.compute_constraints_frequencies()
        travel_time = freq_stats.compute_travel_time_frequencies()
        recommendations = freq_stats.compute_recommendation_frequencies()
        mode_frequencies = freq_stats.compute_modes_frequencies()
        pro_mode_frequencies = freq_stats.compute_modes_pro_frequencies()
        pro_recommendations = freq_stats.compute_recommendation_pro_frequencies()

        emissions_stats = EmissionsService(df)
        mode_emissions = emissions_stats.compute_modes_emissions()
        reco_mode_emissions = emissions_stats.compute_modes_emissions(
            apply_reco=True)
        pro_mode_emissions = emissions_stats.compute_modes_pro_emissions()
        # pro_reco_mode_emissions = emissions_stats.compute_modes_pro_emissions(apply_reco=True)

        links_stats = LinksService(df)
        mode_links = links_stats.compute_mode_reco_links()
        pro_mode_links = links_stats.compute_mode_reco_pro_links()

        return Stats(
            total=len(df),
            # individual
            frequencies=[
                equipments,
                constraints,
                travel_time,
                recommendations
            ],
            mode_frequencies=mode_frequencies,
            mode_emissions=mode_emissions,
            reco_mode_emissions=reco_mode_emissions,
            mode_links=mode_links,
            # professional
            pro_frequencies=[
                pro_recommendations
            ],
            pro_mode_frequencies=pro_mode_frequencies,
            pro_mode_emissions=pro_mode_emissions,
            pro_mode_links=pro_mode_links
        )

    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the DataFrame before computing statistics."""
        # Filter only completed records
        df = self._filter_completed_records(df).copy()
        return df

    def _filter_completed_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get a DataFrame representation of the completed records.

        Args:
            filter (dict): The filter criteria for the records.
            flat (bool, optional): Whether to flatten the DataFrame. Defaults to False.
        """
        # Filter records with values in column typo.reco_dt2.0
        if 'typo.reco.reco_dt2.0' in df.columns:
            df = df[df['typo.reco.reco_dt2.0'].notna()]
            return df
        else:
            return pd.DataFrame()

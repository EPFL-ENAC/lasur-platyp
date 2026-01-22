import logging
import pandas as pd
from api.models.domain import Campaign
from api.models.query import Stats, CampaignStats, WeeklyStats
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

    def compute_campaign_stats(self, campaign: Campaign, df: pd.DataFrame) -> CampaignStats:
        """Compute statistics for a campaign."""
        if (len(df) == 0):
            return CampaignStats(
                name=campaign.name,
                company_id=campaign.company_id,
                campaign_id=campaign.id,
                nb_employees=campaign.nb_employees,
                completed_records=0,
                total_records=0,
                weekly=[]
            )
        completed = self._preprocess_dataframe(df)
        # Count the number of created records per business week
        created_per_week = df.resample('W', on='created_at').size()
        logging.debug(f"Created per week: {created_per_week}")
        # Count the number of completed records per business week
        completed_per_week = completed.resample('W', on='updated_at').size()
        logging.debug(f"Completed per week: {completed_per_week}")
        # Merge created and completed per week into a single DataFrame
        stats_df = pd.DataFrame({
            'created': created_per_week,
            'completed': completed_per_week
        }).fillna(0)
        logging.debug(f"Stats per week:\n{stats_df}")
        return CampaignStats(
            name=campaign.name,
            company_id=campaign.company_id,
            campaign_id=campaign.id,
            nb_employees=campaign.nb_employees,
            completed_records=len(completed),
            total_records=len(df),
            weekly=[
                WeeklyStats(
                    week=str(index.date()),
                    created=row['created'],
                    completed=row['completed']
                )
                for index, row in stats_df.iterrows()
            ]
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

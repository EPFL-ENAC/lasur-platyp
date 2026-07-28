import logging
import pandas as pd
from api.models.domain import Campaign
from api.models.query import Stats, CampaignStats, WeeklyStats
from api.services.stats.emissions import EmissionsService
from api.services.stats.energy import EnergyService
from api.services.stats.frequencies import FrequenciesService
from api.services.stats.links import LinksService
from api.services.stats.locations import LocationsService
from api.services.stats.behavior_change import BehaviorChangeService
from api.services.stats.equipments import EquipmentsService


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
        mode_frequencies_simple_labels = freq_stats.compute_modes_frequencies_simple_labels()
        mode_frequencies_complex_labels = freq_stats.compute_modes_frequencies_complex_labels()
        pro_mode_frequencies = freq_stats.compute_modes_pro_frequencies()
        pro_recommendations = freq_stats.compute_recommendation_pro_frequencies()

        emissions_stats = EmissionsService(df)
        mode_emissions = emissions_stats.compute_modes_emissions()
        reco_mode_emissions = emissions_stats.compute_modes_emissions(
            apply_reco=True)
        pro_mode_emissions = emissions_stats.compute_modes_pro_emissions()
        pro_reco_mode_emissions = emissions_stats.compute_modes_pro_emissions(apply_reco=True)
        mode_emission_reductions = emissions_stats.compute_modes_emission_reductions()
        pro_mode_emission_reductions = emissions_stats.compute_modes_pro_emission_reductions()

        energy_stats = EnergyService(df)
        mode_energy = energy_stats.compute_modes_energy(apply_reco=False)
        reco_mode_energy = energy_stats.compute_modes_energy(apply_reco=True)
        journey_energy_stats = energy_stats.compute_journey_energy_stats()

        links_stats = LinksService(df)
        mode_links = links_stats.compute_mode_reco_links()
        pro_mode_links = links_stats.compute_mode_reco_pro_links()

        locations_stats = LocationsService(df)
        home_location_heatmap = locations_stats.compute_home_location_heatmap()
        workplace_locations = locations_stats.get_workplaces()

        behavior_change_stats = BehaviorChangeService(df)
        behavior_change = behavior_change_stats.compute_behavior_change_stats()

        equipments_stats_service = EquipmentsService(df)
        equipments_stats = equipments_stats_service.compute_equipments_stats()

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
            mode_frequencies_simple_labels=mode_frequencies_simple_labels,
            mode_frequencies_complex_labels=mode_frequencies_complex_labels,
            mode_emissions=mode_emissions,
            reco_mode_emissions=reco_mode_emissions,
            mode_emission_reductions=mode_emission_reductions,

            mode_energy=mode_energy,
            reco_mode_energy=reco_mode_energy,
            journey_energy_stats=journey_energy_stats,

            mode_links=mode_links,

            # professional
            pro_frequencies=[
                pro_recommendations
            ],
            pro_mode_frequencies=pro_mode_frequencies,
            pro_mode_emissions=pro_mode_emissions,
            pro_reco_mode_emissions=pro_reco_mode_emissions,
            pro_mode_emission_reductions=pro_mode_emission_reductions,
            pro_mode_links=pro_mode_links,

            home_location_heatmap=home_location_heatmap,
            workplace_locations=workplace_locations,
            
            behavior_change=behavior_change,

            equipments_stats=equipments_stats
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
        # A record is completed once it has a recommendation: either the new
        # typo.reco.reco_inter.N (one per journey) or, for records collected before
        # that change, the legacy typo.reco.reco_dt2.0
        reco_cols = [col for col in df.columns if col ==
                     'typo.reco.reco_dt2.0' or col.startswith('typo.reco.reco_inter.')]
        if not reco_cols:
            return pd.DataFrame()
        df = df[df[reco_cols].notna().any(axis=1)]
        return df
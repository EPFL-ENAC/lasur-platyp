import pandas as pd
import h3
from api.models.domain import Campaign
from api.models.query import HomeWorkplaceFlow, LocationStats, WorkplaceCampaign, WorkplaceLocation
from api.services.stats.commons import BaseStatsService

WORKPLACE_COLS = {
    "data.workplace.lat": "lat",
    "data.workplace.lon": "lon",
    "data.workplace.name": "name",
    "data.workplace.address": "address",
}
ORIGIN_COLS = ["data.origin.lat", "data.origin.lon"]
# Campaigns at the same address stay separate workplaces so the map can show one dot each
WORKPLACE_KEY = ["lat", "lon", "campaign_id"]


class LocationsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    def compute_home_location_heatmap(self, resolution: int = 8) -> dict[str, int]:
        """Compute a heatmap of home locations using H3 hexagons."""
        if self.df.empty or any(col not in self.df.columns for col in ORIGIN_COLS):
            return {}
        origins = self.df[ORIGIN_COLS].dropna()
        if origins.empty:
            return {}
        hex_ids = self._to_hex_ids(origins[ORIGIN_COLS[0]], origins[ORIGIN_COLS[1]], resolution)
        return hex_ids.value_counts().to_dict()

    def compute_location_stats(self, resolution: int = 8) -> LocationStats:
        """Heatmap, workplaces and flows of the dataframe, sharing one hexagon resolution."""
        workplaces, flows = self.compute_workplaces(resolution)
        return LocationStats(
            home_location_heatmap=self.compute_home_location_heatmap(resolution),
            workplace_locations=workplaces,
            home_workplace_flows=flows,
        )

    def compute_workplaces(self, resolution: int = 8) -> tuple[list[WorkplaceLocation], list[HomeWorkplaceFlow]]:
        """Workplaces (one per coordinates and campaign) and the home hexagon -> workplace flows.

        Hexagons use the same resolution as the home heatmap so ids match.
        """
        frame = self._workplace_frame()
        if frame.empty:
            return [], []
        workplaces = self._group_workplaces(frame)
        flows = self._group_flows(frame, workplaces, resolution)
        return (
            [WorkplaceLocation(**row) for row in workplaces.to_dict(orient="records")],
            [HomeWorkplaceFlow(**row) for row in flows.to_dict(orient="records")],
        )

    @staticmethod
    def attach_campaigns(workplaces: list[WorkplaceLocation], campaigns: list[Campaign]) -> None:
        """Resolve each workplace's campaign id into campaign and company names."""
        lookup = {
            campaign.id: WorkplaceCampaign(
                id=campaign.id, name=campaign.name, company_name=campaign.company.name)
            for campaign in campaigns
        }
        missing = sorted({wp.campaign_id for wp in workplaces} - set(lookup))
        if missing:
            raise ValueError(f"Campaigns {missing} not found for workplace enrichment")
        for workplace in workplaces:
            workplace.campaign = lookup[workplace.campaign_id]

    def _workplace_frame(self) -> pd.DataFrame:
        """Rows with workplace coordinates; missing optional columns are re-created as NaN."""
        required = ["data.workplace.lat", "data.workplace.lon", "campaign_id"]
        if self.df.empty or any(col not in self.df.columns for col in required):
            return pd.DataFrame()
        columns = [*WORKPLACE_COLS.keys(), *ORIGIN_COLS, "campaign_id"]
        frame = self.df.reindex(columns=columns).rename(columns=WORKPLACE_COLS)
        frame = frame.dropna(subset=["lat", "lon"])
        if frame["campaign_id"].isna().any():
            raise ValueError("Records with a workplace but no campaign id")
        frame["campaign_id"] = frame["campaign_id"].astype(int)
        return frame

    @staticmethod
    def _group_workplaces(frame: pd.DataFrame) -> pd.DataFrame:
        """One row per (lat, lon, campaign_id) with a stable id and counts."""
        grouped = (
            frame.groupby(WORKPLACE_KEY, sort=True)
            .agg(
                name=("name", "first"),
                address=("address", "first"),
                count=("lat", "size"),
            )
            .reset_index()
        )
        grouped["id"] = range(len(grouped))
        text_cols = ["name", "address"]
        grouped[text_cols] = grouped[text_cols].astype(object).where(grouped[text_cols].notna(), None)
        return grouped

    def _group_flows(self, frame: pd.DataFrame, workplaces: pd.DataFrame, resolution: int) -> pd.DataFrame:
        """Count records per (home hexagon, workplace id); rows without origin are skipped."""
        with_origin = frame.dropna(subset=ORIGIN_COLS).copy()
        if with_origin.empty:
            return pd.DataFrame(columns=["hex_id", "workplace_id", "count"])
        with_origin["hex_id"] = self._to_hex_ids(
            with_origin[ORIGIN_COLS[0]], with_origin[ORIGIN_COLS[1]], resolution).values
        merged = with_origin.merge(workplaces[[*WORKPLACE_KEY, "id"]], on=WORKPLACE_KEY)
        return (
            merged.groupby(["hex_id", "id"], sort=True)
            .size()
            .reset_index(name="count")
            .rename(columns={"id": "workplace_id"})
        )

    @staticmethod
    def _to_hex_ids(lat: pd.Series, lon: pd.Series, resolution: int) -> pd.Series:
        """H3 cell id per coordinate pair, shared by heatmap and flows."""
        return pd.Series(
            [h3.latlng_to_cell(la, lo, resolution) for la, lo in zip(lat, lon)],
            index=lat.index,
        )

import pandas as pd
import h3
from api.models.domain import Campaign
from api.models.query import HomeWorkplaceFlow, WorkplaceCampaign, WorkplaceLocation
from api.services.stats.commons import BaseStatsService

WORKPLACE_COLS = {
    "data.workplace.lat": "lat",
    "data.workplace.lon": "lon",
    "data.workplace.name": "name",
    "data.workplace.address": "address",
}
ORIGIN_COLS = ["data.origin.lat", "data.origin.lon"]


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

    def compute_workplaces(self, resolution: int = 8) -> tuple[list[WorkplaceLocation], list[HomeWorkplaceFlow]]:
        """Unique workplaces (by coordinates) and the home hexagon -> workplace flows.

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
        """Resolve each workplace's campaign ids into campaign and company names."""
        lookup = {
            campaign.id: WorkplaceCampaign(
                id=campaign.id, name=campaign.name, company_name=campaign.company.name)
            for campaign in campaigns
        }
        for workplace in workplaces:
            missing = [cid for cid in workplace.campaign_ids if cid not in lookup]
            if missing:
                raise ValueError(
                    f"Campaigns {missing} not found for workplace enrichment")
            workplace.campaigns = [lookup[cid] for cid in workplace.campaign_ids]

    def _workplace_frame(self) -> pd.DataFrame:
        """Rows with workplace coordinates; missing optional columns are re-created as NaN."""
        required = ["data.workplace.lat", "data.workplace.lon"]
        if self.df.empty or any(col not in self.df.columns for col in required):
            return pd.DataFrame()
        columns = [*WORKPLACE_COLS.keys(), *ORIGIN_COLS, "campaign_id"]
        frame = self.df.reindex(columns=columns).rename(columns=WORKPLACE_COLS)
        return frame.dropna(subset=["lat", "lon"])

    @staticmethod
    def _group_workplaces(frame: pd.DataFrame) -> pd.DataFrame:
        """One row per (lat, lon) with a stable id, counts and campaign ids."""
        grouped = (
            frame.groupby(["lat", "lon"], sort=True)
            .agg(
                name=("name", "first"),
                address=("address", "first"),
                count=("lat", "size"),
                campaign_ids=("campaign_id", lambda s: sorted(s.dropna().astype(int).unique().tolist())),
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
        merged = with_origin.merge(workplaces[["lat", "lon", "id"]], on=["lat", "lon"])
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

import pandas as pd
import h3
from api.services.stats.commons import BaseStatsService

class LocationsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
    
    def compute_home_location_heatmap(self, resolution: int = 8, min_count: int = 0) -> dict[str, int]:
        """Compute a heatmap of home locations using H3 hexagons."""

        return self._compute_location_heatmap("data.origin.lat", "data.origin.lon", resolution, min_count)
    
    def compute_workplace_location_heatmap(self, resolution: int = 8, min_count: int = 0) -> dict[str, int]:
        """Compute a heatmap of workplace locations using H3 hexagons."""
        return self._compute_location_heatmap("data.workplace.lat", "data.workplace.lon", resolution, min_count)

    def get_workplaces(self) -> list[dict]:
        """Get a list of unique workplaces with their coordinates."""
        workplaces = self.df[["data.workplace.lat", "data.workplace.lon"]].dropna().drop_duplicates()
        return workplaces.rename(columns={"data.workplace.lat": "lat", "data.workplace.lon": "lon"}).to_dict(orient="records")

    def _compute_location_heatmap(self, lat_col: str, lon_col: str, resolution: int = 8, min_count: int = 0) -> dict[str, int]:
        """Compute a heatmap of locations using H3 hexagons."""
        # Early return if dataframe is empty or required columns are missing
        if self.df.empty or lat_col not in self.df.columns or lon_col not in self.df.columns:
            return {}
        
        # Work on a filtered view with non-null coordinates to avoid errors in h3.latlng_to_cell
        location_df = self.df[[lat_col, lon_col]].dropna(subset=[lat_col, lon_col])
        if location_df.empty:
            return {}
        
        hex_ids = [
            h3.latlng_to_cell(lat, lon, resolution)
            for lat, lon in zip(location_df[lat_col], location_df[lon_col])
        ]
        # Group by hex_id and count occurrences
        counts = pd.Series(hex_ids).value_counts()
        # Filter out hexagons with counts below the minimum
        if min_count > 0:
            counts = counts[counts >= min_count]
        
        return counts.to_dict()


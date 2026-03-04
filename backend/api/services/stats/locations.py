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

    def _compute_location_heatmap(self, lat_col: str, lon_col: str, resolution: int = 8, min_count: int = 0) -> dict[str, int]:
        """Compute a heatmap of locations using H3 hexagons."""
        self.df["hex_id"] = [
            h3.latlng_to_cell(lat, lon, resolution) 
            for lat, lon in zip(self.df[lat_col], self.df[lon_col])
        ]
        # Group by hex_id and count occurrences
        counts = self.df["hex_id"].value_counts()
        
        # Filter out hexagons with counts below the minimum
        if min_count > 0:
            counts = counts[counts >= min_count]
        
        if self.df.empty:
            return {}
        
        return counts.to_dict()


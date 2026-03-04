import pandas as pd
import h3
from api.services.stats.commons import BaseStatsService

class LocationsService(BaseStatsService):

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
    
    def compute_home_location_heatmap(self, resolution: int = 8) -> dict[str, int]:
        """Compute a heatmap of home locations using H3 hexagons."""

        self.df["hex_id"] = [
            h3.latlng_to_cell(lat, lon, resolution) 
            for lat, lon in zip(self.df["data.origin.lat"], self.df["data.origin.lon"])
        ]
        # Group by hex_id and count occurrences
        counts = self.df["hex_id"].value_counts()
        return counts.to_dict()


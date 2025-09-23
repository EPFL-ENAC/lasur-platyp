from typing import Dict, List
from api.config import config
from api.models.isochrones import IsochronePoisData, IsochroneResponse, FeatureCollection
import requests


class IsochronesService:

    def __init__(self):
        self.url = config.LASUR_API_URL
        self.key = config.LASUR_API_KEY
        self.headers = {
            "x-api-key": self.key,
            "Content-Type": "application/json"
        }

    def compute_isochrones(self, data: IsochronePoisData) -> IsochroneResponse:
        response = requests.post(
            f"{self.url}/isochrones/compute",
            json=data.model_dump(),
            headers=self.headers
        )
        response.raise_for_status()
        return IsochroneResponse.model_validate(response.json())

    def get_available_modes(self) -> Dict[str, str]:

        response = requests.get(
            f"{self.url}/isochrones/modes",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_pois(self, data) -> FeatureCollection:
        response = requests.post(
            f"{self.url}/isochrones/pois",
            json=data.model_dump(),
            headers=self.headers
        )
        response.raise_for_status()
        return FeatureCollection.model_validate(response.json())

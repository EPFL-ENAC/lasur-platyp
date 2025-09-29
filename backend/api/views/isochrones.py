from ast import Dict, List
import logging
from fastapi import APIRouter, Depends, Response
from api.auth import kc_service, User
from ..models.isochrones import IsochronePoisData, IsochroneResponse, FeatureCollection, PoisData, PoisData
from api.services.isochrones import IsochronesService

router = APIRouter()


@router.get("/_modes")
async def get_available_modes() -> Response:
    """
    Retrieve available transportation modes for isochrone calculations.
    """
    service = IsochronesService()
    return service.get_available_modes()


@router.post("/_compute", response_model=IsochroneResponse, response_model_exclude_none=True)
async def compute_isochrones(
    data: IsochronePoisData,
) -> IsochroneResponse:
    """
    Compute isochrones and optionally retrieve points of interest (POIs) within the isochrones.

    - **lon**: Longitude of the starting point.
    - **lat**: Latitude of the starting point.
    - **cutoffSec**: List of cutoff times in seconds for which to compute isochrones.
    - **datetime**: ISO 8601 formatted datetime string representing the departure time.
    - **mode**: Transportation mode (e.g., driving, walking, cycling).
    - **bikeSpeed**: Optional cycling speed in km/h, required if mode includes cycling.
    - **categories**: Optional list of POI categories to filter.

    Returns a GeoJSON FeatureCollection of isochrones and optionally a FeatureCollection of POIs.
    """
    service = IsochronesService()
    return service.compute_isochrones(data)


@router.post("/_pois", response_model=FeatureCollection, response_model_exclude_none=True)
async def get_pois(
    data: PoisData,
) -> FeatureCollection:
    service = IsochronesService()
    return service.get_pois(data)

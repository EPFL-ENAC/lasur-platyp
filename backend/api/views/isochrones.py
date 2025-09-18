import logging
from fastapi import APIRouter, Depends
from api.auth import kc_service, User
from ..models.isochrones import IsochronePoisData, IsochroneResponse, FeatureCollection
from api.services.isochrones import IsochronesService

router = APIRouter()


@router.post("/_compute", response_model=IsochroneResponse, response_model_exclude_none=True)
async def compute_isochrones(
    data: IsochronePoisData,
    user: User = Depends(kc_service.require_admin())
) -> IsochroneResponse:
    """
    Compute isochrones and optionally retrieve points of interest (POIs) within the isochrones.

    - **lon**: Longitude of the starting point.
    - **lat**: Latitude of the starting point.
    - **cutoffSec**: List of cutoff times in seconds for which to compute isochrones.
    - **datetime**: ISO 8601 formatted datetime string representing the departure time.
    - **categories**: Optional list of POI categories to filter.

    Returns a GeoJSON FeatureCollection of isochrones and optionally a FeatureCollection of POIs.
    """
    service = IsochronesService()
    return service.compute_isochrones(data)

import h3
import numpy as np
import pandas as pd
import pytest

from api.models.domain import Campaign, Company
from api.models.query import HomeWorkplaceFlow, LocationStats, WorkplaceLocation
from api.services.stats.locations import LocationsService
from api.services.stats.stats import StatsService

EPFL = (46.5191, 6.5668)
UNIL = (46.5225, 6.5804)
HOME_A = (46.5300, 6.6000)
HOME_B = (46.5400, 6.6200)


def workplace_df() -> pd.DataFrame:
    return pd.DataFrame({
        "campaign_id": [2, 1, 1, 3],
        "data.workplace.lat": [UNIL[0], EPFL[0], EPFL[0], UNIL[0]],
        "data.workplace.lon": [UNIL[1], EPFL[1], EPFL[1], UNIL[1]],
        "data.workplace.name": [None, "EPFL", "EPFL bis", "UNIL"],
        "data.workplace.address": ["Unicentre", None, "Route Cantonale", "Unicentre"],
        "data.origin.lat": [HOME_A[0], HOME_A[0], HOME_B[0], HOME_A[0]],
        "data.origin.lon": [HOME_A[1], HOME_A[1], HOME_B[1], HOME_A[1]],
    })


def test_compute_workplaces_groups_by_coordinates_and_campaign():
    workplaces, _ = LocationsService(workplace_df()).compute_workplaces()

    # UNIL hosts two campaigns: they stay separate workplaces so the map can draw one dot each
    assert workplaces == [
        WorkplaceLocation(id=0, lat=EPFL[0], lon=EPFL[1], name="EPFL",
                          address="Route Cantonale", count=2, campaign_id=1),
        WorkplaceLocation(id=1, lat=UNIL[0], lon=UNIL[1], name=None,
                          address="Unicentre", count=1, campaign_id=2),
        WorkplaceLocation(id=2, lat=UNIL[0], lon=UNIL[1], name="UNIL",
                          address="Unicentre", count=1, campaign_id=3),
    ]


def test_compute_location_stats_bundles_heatmap_workplaces_and_flows():
    service = LocationsService(workplace_df())

    stats = service.compute_location_stats()

    assert stats.home_location_heatmap == service.compute_home_location_heatmap()
    workplaces, flows = service.compute_workplaces()
    assert stats.workplace_locations == workplaces
    assert stats.home_workplace_flows == flows
    assert LocationsService(pd.DataFrame()).compute_location_stats() == LocationStats(
        home_location_heatmap={}, workplace_locations=[], home_workplace_flows=[])


def test_compute_workplaces_without_campaign_id_raises():
    df = workplace_df()
    df.loc[0, "campaign_id"] = np.nan

    with pytest.raises(ValueError, match="no campaign id"):
        LocationsService(df).compute_workplaces()


def test_compute_workplaces_without_name_column():
    df = workplace_df().drop(columns=["data.workplace.name"])

    workplaces, _ = LocationsService(df).compute_workplaces()

    assert [wp.name for wp in workplaces] == [None, None, None]
    assert [wp.address for wp in workplaces] == ["Route Cantonale", "Unicentre", "Unicentre"]


def test_compute_workplaces_flows_match_heatmap_hexes():
    service = LocationsService(workplace_df())
    heatmap = service.compute_home_location_heatmap()

    _, flows = service.compute_workplaces()

    hex_a = h3.latlng_to_cell(*HOME_A, 8)
    hex_b = h3.latlng_to_cell(*HOME_B, 8)
    assert sorted(flows, key=lambda f: (f.hex_id, f.workplace_id)) == sorted([
        HomeWorkplaceFlow(hex_id=hex_a, workplace_id=0, count=1),
        HomeWorkplaceFlow(hex_id=hex_a, workplace_id=1, count=1),
        HomeWorkplaceFlow(hex_id=hex_a, workplace_id=2, count=1),
        HomeWorkplaceFlow(hex_id=hex_b, workplace_id=0, count=1),
    ], key=lambda f: (f.hex_id, f.workplace_id))
    assert {f.hex_id for f in flows} <= set(heatmap)
    assert sum(f.count for f in flows) == sum(heatmap.values())


def test_compute_workplaces_record_without_origin():
    df = workplace_df()
    df.loc[3, ["data.origin.lat", "data.origin.lon"]] = np.nan

    workplaces, flows = LocationsService(df).compute_workplaces()

    assert workplaces[2].count == 1
    assert sum(f.count for f in flows if f.workplace_id == 2) == 0


def test_compute_workplaces_empty_or_missing_columns():
    assert LocationsService(pd.DataFrame()).compute_workplaces() == ([], [])
    df = pd.DataFrame({"data.origin.lat": [46.5], "data.origin.lon": [6.5]})
    assert LocationsService(df).compute_workplaces() == ([], [])


def test_attach_campaigns():
    workplaces, _ = LocationsService(workplace_df()).compute_workplaces()
    epfl = Company(name="EPFL")
    campaigns = [
        Campaign(id=1, name="Spring", company=epfl),
        Campaign(id=2, name="Autumn", company=epfl),
        Campaign(id=3, name="Winter", company=Company(name="UNIL")),
    ]

    LocationsService.attach_campaigns(workplaces, campaigns)

    assert [(wp.campaign.id, wp.campaign.name, wp.campaign.company_name) for wp in workplaces] == [
        (1, "Spring", "EPFL"), (2, "Autumn", "EPFL"), (3, "Winter", "UNIL")]


def test_attach_campaigns_missing_raises():
    workplaces, _ = LocationsService(workplace_df()).compute_workplaces()

    with pytest.raises(ValueError, match="Campaigns \\[2, 3\\] not found"):
        LocationsService.attach_campaigns(
            workplaces, [Campaign(id=1, name="Spring", company=Company(name="EPFL"))])


def test_compute_stats_includes_workplaces_and_flows():
    df = pd.read_csv("tests/data/records.csv")

    stats = StatsService().compute_stats(df)

    assert stats.workplace_locations[0].id == 0
    assert stats.workplace_locations[0].name is None
    assert stats.workplace_locations[0].address
    assert all(isinstance(f, HomeWorkplaceFlow) for f in stats.home_workplace_flows)
    assert {f.hex_id for f in stats.home_workplace_flows} <= set(stats.home_location_heatmap)

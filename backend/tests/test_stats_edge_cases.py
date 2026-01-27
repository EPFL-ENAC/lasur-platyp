import pandas as pd
import numpy as np
from api.services.stats.links import LinksService
from api.services.stats.stats import StatsService
from api.models.query import Frequencies, Links
from api.services.stats.frequencies import FrequenciesService
from api.services.stats.emissions import EmissionsService


def test_empty_dataframe():
    """Test that services handle empty DataFrames correctly."""
    df = pd.DataFrame()

    freq_service = FrequenciesService(df)
    emissions_service = EmissionsService(df)
    links_service = LinksService(df)

    # Frequencies service should handle empty dataframe
    result = freq_service.compute_equipments_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 0
    assert result.data == []

    result = freq_service.compute_travel_time_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 0
    assert result.data == []

    result = freq_service.compute_modes_frequencies()
    assert isinstance(result, list)
    assert all(isinstance(f, Frequencies) for f in result)

    # Emissions service should handle empty dataframe
    result = emissions_service.compute_modes_emissions()
    assert isinstance(result, list)
    assert result == []

    result = emissions_service.compute_modes_pro_emissions()
    assert isinstance(result, list)
    assert result == []

    # Links service should handle empty dataframe
    result = links_service.compute_mode_reco_links()
    assert isinstance(result, Links)
    assert result.total == 0
    assert result.data == []


def test_missing_columns():
    """Test that services handle missing columns gracefully."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "data.origin.lat": [48.85, 48.86, 48.87],
            "data.origin.lon": [2.35, 2.36, 2.37],
        }
    )

    freq_service = FrequenciesService(df)
    emissions_service = EmissionsService(df)

    # Should handle missing travel_time column
    result = freq_service.compute_travel_time_frequencies()
    assert isinstance(result, Frequencies)
    assert result.field == "travel_time"
    assert result.data == []

    # Should handle missing recommendation column
    result = freq_service.compute_recommendation_frequencies()
    assert isinstance(result, Frequencies)
    assert result.field == "reco_dt2"
    assert result.data == []

    # EmissionsService should now handle missing workplace coordinates gracefully
    result = emissions_service.compute_modes_emissions()
    assert isinstance(result, list)
    # Without workplace coordinates, all distances should be 0, so no emissions
    assert result == []


def test_all_nan_values():
    """Test that services handle DataFrames with all NaN values."""
    df = pd.DataFrame(
        {
            "data.equipments.0": [np.nan, np.nan, np.nan],
            "data.constraints.0": [np.nan, np.nan, np.nan],
            "data.travel_time": [np.nan, np.nan, np.nan],
        }
    )

    freq_service = FrequenciesService(df)

    result = freq_service.compute_equipments_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    assert result.data == []

    result = freq_service.compute_constraints_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    assert result.data == []

    result = freq_service.compute_travel_time_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    assert result.data == []


def test_single_row_dataframe():
    """Test that services handle single-row DataFrames correctly."""
    df = pd.DataFrame(
        {
            "data.equipments.0": ["bike"],
            "data.constraints.0": ["night"],
            "data.travel_time": ["30"],
            "typo.reco.reco_dt2.0": ["train"],
            "data.origin.lat": [48.85],
            "data.origin.lon": [2.35],
            "data.workplace.lat": [48.86],
            "data.workplace.lon": [2.36],
        }
    )

    freq_service = FrequenciesService(df)

    result = freq_service.compute_equipments_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 1
    assert len(result.data) == 1
    assert result.data[0].value == "bike"
    assert result.data[0].count == 1

    result = freq_service.compute_travel_time_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 1
    assert len(result.data) == 1
    assert result.data[0].value == "30"
    assert result.data[0].count == 1


def test_zero_journeys():
    """Test that emissions service handles zero journeys correctly."""
    df = pd.DataFrame(
        {
            "data.freq_mod_walking": [0, 0, 0],
            "data.origin.lat": [48.85, 48.86, 48.87],
            "data.origin.lon": [2.35, 2.36, 2.37],
            "data.workplace.lat": [48.86, 48.87, 48.88],
            "data.workplace.lon": [2.36, 2.37, 2.38],
        }
    )

    service = EmissionsService(df)
    result = service.compute_modes_emissions()

    # Check that the service doesn't crash with zero journeys
    assert isinstance(result, list)
    # Zero journeys should either be filtered out or produce zero emissions
    for emission in result:
        if emission.mode == "walking" and emission.emissions is not None:
            assert emission.emissions <= 0.001


def test_invalid_data_types():
    """Test that services handle invalid data types gracefully."""
    df = pd.DataFrame(
        {
            "data.travel_time": ["invalid", "30", 45],
            "data.equipments.0": ["bike", None, "car"],
        }
    )

    freq_service = FrequenciesService(df)

    result = freq_service.compute_travel_time_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3

    result = freq_service.compute_equipments_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    assert len(result.data) == 2  # Only bike and car, None is dropped


def test_negative_values():
    """Test that services handle negative values."""
    df = pd.DataFrame(
        {
            "data.freq_mod_walking": [1, -1, 2],
            "data.origin.lat": [48.85, 48.86, 48.87],
            "data.origin.lon": [2.35, 2.36, 2.37],
            "data.workplace.lat": [48.86, 48.87, 48.88],
            "data.workplace.lon": [2.36, 2.37, 2.38],
        }
    )

    service = EmissionsService(df)

    # Emissions service might produce unexpected results with negative values
    # but should not crash
    result = service.compute_modes_emissions()
    assert isinstance(result, list)


def test_large_values():
    """Test that services handle large numerical values."""
    df = pd.DataFrame(
        {
            "data.travel_time": ["1000", "2000", "3000"],
            "data.freq_mod_car": [1000, 2000, 3000],
            "data.origin.lat": [48.85, 48.86, 48.87],
            "data.origin.lon": [2.35, 2.36, 2.37],
            "data.workplace.lat": [48.86, 48.87, 48.88],
            "data.workplace.lon": [2.36, 2.37, 2.38],
        }
    )

    freq_service = FrequenciesService(df)
    emissions_service = EmissionsService(df)

    result = freq_service.compute_travel_time_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    assert len(result.data) == 3

    result = emissions_service.compute_modes_emissions()
    assert isinstance(result, list)


def test_nan_coordinates():
    """Test that services handle NaN coordinates in distance calculations."""
    df = pd.DataFrame(
        {
            "data.origin.lat": [48.85, np.nan, 48.87, 48.87],
            "data.origin.lon": [2.35, 2.36, np.nan, 2.36],
            "data.workplace.lat": [48.86, 48.87, 48.88, np.nan],
            "data.workplace.lon": [np.nan, 2.36, 2.38, 2.37],
        }
    )

    service = EmissionsService(df)

    # Should not crash with NaN coordinates
    result = service.compute_modes_emissions()
    assert isinstance(result, list)

    # Distance should be 0 for NaN coordinates
    assert np.all(service.df["distance_km"] == 0)


def test_mixed_data_versions():
    """Test that services handle mixed v1 and v2 data correctly."""
    df = pd.DataFrame(
        {
            "data.version": [np.nan, np.nan, "2.0", "2.1"],
            "data.freq_mod_walking": [1, 2, np.nan, np.nan],
            "data.freq_mod_journeys.0.days": [np.nan, np.nan, 3, 4],
            "data.freq_mod_journeys.0.modes.0": [np.nan, np.nan, "walking", "walking"],
            "data.origin.lat": [48.85, 48.86, 48.87, 48.88],
            "data.origin.lon": [2.35, 2.36, 2.37, 2.38],
            "data.workplace.lat": [48.86, 48.87, 48.88, 48.89],
            "data.workplace.lon": [2.36, 2.37, 2.38, 2.39],
        }
    )

    stats = StatsService()
    df = stats._preprocess_dataframe(df)

    freq_service = FrequenciesService(df)
    emissions_service = EmissionsService(df)

    result = freq_service.compute_modes_frequencies()
    assert isinstance(result, list)

    result = emissions_service.compute_modes_emissions()
    assert isinstance(result, list)


def test_special_characters():
    """Test that services handle special characters in string values."""
    df = pd.DataFrame(
        {
            "data.equipments.0": ["bike", "bîké", "bike_(special)"],
            "data.constraints.0": ["nîght", "hêavy", "none"],
        }
    )

    freq_service = FrequenciesService(df)

    result = freq_service.compute_equipments_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    assert len(result.data) == 3

    result = freq_service.compute_constraints_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    assert len(result.data) == 3


def test_duplicate_values():
    """Test that services handle duplicate values correctly."""
    df = pd.DataFrame(
        {
            "data.equipments.0": ["bike", "bike", "bike"],
            "data.equipments.1": ["car", "car", "car"],
            "data.equipments.2": ["bike", "car", "bike"],
        }
    )

    freq_service = FrequenciesService(df)

    result = freq_service.compute_equipments_frequencies()
    assert isinstance(result, Frequencies)
    assert result.total == 3
    # Bike appears 5 times (3 in equipment.0, 2 in equipment.2)
    # Car appears 4 times (3 in equipment.1, 1 in equipment.2)
    bike_count = next(
        (f.count for f in result.data if f.value == "bike"), None)
    car_count = next((f.count for f in result.data if f.value == "car"), None)
    assert bike_count == 5
    assert car_count == 4

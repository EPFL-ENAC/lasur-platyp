"""
Tests for professional travel emission reductions.

This module tests the compute_modes_pro_emission_reductions() functionality,
which calculates CO2 savings when professional travel recommendations are applied.
"""

import pandas as pd
import pytest
import h3
from api.services.stats.emissions import EmissionsService
from api.services.stats.stats import StatsService
from api.models.query import EmissionReductions


def create_pro_journey_dataframe(journeys: list[dict]) -> pd.DataFrame:
    """
    Create test DataFrame with professional journey data.
    
    Args:
        journeys: List of journey dictionaries with keys:
            - current_mode: str (e.g., 'plane', 'car', 'train')
            - reco_mode: str (e.g., 'train', 'bike', 'avoid') or None
            - days: int (annual frequency)
            - hex_id: str (destination H3 hex)
            - workplace_lat: float
            - workplace_lon: float
            - journey_idx: int (0, 1, 2, ...)
    
    Returns:
        pd.DataFrame with columns matching the professional journey structure
    """
    # Initialize base columns
    base_data = {
        'data.workplace.lat': [],
        'data.workplace.lon': [],
        'data.version': [],  # Required for v2 filtering
    }
    
    # Group journeys by record to handle multiple journeys per record
    journeys_by_record = {}
    for journey in journeys:
        record_id = journey.get('record_id', 0)
        if record_id not in journeys_by_record:
            journeys_by_record[record_id] = []
        journeys_by_record[record_id].append(journey)
    
    # Build dataframe rows
    for record_id, record_journeys in journeys_by_record.items():
        row = {
            'data.workplace.lat': record_journeys[0]['workplace_lat'],
            'data.workplace.lon': record_journeys[0]['workplace_lon'],
            'data.version': '2.0',  # Mark as v2 data
        }
        
        # Add journey-specific columns using the correct data.freq_mod_pro_journeys format
        for journey in record_journeys:
            idx = journey['journey_idx']
            row[f'data.freq_mod_pro_journeys.{idx}.mode'] = journey['current_mode']
            row[f'data.freq_mod_pro_journeys.{idx}.days'] = journey['days']
            row[f'data.freq_mod_pro_journeys.{idx}.hex_id'] = journey['hex_id']
            if journey.get('reco_mode'):
                row[f'typo.reco_pro.reco_pros.{idx}'] = journey['reco_mode']
        
        # Add row data to base columns
        for key, value in row.items():
            if key not in base_data:
                base_data[key] = []
            base_data[key].append(value)
    
    # Fill missing values with None for columns that don't exist in all rows
    max_len = len(journeys_by_record)
    for key in base_data:
        if len(base_data[key]) < max_len:
            base_data[key].extend([None] * (max_len - len(base_data[key])))
    
    return pd.DataFrame(base_data)


def assert_emission_reductions_equal(result: list[EmissionReductions], expected: list[EmissionReductions]):
    """Helper to assert emission reductions match expected values."""
    assert len(result) == len(expected), f"Expected {len(expected)} reductions, got {len(result)}"
    
    # Sort both by mode for consistent comparison
    result_sorted = sorted(result, key=lambda x: x.mode or '')
    expected_sorted = sorted(expected, key=lambda x: x.mode or '')
    
    for res, exp in zip(result_sorted, expected_sorted):
        assert res.mode == exp.mode, f"Mode mismatch: {res.mode} != {exp.mode}"
        assert res.total == exp.total, f"Total mismatch for {res.mode}: {res.total} != {exp.total}"
        assert res.reduced == pytest.approx(exp.reduced, abs=0.01), \
            f"Reduced mismatch for {res.mode}: {res.reduced} != {exp.reduced}"


# ============================================================================
# BASIC FUNCTIONALITY TESTS
# ============================================================================

def test_simple_plane_to_train_reduction():
    """Test basic emission reduction: plane → train recommendation."""
    # Workplace at (46.5, 6.5), destination 100km away
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)  # ~100km east
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'plane',
        'reco_mode': 'train',
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Check that result has expected structure
    assert len(result) == 1
    assert result[0].mode == 'train'
    assert result[0].total == 1
    # Savings should be positive and significant (plane to train is a big reduction)
    # Actual value ~470 kg based on calculated distance
    assert result[0].reduced > 400  # At least 400kg savings
    assert result[0].reduced < 600  # But not more than 600kg


def test_multiple_journeys_same_reco_mode():
    """Test multiple journeys with same recommendation aggregate correctly."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex1 = h3.latlng_to_cell(46.5, 7.5, 7)  # ~100km
    dest_hex2 = h3.latlng_to_cell(46.5, 8.5, 7)  # ~200km
    
    journeys = [
        {
            'record_id': 0,
            'current_mode': 'plane',
            'reco_mode': 'train',
            'days': 10,
            'hex_id': dest_hex1,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 0
        },
        {
            'record_id': 0,
            'current_mode': 'car',
            'reco_mode': 'train',
            'days': 5,
            'hex_id': dest_hex2,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 1
        }
    ]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Both journeys recommend train, should aggregate
    assert len(result) == 1
    assert result[0].mode == 'train'
    # Total is number of records (people), not journeys
    assert result[0].total == 1
    # Savings should be sum of both journeys
    assert result[0].reduced > 0


def test_multiple_journeys_different_reco_modes():
    """Test multiple journeys with different recommendations."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex1 = h3.latlng_to_cell(46.5, 7.5, 7)  # ~100km
    dest_hex2 = h3.latlng_to_cell(46.6, 6.6, 7)  # ~10km
    
    journeys = [
        {
            'record_id': 0,
            'current_mode': 'plane',
            'reco_mode': 'train',
            'days': 10,
            'hex_id': dest_hex1,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 0
        },
        {
            'record_id': 0,
            'current_mode': 'car',
            'reco_mode': 'bike',
            'days': 5,
            'hex_id': dest_hex2,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 1
        }
    ]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Should have two separate reductions
    assert len(result) == 2
    modes = {r.mode for r in result}
    assert modes == {'train', 'bike'}
    
    for r in result:
        assert r.total == 1
        assert r.reduced > 0


# ============================================================================
# EDGE CASES
# ============================================================================

def test_same_mode_zero_savings_excluded():
    """Test that same mode (zero savings) is excluded by default."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'train',
        'reco_mode': 'train',  # Same mode
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Should be empty (zero savings excluded)
    assert len(result) == 0


def test_avoid_recommendation_maximum_savings():
    """Test 'avoid' recommendation gives maximum savings (current emissions)."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)  # ~100km
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'plane',
        'reco_mode': 'avoid',
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Avoid means reco_emissions = 0, so savings = current_emissions
    assert len(result) == 1
    assert result[0].mode == 'avoid'
    # Should be close to current plane emissions (actual: ~470kg)
    assert result[0].reduced > 400  # At least 400kg
    assert result[0].reduced < 600  # But not more than 600kg


def test_negative_savings_excluded_by_default():
    """Test that recommendations increasing emissions are excluded by default."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'bike',
        'reco_mode': 'car',  # Worse for environment
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions(include_negative=False)
    
    # Should be excluded (negative savings)
    assert len(result) == 0


def test_negative_savings_included_when_requested():
    """Test that negative savings are included when include_negative=True."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)  # ~100km
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'bike',
        'reco_mode': 'car',  # Worse for environment
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions(include_negative=True)
    
    # Should be included with negative value
    assert len(result) == 1
    assert result[0].mode == 'car'
    assert result[0].reduced < 0  # Negative savings


def test_missing_recommendation_skipped():
    """Test that journeys without recommendations are skipped."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'plane',
        'reco_mode': None,  # No recommendation
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Should be empty (no recommendations)
    assert len(result) == 0


def test_missing_workplace_coords_skipped():
    """Test that journeys with missing workplace coordinates are skipped."""
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'plane',
        'reco_mode': 'train',
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': None,  # Missing
        'workplace_lon': None,  # Missing
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Should be empty (can't calculate distance)
    assert len(result) == 0


def test_zero_or_negative_days_skipped():
    """Test that journeys with zero or negative days are skipped."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)
    
    journeys = [
        {
            'record_id': 0,
            'current_mode': 'plane',
            'reco_mode': 'train',
            'days': 0,  # Zero days
            'hex_id': dest_hex,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 0
        },
        {
            'record_id': 1,
            'current_mode': 'plane',
            'reco_mode': 'train',
            'days': -5,  # Negative days
            'hex_id': dest_hex,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 0
        }
    ]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Should be empty (invalid days)
    assert len(result) == 0


# ============================================================================
# MODE NORMALIZATION TESTS
# ============================================================================

def test_mode_normalization():
    """Test that mode names are normalized correctly."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.6, 6.6, 7)  # ~10km
    
    journeys = [
        {
            'record_id': 0,
            'current_mode': 'plane',
            'reco_mode': 'velo',  # Should normalize to 'bike'
            'days': 5,
            'hex_id': dest_hex,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 0
        },
        {
            'record_id': 1,
            'current_mode': 'plane',
            'reco_mode': 'tpu',  # Should normalize to 'pub'
            'days': 5,
            'hex_id': dest_hex,
            'workplace_lat': workplace_lat,
            'workplace_lon': workplace_lon,
            'journey_idx': 0
        }
    ]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # Should have normalized mode names
    assert len(result) == 2
    modes = {r.mode for r in result}
    assert modes == {'bike', 'pub'}


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_annual_frequency_not_weekly():
    """Verify professional travel uses annual frequency (days * 2), not weekly (* 45)."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)  # ~100km
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'plane',
        'reco_mode': 'train',
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    
    # If it were using weekly multiplier (* 45), savings would be ~22,000+ kg
    # With annual frequency, should be ~470 kg
    assert len(result) == 1
    assert result[0].reduced < 1000  # Sanity check: less than 1 ton
    assert result[0].reduced > 400   # But still significant


def test_integration_with_stats_service():
    """Test that pro_mode_emission_reductions is included in Stats."""
    workplace_lat, workplace_lon = 46.5, 6.5
    dest_hex = h3.latlng_to_cell(46.5, 7.5, 7)
    
    journeys = [{
        'record_id': 0,
        'current_mode': 'plane',
        'reco_mode': 'train',
        'days': 10,
        'hex_id': dest_hex,
        'workplace_lat': workplace_lat,
        'workplace_lon': workplace_lon,
        'journey_idx': 0
    }]
    
    df = create_pro_journey_dataframe(journeys)
    # Add required columns for StatsService preprocessing and other services
    df['typo.reco.reco_dt2.0'] = 'train'  # Required for completed records filter
    df['data.workplace.lat'] = workplace_lat  # Required for locations service
    df['data.workplace.lon'] = workplace_lon  # Required for locations service
    
    stats_service = StatsService()
    stats = stats_service.compute_stats(df)
    
    # Check that pro_mode_emission_reductions exists and is populated
    assert stats.pro_mode_emission_reductions is not None
    assert len(stats.pro_mode_emission_reductions) == 1
    assert stats.pro_mode_emission_reductions[0].mode == 'train'
    assert stats.pro_mode_emission_reductions[0].reduced > 0

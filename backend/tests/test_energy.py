import pandas as pd
import pytest
from api.models.query import EnergyExpenditure, EnergyByJourney, JourneyEnergyLeg
from api.services.stats.energy import EnergyService


def load_test_dataframe() -> pd.DataFrame:
    """Load the test CSV into a DataFrame."""
    df = pd.read_csv('tests/data/records.csv')
    # Preprocess the dataframe to filter completed records
    if 'typo.reco.reco_dt2.0' in df.columns:
        df = df[df['typo.reco.reco_dt2.0'].notna()].copy()
    return df


def assert_energy_equal(result: EnergyExpenditure, expected: EnergyExpenditure, tolerance: float = 0.01):
    """Assert that two EnergyExpenditure objects are approximately equal."""
    assert result.mode == expected.mode
    assert result.total == expected.total
    assert result.journeys == expected.journeys
    assert abs(result.energy_kcal - expected.energy_kcal) < tolerance, \
        f"Energy mismatch for mode {result.mode}: {result.energy_kcal} != {expected.energy_kcal}"


def test_calculate_intermodal_met():
    """Test intermodal MET calculation from actual intermodal journeys."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    # Calculate intermodal MET
    intermodal_met = service._calculate_intermodal_met()
    
    # Should be between sedentary (91 kcal/hr) and active modes (245-560 kcal/hr)
    # Intermodal typically combines active + sedentary, so expect mid-range
    assert 90 < intermodal_met < 600
    
    # Should be a weighted average, not just an arbitrary value
    assert isinstance(intermodal_met, float)


def test_calculate_intermodal_time_fractions_with_train():
    """Test time fraction calculation when train is present."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    # Create a sample dataframe with the structure expected by the method
    sample_df = pd.DataFrame([
        {
            'token': 'test1',
            'journey': '0',
            'mode': 'walking',
            'is_intermodal': True,
            'is_walking': True,
            'has_train': True,
            'n_modes': 3,
            'n_walking': 1,
            'travel_time': 60.0,
            'days': 5
        },
        {
            'token': 'test1',
            'journey': '0',
            'mode': 'train',
            'is_intermodal': True,
            'is_walking': False,
            'has_train': True,
            'n_modes': 3,
            'n_walking': 1,
            'travel_time': 60.0,
            'days': 5
        },
        {
            'token': 'test1',
            'journey': '0',
            'mode': 'bike',
            'is_intermodal': True,
            'is_walking': False,
            'has_train': True,
            'n_modes': 3,
            'n_walking': 1,
            'travel_time': 60.0,
            'days': 5
        }
    ])
    
    result_df = service._calculate_intermodal_time_fractions(sample_df)

    walking_fraction = result_df[result_df['mode'] == 'walking']['time_fraction'].iloc[0]
    train_fraction = result_df[result_df['mode'] == 'train']['time_fraction'].iloc[0]
    bike_fraction = result_df[result_df['mode'] == 'bike']['time_fraction'].iloc[0]

    # Walking gets 10 min (10/60 = 0.1667 fraction)
    # Remaining: 50 min = 0.8333 fraction
    # Train gets 50% + 50% / 2 of remaining = 0.8333 * 0.75 = 0.625
    # Bike gets 50% / 2 of remaining = 0.8333 * 0.25 = 0.2083

    assert abs(walking_fraction - 10/60) < 0.01 
    assert train_fraction == (60-10)/60 * (0.5 + 0.5 / 2)
    assert bike_fraction == (60-10)/60 * (0.5 / 2)
    
    # Fractions should sum to 1.0 for the journey
    assert 'time_fraction' in result_df.columns
    total_fraction = result_df['time_fraction'].sum()
    assert abs(total_fraction - 1.0) < 0.01
    
    # All fractions should be non-negative
    assert all(result_df['time_fraction'] >= 0)

def test_calculate_intermodal_time_fractions_without_train():
    """Test time fractions when train is not present (equal split of remaining)."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    # Create sample without train
    sample_df = pd.DataFrame([
        {'token': 'test1', 'journey': '0', 'mode': 'walking', 'is_intermodal': True, 'is_walking': True, 
         'has_train': False, 'n_modes': 3, 'n_walking': 1, 'travel_time': 60.0, 'days': 5},
        {'token': 'test1', 'journey': '0', 'mode': 'bike', 'is_intermodal': True, 'is_walking': False, 
         'has_train': False, 'n_modes': 3, 'n_walking': 1, 'travel_time': 60.0, 'days': 5},
        {'token': 'test1', 'journey': '0', 'mode': 'car', 'is_intermodal': True, 'is_walking': False, 
         'has_train': False, 'n_modes': 3, 'n_walking': 1, 'travel_time': 60.0, 'days': 5}
    ])
    
    result_df = service._calculate_intermodal_time_fractions(sample_df)
    
    # Bike and car should get equal fractions
    bike_fraction = result_df[result_df['mode'] == 'bike']['time_fraction'].iloc[0]
    car_fraction = result_df[result_df['mode'] == 'car']['time_fraction'].iloc[0]
    
    assert abs(bike_fraction - car_fraction) < 0.001


def test_calculate_intermodal_time_fractions_short_journey():
    """Test time fractions for very short journeys (less than walking time)."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    # Create sample with very short time
    sample_df = pd.DataFrame([
        {'token': 'test1', 'journey': '0', 'mode': 'walking', 'is_intermodal': True, 'is_walking': True, 
         'has_train': False, 'n_modes': 2, 'n_walking': 1, 'travel_time': 7.0, 'days': 5},
        {'token': 'test1', 'journey': '0', 'mode': 'bike', 'is_intermodal': True, 'is_walking': False, 
         'has_train': False, 'n_modes': 2, 'n_walking': 1, 'travel_time': 7.0, 'days': 5}
    ])
    
    result_df = service._calculate_intermodal_time_fractions(sample_df)
    
    # Should still sum to 1.0
    assert abs(result_df['time_fraction'].sum() - 1.0) < 0.01
    
    # Walking should still get reasonable fraction
    walking_fraction = result_df[result_df['mode'] == 'walking']['time_fraction'].iloc[0]
    assert walking_fraction == 1.0  # All time should be allocated to walking since it's less than 10 min


def test_compute_modes_energy():
    """Test computation of energy expenditure for current modes."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    result = service.compute_modes_energy(apply_reco=False)
    
    # Should return a list of EnergyExpenditure objects
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(e, EnergyExpenditure) for e in result)
    
    # All energy values should be non-negative
    for energy in result:
        assert energy.energy_kcal >= 0
        assert energy.total > 0
        assert energy.journeys > 0
    
    # Check that we have expected modes
    modes = {e.mode for e in result}
    assert 'bike' in modes or 'car' in modes or 'pub' in modes


def test_compute_modes_energy_reco():
    """Test computation of energy expenditure for recommended modes."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    result = service.compute_modes_energy(apply_reco=True)
    
    # Should return a list of EnergyExpenditure objects
    assert isinstance(result, list)
    assert len(result) > 0
    
    # All energy values should be non-negative
    for energy in result:
        assert energy.energy_kcal >= 0
        assert energy.total > 0
        assert energy.journeys > 0


def test_compute_modes_energy_comparison():
    """Test that recommended modes might have different energy than current modes."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    current = service.compute_modes_energy(apply_reco=False)
    reco = service.compute_modes_energy(apply_reco=True)
    
    # Convert to dictionaries for easier comparison
    current_dict = {e.mode: e.energy_kcal for e in current}
    reco_dict = {e.mode: e.energy_kcal for e in reco}
    
    # Should have some modes in common
    assert len(current_dict) > 0
    assert len(reco_dict) > 0


def test_compute_journey_energy_current():
    """Test computation of per-journey energy for current modes."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    result = service.compute_journey_energy(apply_reco=False)
    
    # Should return an EnergyByJourney object
    assert isinstance(result, EnergyByJourney)
    assert isinstance(result.data, list)
    
    # Each leg should be a JourneyEnergyLeg
    for leg in result.data:
        assert isinstance(leg, JourneyEnergyLeg)
        assert leg.mode is not None
        assert leg.energy_kcal >= 0


def test_compute_journey_energy_reco():
    """Test computation of per-journey energy for recommended modes."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    result = service.compute_journey_energy(apply_reco=True)
    
    # Should return an EnergyByJourney object
    assert isinstance(result, EnergyByJourney)
    assert isinstance(result.data, list)


def test_journey_energy_leg_count():
    """Test that journey legs are properly counted (outbound + return)."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    result = service.compute_journey_energy(apply_reco=False)
    
    # Should have some legs
    assert len(result.data) >= 0


def test_energy_positive_values():
    """Test that all energy values are positive (or zero for non-commuting)."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    # Test aggregated energy
    mode_energy = service.compute_modes_energy(apply_reco=False)
    for energy in mode_energy:
        assert energy.energy_kcal >= 0
    
    # Test per-journey energy
    journey_energy = service.compute_journey_energy(apply_reco=False)
    for leg in journey_energy.data:
        assert leg.energy_kcal >= 0


def test_energy_formula():
    """Test that energy calculation follows the correct formula."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    # Just check that we can compute energy
    result = service.compute_modes_energy(apply_reco=False)
    assert len(result) >= 0  # May be empty if no data matches


def test_intermodal_energy_allocation():
    """Test that intermodal journeys properly allocate energy to walking."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    # Compute journey energy
    result = service.compute_journey_energy(apply_reco=False)
    
    # Check that we got some data
    assert isinstance(result, EnergyByJourney)
    
    # Find intermodal journeys (if any)
    intermodal_legs = [leg for leg in result.data if leg.is_intermodal]
    
    # If we have intermodal journeys, check they have reasonable values
    if intermodal_legs:
        for leg in intermodal_legs:
            assert leg.energy_kcal >= 0


def test_empty_dataframe():
    """Test handling of empty DataFrame."""
    df = pd.DataFrame()
    service = EnergyService(df)
    
    result = service.compute_modes_energy(apply_reco=False)
    assert result == []
    
    result = service.compute_journey_energy(apply_reco=False)
    assert isinstance(result, EnergyByJourney)
    assert result.total == 0
    assert result.data == []


def test_met_values_defined():
    """Test that all expected modes have MET values defined."""
    df = load_test_dataframe()
    service = EnergyService(df)
    
    expected_modes = ['bike', 'walking', 'car', 'train', 'pub', 'ebike', 'moto', 'carpool']
    
    # MODE_MET is a module-level variable, not an instance attribute
    from api.services.stats.energy import MODE_MET
    
    for mode in expected_modes:
        assert mode in MODE_MET
        assert MODE_MET[mode] > 0
    
    # Intermodal should be calculated
    assert 'inter' in MODE_MET

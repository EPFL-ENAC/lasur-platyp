"""
Tests for days_per normalization in professional journey statistics.

ProJourney.days now comes with a days_per field ('week', 'month', 'year').
Before any calculation, days must be converted to an annual equivalent:
  week  → days * 52
  month → days * 12
  year  → days * 1 (no change)
  missing/unknown → days * 1 (backward compat with old records)
"""

import pandas as pd
import pytest
import h3
from api.services.stats.commons import normalize_pro_days_to_yearly
from api.services.stats.emissions import EmissionsService
from api.services.stats.frequencies import FrequenciesService


# ---------------------------------------------------------------------------
# DataFrame builder (extends the pattern from test_pro_emission_reductions.py
# to include the days_per column)
# ---------------------------------------------------------------------------

def make_pro_journey_df(journeys: list[dict]) -> pd.DataFrame:
    """
    Build a minimal v3 DataFrame for professional journey tests.

    Each journey dict may contain:
        record_id, journey_idx, current_mode, reco_mode,
        days, days_per (optional), hex_id, workplace_lat, workplace_lon
    """
    base: dict[str, list] = {
        'data.workplace.lat': [],
        'data.workplace.lon': [],
        'data.version': [],
    }

    by_record: dict[int, list] = {}
    for j in journeys:
        rid = j.get('record_id', 0)
        by_record.setdefault(rid, []).append(j)

    for rid, record_journeys in by_record.items():
        row: dict = {
            'data.workplace.lat': record_journeys[0]['workplace_lat'],
            'data.workplace.lon': record_journeys[0]['workplace_lon'],
            'data.version': '3.0',
        }
        for j in record_journeys:
            idx = j['journey_idx']
            row[f'data.freq_mod_pro_journeys.{idx}.mode'] = j['current_mode']
            row[f'data.freq_mod_pro_journeys.{idx}.days'] = j['days']
            row[f'data.freq_mod_pro_journeys.{idx}.hex_id'] = j['hex_id']
            if 'days_per' in j:
                row[f'data.freq_mod_pro_journeys.{idx}.days_per'] = j['days_per']
            if j.get('reco_mode'):
                row[f'typo.reco_pro.reco_pros.{idx}'] = j['reco_mode']

        for key, value in row.items():
            base.setdefault(key, []).append(value)

    max_len = len(by_record)
    for key in base:
        if len(base[key]) < max_len:
            base[key].extend([None] * (max_len - len(base[key])))

    return pd.DataFrame(base)


# ---------------------------------------------------------------------------
# Unit tests: normalize_pro_days_to_yearly
# ---------------------------------------------------------------------------

class TestNormalizeProDaysToYearly:

    def test_year_unchanged(self):
        assert normalize_pro_days_to_yearly(10, 'year') == 10

    def test_month_multiplied_by_11(self):
        assert normalize_pro_days_to_yearly(3, 'month') == 33

    def test_week_multiplied_by_47(self):
        assert normalize_pro_days_to_yearly(2, 'week') == 94

    def test_none_treated_as_year(self):
        assert normalize_pro_days_to_yearly(10, None) == 10

    def test_nan_treated_as_year(self):
        import math
        result = normalize_pro_days_to_yearly(10, float('nan'))
        assert result == 10

    def test_unknown_value_treated_as_year(self):
        assert normalize_pro_days_to_yearly(10, 'quarter') == 10

    def test_fractional_days(self):
        assert normalize_pro_days_to_yearly(1.5, 'week') == pytest.approx(70.5)


# ---------------------------------------------------------------------------
# Emission reductions: days_per scaling
# ---------------------------------------------------------------------------

WORKPLACE_LAT, WORKPLACE_LON = 46.5, 6.5
DEST_HEX = h3.latlng_to_cell(46.5, 7.5, 7)  # ~100 km east


def _plane_to_train_reductions(days, days_per=None):
    journey = {
        'record_id': 0,
        'current_mode': 'plane',
        'reco_mode': 'train',
        'days': days,
        'hex_id': DEST_HEX,
        'workplace_lat': WORKPLACE_LAT,
        'workplace_lon': WORKPLACE_LON,
        'journey_idx': 0,
    }
    if days_per is not None:
        journey['days_per'] = days_per
    df = make_pro_journey_df([journey])
    service = EmissionsService(df)
    result = service.compute_modes_pro_emission_reductions()
    assert len(result) == 1 and result[0].mode == 'train'
    return result[0].reduced


class TestEmissionReductionsDaysPer:

    def test_year_equals_no_days_per(self):
        """days_per='year' must give the same result as omitting days_per."""
        assert _plane_to_train_reductions(10, 'year') == pytest.approx(
            _plane_to_train_reductions(10), rel=1e-6
        )

    def test_week_gives_47x_year(self):
        """days=1, days_per='week' should equal days=47, days_per='year'."""
        assert _plane_to_train_reductions(1, 'week') == pytest.approx(
            _plane_to_train_reductions(47, 'year'), rel=1e-4
        )

    def test_month_gives_11x_year(self):
        """days=1, days_per='month' should equal days=11, days_per='year'."""
        assert _plane_to_train_reductions(1, 'month') == pytest.approx(
            _plane_to_train_reductions(11, 'year'), rel=1e-4
        )

    def test_week_greater_than_month_greater_than_year(self):
        """For the same raw days value, week > month > year."""
        r_week = _plane_to_train_reductions(5, 'week')
        r_month = _plane_to_train_reductions(5, 'month')
        r_year = _plane_to_train_reductions(5, 'year')
        assert r_week > r_month > r_year

    def test_missing_days_per_backward_compat(self):
        """Old records without days_per behave identically to days_per='year'."""
        assert _plane_to_train_reductions(10) == pytest.approx(
            _plane_to_train_reductions(10, 'year'), rel=1e-6
        )


# ---------------------------------------------------------------------------
# Pro emissions: days_per scaling
# ---------------------------------------------------------------------------

def _plane_emissions(days, days_per=None):
    journey = {
        'record_id': 0,
        'current_mode': 'plane',
        'days': days,
        'hex_id': DEST_HEX,
        'workplace_lat': WORKPLACE_LAT,
        'workplace_lon': WORKPLACE_LON,
        'journey_idx': 0,
    }
    if days_per is not None:
        journey['days_per'] = days_per
    df = make_pro_journey_df([journey])
    service = EmissionsService(df)
    results = service.compute_modes_pro_emissions()
    plane = next((r for r in results if r.mode == 'plane'), None)
    assert plane is not None, "Expected plane emissions in result"
    return plane.emissions


class TestProEmissionsDaysPer:

    def test_year_equals_no_days_per(self):
        assert _plane_emissions(10, 'year') == pytest.approx(
            _plane_emissions(10), rel=1e-6
        )

    def test_week_gives_47x_year(self):
        assert _plane_emissions(1, 'week') == pytest.approx(
            _plane_emissions(47, 'year'), rel=1e-4
        )

    def test_month_gives_11x_year(self):
        assert _plane_emissions(1, 'month') == pytest.approx(
            _plane_emissions(11, 'year'), rel=1e-4
        )

    def test_missing_days_per_backward_compat(self):
        assert _plane_emissions(10) == pytest.approx(
            _plane_emissions(10, 'year'), rel=1e-6
        )


# ---------------------------------------------------------------------------
# Pro frequencies: days_per changes the bucketed value
# ---------------------------------------------------------------------------

def _car_frequency_values(days, days_per=None) -> dict[str, int]:
    """
    Return {value_str: sum} from the frequency data for 'car' mode journeys.
    The value in Frequencies is the *normalized* annual days count.
    """
    journey = {
        'record_id': 0,
        'current_mode': 'car',
        'days': days,
        'hex_id': DEST_HEX,
        'workplace_lat': WORKPLACE_LAT,
        'workplace_lon': WORKPLACE_LON,
        'journey_idx': 0,
    }
    if days_per is not None:
        journey['days_per'] = days_per
    df = make_pro_journey_df([journey])
    service = FrequenciesService(df)
    results = service.compute_modes_pro_frequencies()
    # Results are keyed like "local_car", "national_car", etc.
    combined: dict[str, int] = {}
    for freq in results:
        if 'car' in freq.field:
            for entry in freq.data:
                combined[entry.value] = combined.get(
                    entry.value, 0) + (entry.sum or 0)
    return combined


class TestProFrequenciesDaysPer:

    def test_year_value_unchanged(self):
        values = _car_frequency_values(5, 'year')
        assert '5' in values

    def test_week_value_multiplied_by_47(self):
        values = _car_frequency_values(1, 'week')
        assert '47' in values

    def test_month_value_multiplied_by_11(self):
        values = _car_frequency_values(1, 'month')
        assert '11' in values

    def test_missing_days_per_behaves_as_year(self):
        without = _car_frequency_values(5)
        with_year = _car_frequency_values(5, 'year')
        assert without == with_year

    def test_week_bucket_differs_from_year_bucket(self):
        week_values = _car_frequency_values(1, 'week')
        year_values = _car_frequency_values(1, 'year')
        assert week_values != year_values

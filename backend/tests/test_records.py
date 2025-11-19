import pandas as pd
import pytest
import os
from unittest import mock
with mock.patch.dict(os.environ, {
    "DB_PREFIX": "test",
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "test",
    "KEYCLOAK_API_ID": "dummy",
    "KEYCLOAK_API_SECRET": "dummy"
}):
    from api.services.records import RecordService
from api.models.query import Emissions, Frequencies, Frequency


def assert_frequencies_equal(result: Frequencies, expected: Frequencies):
    assert result.field == expected.field
    assert result.total == expected.total
    assert len(result.data) == len(expected.data)
    for exp_freq in expected.data:
        matched = next(
            (f for f in result.data if f.value == exp_freq.value), None)
        assert matched is not None, f"Expected frequency value {exp_freq.value} not found"
        assert matched.count == exp_freq.count


def assert_emissions_equal(result: Emissions, expected: Emissions):
    assert result.field == expected.field
    assert result.total == expected.total
    assert result.distances == expected.distances
    assert result.journeys == expected.journeys
    assert result.emissions == expected.emissions


def test_compute_equipments_frequencies():
    # Load the test CSV into a DataFrame
    df = pd.read_csv('tests/data/records.csv')
    service = RecordService(session=None)  # session not needed for this test
    df = service.preprocess_dataframe(df)
    result = service.compute_equipments_frequencies(df)

    # Basic checks
    assert isinstance(result, Frequencies)
    assert result.field == 'equipments'
    assert result.total == len(df)
    assert isinstance(result.data, list)
    for freq in result.data:
        assert isinstance(freq, Frequency)
        assert hasattr(freq, 'value')
        assert hasattr(freq, 'count')

    # print(result)
    expected = Frequencies(
        field='equipments',
        total=30,
        data=[
            Frequency(value='car_driver', count=8, sum=None),
            Frequency(value='mob_subs', count=8, sum=None),
            Frequency(value='train_subs', count=7, sum=None),
            Frequency(value='moto', count=6, sum=None),
            Frequency(value='upt_subs', count=2, sum=None),
            Frequency(value='ebike', count=2, sum=None),
            Frequency(value='car', count=2, sum=None),
            Frequency(value='bike', count=2, sum=None),
            Frequency(value='car_passenger', count=1, sum=None)
        ]
    )

    assert_frequencies_equal(result, expected)


def test_compute_constraints_frequencies():
    # Load the test CSV into a DataFrame
    df = pd.read_csv('tests/data/records.csv')
    service = RecordService(session=None)  # session not needed for this test
    df = service.preprocess_dataframe(df)
    result = service.compute_constraints_frequencies(df)

    # print(result)
    expected = Frequencies(
        field='constraints',
        total=30,
        data=[
            Frequency(value='night', count=9, sum=None),
            Frequency(value='disabled', count=6, sum=None),
            Frequency(value='heavy', count=5, sum=None),
            Frequency(value='dependent', count=1, sum=None),
            Frequency(value='none', count=1, sum=None)
        ]
    )

    assert_frequencies_equal(result, expected)


def test_compute_travel_time_frequencies():
    # Load the test CSV into a DataFrame
    df = pd.read_csv('tests/data/records.csv')
    service = RecordService(session=None)  # session not needed for this test
    df = service.preprocess_dataframe(df)
    result = service.compute_travel_time_frequencies(df)

    # print(result)
    expected = Frequencies(
        field='travel_time',
        total=30,
        data=[
            Frequency(value='5', count=10, sum=None),
            Frequency(value='0', count=8, sum=None),
            Frequency(value='35', count=5, sum=None),
            Frequency(value='40', count=2, sum=None),
            Frequency(value='20', count=2, sum=None),
            Frequency(value='50', count=1, sum=None),
            Frequency(value='10', count=1, sum=None),
            Frequency(value='25', count=1, sum=None)
        ]
    )

    assert_frequencies_equal(result, expected)


def test_compute_recommendation_frequencies():
    # Load the test CSV into a DataFrame
    df = pd.read_csv('tests/data/records.csv')
    service = RecordService(session=None)  # session not needed for this test
    df = service.preprocess_dataframe(df)
    result = service.compute_recommendation_frequencies(df)

    # print(result)
    expected = Frequencies(
        field='reco_dt2',
        total=30,
        data=[
            Frequency(value='covoit', count=11, sum=None),
            Frequency(value='inter', count=5, sum=None),
            Frequency(value='train', count=3, sum=None),
            Frequency(value='vae', count=3, sum=None),
            Frequency(value='tpu', count=4, sum=None),
            Frequency(value='elec', count=2, sum=None),
            Frequency(value='velo', count=1, sum=None),
            Frequency(value='marche', count=1, sum=None)
        ]
    )

    assert_frequencies_equal(result, expected)


def test_compute_modes_frequencies():
    # Load the test CSV into a DataFrame
    df = pd.read_csv('tests/data/records.csv')
    service = RecordService(session=None)  # session not needed for this test
    df = service.preprocess_dataframe(df)
    result = service.compute_modes_frequencies(df)

    # print(result)
    expected = [
        Frequencies(field='walking', total=30, data=[Frequency(value='1', count=3, sum=3), Frequency(
            value='3', count=2, sum=6), Frequency(value='4', count=1, sum=4), Frequency(value='5', count=1, sum=5)]),
        Frequencies(field='bike', total=30, data=[Frequency(value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2), Frequency(
            value='3', count=5, sum=15), Frequency(value='4', count=1, sum=4), Frequency(value='5', count=1, sum=5)]),
        Frequencies(field='ebike', total=30, data=[]),
        Frequencies(field='pub', total=30, data=[Frequency(value='1', count=1, sum=1), Frequency(
            value='3', count=7, sum=21), Frequency(value='4', count=1, sum=4), Frequency(value='5', count=3, sum=15)]),
        Frequencies(field='moto', total=30, data=[Frequency(value='1', count=1, sum=1), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=1, sum=4), Frequency(value='5', count=2, sum=10)]),
        Frequencies(field='carpool', total=30, data=[
                    Frequency(value='3', count=1, sum=3)]),
        Frequencies(field='car', total=30, data=[Frequency(value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=3, sum=12), Frequency(value='5', count=3, sum=15)]),
        Frequencies(field='train', total=30, data=[Frequency(value='1', count=1, sum=1), Frequency(
            value='3', count=2, sum=6), Frequency(value='5', count=1, sum=5)])
    ]
    assert len(result) == len(expected)
    for res_freqs, exp_freqs in zip(result, expected):
        assert_frequencies_equal(res_freqs, exp_freqs)


def test_compute_modes_emissions():
    # Load the test CSV into a DataFrame
    df = pd.read_csv('tests/data/records.csv')
    service = RecordService(session=None)  # session not needed for this test
    df = service.preprocess_dataframe(df)
    result = service.compute_modes_emissions(df)

    # print(result)
    expected = [
        Emissions(field='walking', total=30, distances=587.756,
                  journeys=1170, emissions=0.0),
        Emissions(field='bike', total=30, distances=6728.72,
                  journeys=2430, emissions=151.304),
        Emissions(field='ebike', total=30, distances=0.0,
                  journeys=0, emissions=0.0),
        Emissions(field='pub', total=30, distances=20859.321,
                  journeys=3690, emissions=2243.077),
        Emissions(field='moto', total=30, distances=6837.789,
                  journeys=1620, emissions=2469.62),
        Emissions(field='carpool', total=30, distances=4605.723,
                  journeys=270, emissions=214.166),
        Emissions(field='car', total=30, distances=15839.606,
                  journeys=2970, emissions=15023.343),
        Emissions(field='train', total=30, distances=2122.997,
                  journeys=1080, emissions=82.563)
    ]
    assert len(result) == len(expected)
    for res_emission, exp_emission in zip(result, expected):
        assert_emissions_equal(res_emission, exp_emission)

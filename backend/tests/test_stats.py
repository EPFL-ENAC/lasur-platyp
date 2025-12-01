import pandas as pd
from api.services.stats.links import LinksService
from api.services.stats.stats import StatsService
from api.models.query import Emissions, Frequencies, Frequency, Link, Links
from api.services.stats.frequencies import FrequenciesService
from api.services.stats.emissions import EmissionsService


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


def assert_links_equal(result: Links, expected: Links):
    assert result.total == expected.total
    assert len(result.data) == len(expected.data)
    for exp_link in expected.data:
        matched = next(
            (l for l in result.data if l.source == exp_link.source and l.target == exp_link.target), None)
        assert matched is not None, f"Expected link {exp_link.source} -> {exp_link.target} not found"
        assert matched.value == exp_link.value


def load_test_dataframe() -> pd.DataFrame:
    """Load the test CSV into a DataFrame."""
    df = pd.read_csv('tests/data/records.csv')
    stats = StatsService()
    df = stats._preprocess_dataframe(df)
    return df


def test_compute_equipments_frequencies():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_equipments_frequencies()

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
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_constraints_frequencies()

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
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_travel_time_frequencies()

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
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_recommendation_frequencies()

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


def test_compute_recommendation_pro_frequencies():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_recommendation_pro_frequencies()

    # print(result)
    expected = Frequencies(
        field='reco_pros',
        total=30,
        data=[
            Frequency(value='elec', count=4, sum=None),
            Frequency(value='train', count=4, sum=None),
            Frequency(value='avoid', count=2, sum=None),
            Frequency(value='bike', count=1, sum=None),
            Frequency(value='elec_moto', count=1, sum=None)
        ]
    )
    assert_frequencies_equal(result, expected)


def test_compute_modes_frequencies():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_modes_frequencies()

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


def test_compute_modes_pro_frequencies():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_modes_pro_frequencies()

    # print(result)
    expected = [
        Frequencies(field='local_walking', total=30, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='local_car', total=30, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='local_pub', total=30, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='local_bike', total=30, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='local_moto', total=30, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='local_train', total=30, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='national_car', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(value='3', count=1, sum=3), Frequency(
            value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6), Frequency(value='48', count=1, sum=48)]),
        Frequencies(field='national_pub', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6)]),
        Frequencies(field='national_train', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6)]),
        Frequencies(field='national_moto', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(value='3', count=1, sum=3), Frequency(
            value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6), Frequency(value='240', count=1, sum=240)]),
        Frequencies(field='national_plane', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6)]),
        Frequencies(field='europe_car', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='europe_train', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='europe_plane', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='inter_car', total=30, data=[Frequency(
            value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2)]),
        Frequencies(field='inter_train', total=30, data=[Frequency(value='1', count=1, sum=1), Frequency(
            value='2', count=1, sum=2), Frequency(value='36', count=1, sum=36)]),
        Frequencies(field='inter_plane', total=30, data=[Frequency(value='1', count=1, sum=1), Frequency(
            value='2', count=1, sum=2), Frequency(value='36', count=1, sum=36)]),
        Frequencies(field='europe_walking', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='national_walking', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6)]),
        Frequencies(field='inter_walking', total=30, data=[Frequency(
            value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2)]),
        Frequencies(field='europe_bike', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='national_bike', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6)]),
        Frequencies(field='inter_bike', total=30, data=[Frequency(
            value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2)]),
        Frequencies(field='europe_pub', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='inter_pub', total=30, data=[Frequency(
            value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2)]),
        Frequencies(field='europe_moto', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='inter_moto', total=30, data=[Frequency(
            value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2)]),
        Frequencies(field='europe_boat', total=30, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='national_boat', total=30, data=[Frequency(value='1', count=4, sum=4), Frequency(
            value='3', count=1, sum=3), Frequency(value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6)]),
        Frequencies(field='inter_boat', total=30, data=[Frequency(
            value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2)]),
        Frequencies(field='local_boat', total=30, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='local_plane', total=30, data=[Frequency(value='1', count=1, sum=1)])]

    assert len(result) == len(expected)
    for res_freqs, exp_freqs in zip(result, expected):
        assert_frequencies_equal(res_freqs, exp_freqs)


def test_compute_modes_emissions():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = EmissionsService(df)
    result = service.compute_modes_emissions()

    # print(result)
    expected = [
        Emissions(field='bike', total=30, distances=6728.72,
                  journeys=2430, emissions=151.304),
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


def test_compute_modes_pro_emissions():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = EmissionsService(df)
    result = service.compute_modes_pro_emissions()

    # print(result)
    expected = [
        Emissions(field='bike', total=7, distances=153.654,
                  journeys=2, emissions=0.922),
        Emissions(field='moto', total=7, distances=546.692,
                  journeys=4, emissions=84.737),
        Emissions(field='car', total=7, distances=1259.281,
                  journeys=6, emissions=234.226),
        Emissions(field='train', total=7, distances=5651.081,
                  journeys=22, emissions=45.209),
        Emissions(field='plane', total=7, distances=41811.232,
                  journeys=10, emissions=10996.354)
    ]
    assert len(result) == len(expected)
    for res_emission, exp_emission in zip(result, expected):
        assert_emissions_equal(res_emission, exp_emission)


def test_compute_mode_reco_links():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = LinksService(df)
    result = service.compute_mode_reco_links()

    # print(result)
    expected = Links(
        total=30,
        data=[
            Link(source='walking', target='elec', value=1),
            Link(source='walking', target='train', value=1),
            Link(source='walking', target='tpu', value=5),
            Link(source='bike', target='covoit', value=3),
            Link(source='bike', target='velo', value=1),
            Link(source='bike', target='tpu', value=2),
            Link(source='bike', target='elec', value=1),
            Link(source='pub', target='covoit', value=5),
            Link(source='pub', target='train', value=2),
            Link(source='pub', target='inter', value=1),
            Link(source='pub', target='tpu', value=3),
            Link(source='pub', target='elec', value=1),
            Link(source='moto', target='elec', value=1),
            Link(source='moto', target='covoit', value=1),
            Link(source='car', target='elec', value=1),
            Link(source='car', target='covoit', value=2),
            Link(source='car', target='inter', value=3),
            Link(source='train', target='train', value=1),
            Link(source='train', target='covoit', value=1),
            Link(source='train', target='tpu', value=1),
            Link(source='car', target='vae', value=2),
            Link(source='car', target='train', value=1),
            Link(source='carpool', target='inter', value=1),
            Link(source='bike', target='inter', value=3),
            Link(source='moto', target='marche', value=1),
            Link(source='moto', target='vae', value=1),
            Link(source='moto', target='tpu', value=1),
            Link(source='walking', target='inter', value=2),
            Link(source='train', target='inter', value=1)
        ]
    )
    assert_links_equal(result, expected)


def test_compute_mode_reco_pro_links():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = LinksService(df)
    result = service.compute_mode_reco_pro_links()

    expected = Links(
        total=30,
        data=[
            Link(source='plane', target='train', value=1),
            Link(source='plane', target='avoid', value=2),
            Link(source='train', target='train', value=2),
            Link(source='bike', target='bike', value=1),
            Link(source='moto', target='elec_moto', value=1),
            Link(source='moto', target='train', value=1)
        ]
    )
    assert_links_equal(result, expected)

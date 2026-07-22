import pandas as pd
from api.services.stats.links import LinksService
from api.services.stats.locations import LocationsService
from api.services.stats.stats import StatsService
from api.models.query import Emissions, Frequencies, Frequency, Link, Links
from api.services.stats.frequencies import FrequenciesService
from api.services.stats.emissions import EmissionsService
import h3


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
    assert result.mode == expected.mode
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
    # Load the test CSV into a DataFrame. It only has legacy typo.reco.reco_dt2.0/.1
    # data (no typo.reco.reco_inter.N), so every recommendation at both legacy
    # indices is taken into account.
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_recommendation_frequencies()

    # print(result)
    expected = Frequencies(
        field='reco_inter',
        total=30,
        data=[
            Frequency(value='covoit', count=18, sum=None),
            Frequency(value='elec', count=13, sum=None),
            Frequency(value='inter', count=7, sum=None),
            Frequency(value='train', count=6, sum=None),
            Frequency(value='vae', count=6, sum=None),
            Frequency(value='tpu', count=6, sum=None),
            Frequency(value='velo', count=2, sum=None),
            Frequency(value='marche', count=2, sum=None)
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
            Frequency(value='train', count=4, sum=None),
            Frequency(value='avoid', count=2, sum=None),
            Frequency(value='bike', count=1, sum=None),
            Frequency(value='elec_moto', count=1, sum=None)
        ]
    )
    assert_frequencies_equal(result, expected)


def test_compute_modes_pro_frequencies():
    # Load the test CSV into a DataFrame. Only v3 records (7 of the 30
    # completed records) contribute, since pro mode frequencies are no
    # longer computed for v1/v2 records.
    df = load_test_dataframe()
    service = FrequenciesService(df)
    result = service.compute_modes_pro_frequencies()

    expected = [
        Frequencies(field='national_bike', total=7, data=[
                    Frequency(value='1', count=1, sum=1)]),
        Frequencies(field='national_moto', total=7, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='national_car', total=7, data=[
                    Frequency(value='3', count=1, sum=3)]),
        Frequencies(field='national_train', total=7, data=[
                    Frequency(value='1', count=1, sum=1), Frequency(value='4', count=1, sum=4), Frequency(value='6', count=1, sum=6)]),
        Frequencies(field='europe_plane', total=7, data=[
                    Frequency(value='1', count=2, sum=2)]),
        Frequencies(field='inter_plane', total=7, data=[
                    Frequency(value='1', count=1, sum=1), Frequency(value='2', count=1, sum=2)]),
    ]
    assert len(result) == len(expected)
    for res_freqs, exp_freqs in zip(result, expected):
        assert_frequencies_equal(res_freqs, exp_freqs)


def test_compute_modes_pro_emissions():
    # Load the test CSV into a DataFrame
    df = load_test_dataframe()
    service = EmissionsService(df)
    result = service.compute_modes_pro_emissions()

    # print(result)
    expected = [
        Emissions(mode='bike', total=7, distances=153.654,
                  journeys=2, emissions=0.922),
        Emissions(mode='moto', total=7, distances=546.692,
                  journeys=4, emissions=84.737),
        Emissions(mode='car', total=7, distances=1259.281,
                  journeys=6, emissions=234.226),
        Emissions(mode='train', total=7, distances=5651.081,
                  journeys=22, emissions=45.209),
        Emissions(mode='plane', total=7, distances=41811.232,
                  journeys=10, emissions=10996.354)
    ]
    assert len(result) == len(expected)
    for res_emission, exp_emission in zip(result, expected):
        assert_emissions_equal(res_emission, exp_emission)


def test_compute_mode_reco_links():
    # Load the test CSV into a DataFrame. Only v3 records (7 of the 30
    # completed records) contribute, since mode recommendation links are no
    # longer computed for v1/v2 records.
    df = load_test_dataframe()
    service = LinksService(df)
    result = service.compute_mode_reco_links()

    # print(result)
    expected = Links(
        total=7,
        data=[
            Link(source='car', target='vae', value=11),
            Link(source='car', target='tpu', value=6),
            Link(source='car', target='train', value=4),
            Link(source='car', target='covoit', value=4),
            Link(source='car', target='inter', value=5),
            Link(source='carpool', target='inter', value=5),
            Link(source='carpool', target='vae', value=5),
            Link(source='bike', target='inter', value=15),
            Link(source='bike', target='vae', value=15),
            Link(source='moto', target='marche', value=3),
            Link(source='moto', target='vae', value=8),
            Link(source='moto', target='velo', value=5),
            Link(source='moto', target='tpu', value=5),
            Link(source='moto', target='inter', value=5),
            Link(source='pub', target='tpu', value=10),
            Link(source='pub', target='inter', value=10),
            Link(source='walking', target='tpu', value=15),
            Link(source='walking', target='inter', value=25),
            Link(source='walking', target='vae', value=10),
            Link(source='train', target='inter', value=5),
            Link(source='train', target='vae', value=5),
        ]
    )
    assert_links_equal(result, expected)


def test_compute_mode_reco_pro_links():
    # Load the test CSV into a DataFrame. Only v3 records (7 of the 30
    # completed records) contribute.
    df = load_test_dataframe()
    service = LinksService(df)
    result = service.compute_mode_reco_pro_links()

    expected = Links(
        total=7,
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


def test_compute_home_location_heatmap():
    df = pd.DataFrame(
        {
            "data.origin.lat": [
                48.8566,
                48.8567,
                48.8566,
                45.7640,
            ],
            "data.origin.lon": [
                2.3522,
                2.3523,
                2.3522,
                4.8357,
            ],
        }
    )

    service = LocationsService(df)
    result = service.compute_home_location_heatmap(resolution=8)

    paris_hex_1 = h3.latlng_to_cell(48.8566, 2.3522, 8)
    paris_hex_2 = h3.latlng_to_cell(48.8567, 2.3523, 8)
    lyon_hex = h3.latlng_to_cell(45.7640, 4.8357, 8)

    expected = {}
    expected[paris_hex_1] = expected.get(paris_hex_1, 0) + 1
    expected[paris_hex_2] = expected.get(paris_hex_2, 0) + 1
    expected[paris_hex_1] = expected.get(paris_hex_1, 0) + 1
    expected[lyon_hex] = expected.get(lyon_hex, 0) + 1

    assert result == expected

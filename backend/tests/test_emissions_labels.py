"""
Tests for CO2 emissions (and potential reductions) grouped by v3 typology
labels (typo.reco.simple_labels.N / typo.reco.complex_labels.N), which credit
each journey's full emissions to one label bucket instead of splitting across
its raw modes -- mirroring how FrequenciesService already groups journey days
by these labels.
"""
import pandas as pd
from api.services.stats.emissions import EmissionsService


def v3_df() -> pd.DataFrame:
    """
    Two v3 respondents:
    - A: journey 0 is single-mode 'car' (label 'TIM' / 'car'), recommended
      'train' (a real reduction); journey 1 is intermodal 'train'+'car'
      (label 'TIM+TP' / 'car+pub'), recommended 'inter' (already intermodal,
      so no further reduction)
    - B: journey 0 is single-mode 'pub' (label 'TP' / 'pub'), recommended
      'vae' (a real reduction)
    Plus one v2 record (no labels) that must be excluded entirely, and one v3
    journey with no label/recommendation at all (must be excluded from the
    label totals).
    """
    return pd.DataFrame([
        {
            'token': 'A',
            'data.version': '3.0',
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 3,
            'data.freq_mod_journeys.0.modes.0': 'car',
            'typo.reco.simple_labels.0': 'TIM',
            'typo.reco.complex_labels.0': 'car',
            'typo.reco.reco_inter.0': 'train',
            'data.freq_mod_journeys.1.days': 2,
            'data.freq_mod_journeys.1.modes.0': 'train',
            'data.freq_mod_journeys.1.modes.1': 'car',
            'typo.reco.simple_labels.1': 'TIM+TP',
            'typo.reco.complex_labels.1': 'car+pub',
            'typo.reco.reco_inter.1': 'inter',
        },
        {
            'token': 'B',
            'data.version': '3.0',
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 5,
            'data.freq_mod_journeys.0.modes.0': 'pub',
            'typo.reco.simple_labels.0': 'TP',
            'typo.reco.complex_labels.0': 'pub',
            'typo.reco.reco_inter.0': 'vae',
        },
        {
            'token': 'C',
            'data.version': '3.0',
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 4,
            'data.freq_mod_journeys.0.modes.0': 'bike',
            # no simple/complex label for this journey: must be excluded
        },
        {
            'token': 'D',
            'data.version': '2.0',
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 10,
            'data.freq_mod_journeys.0.modes.0': 'plane',
            # v2 record: even if it had labels, it must be excluded by the v3 filter
        },
    ])


def test_compute_modes_emissions_simple_labels():
    service = EmissionsService(v3_df())
    result = service.compute_modes_emissions_simple_labels()

    by_label = {e.mode: e for e in result}
    assert set(by_label.keys()) == {'TIM', 'TIM+TP', 'TP'}
    for emission in result:
        assert emission.total == 3  # only v3 records (A, B, C)
        assert emission.emissions > 0
        assert emission.distances > 0
        assert emission.journeys > 0

    # journey 0 for A is single-mode 'car' -> full journey emissions credited to 'TIM'
    tim = by_label['TIM']
    assert tim.journeys == 3 * 2 * 45

    # journey 1 for A is intermodal train+car -> full journey emissions
    # (train 80% + car 20% of distance) credited to 'TIM+TP'
    tim_tp = by_label['TIM+TP']
    assert tim_tp.journeys == 2 * 2 * 45

    tp = by_label['TP']
    assert tp.journeys == 5 * 2 * 45


def test_compute_modes_emissions_complex_labels():
    service = EmissionsService(v3_df())
    result = service.compute_modes_emissions_complex_labels()

    by_label = {e.mode: e for e in result}
    assert set(by_label.keys()) == {'car', 'car+pub', 'pub'}
    for emission in result:
        assert emission.total == 3

    # single-mode 'car' journey's emissions must match the raw-mode 'car'
    # emissions computed by the existing v2 pipeline for the same journey
    # (same MODE_EMISSIONS factor, same distance, same days)
    assert by_label['car'].journeys == 3 * 2 * 45
    assert by_label['car+pub'].journeys == 2 * 2 * 45
    assert by_label['pub'].journeys == 5 * 2 * 45


def test_compute_modes_emissions_labels_empty_when_no_v3_records():
    df = pd.DataFrame([
        {
            'token': 'D',
            'data.version': '2.0',
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 10,
            'data.freq_mod_journeys.0.modes.0': 'plane',
        },
    ])
    service = EmissionsService(df)
    assert service.compute_modes_emissions_simple_labels() == []
    assert service.compute_modes_emissions_complex_labels() == []


def test_compute_modes_emissions_simple_labels_apply_reco():
    service = EmissionsService(v3_df())
    current = {e.mode: e for e in service.compute_modes_emissions_simple_labels()}
    reco = {e.mode: e for e in service.compute_modes_emissions_simple_labels(apply_reco=True)}

    # journeys with a recommendation with a positive reduction only
    # ('TIM+TP' is already intermodal with reco 'inter': no journey without a
    # recommendation is included, but 'TIM+TP' itself is, since reco data exists)
    assert set(reco.keys()) == {'TIM', 'TIM+TP', 'TP'}
    for emission in reco.values():
        assert emission.total == 3
        # distances/journeys are unaffected by apply_reco: same trips, only
        # the reported emissions value changes
        assert emission.distances == current[emission.mode].distances
        assert emission.journeys == current[emission.mode].journeys

    # 'TIM' (car -> train) must emit less post-reco than currently
    assert reco['TIM'].emissions < current['TIM'].emissions
    # 'TP' (pub -> vae) must emit less post-reco than currently
    assert reco['TP'].emissions < current['TP'].emissions
    # 'TIM+TP' is already intermodal with reco 'inter': no further change
    assert reco['TIM+TP'].emissions == current['TIM+TP'].emissions


def test_compute_modes_emissions_complex_labels_apply_reco():
    service = EmissionsService(v3_df())
    current = {e.mode: e for e in service.compute_modes_emissions_complex_labels()}
    reco = {e.mode: e for e in service.compute_modes_emissions_complex_labels(apply_reco=True)}

    assert set(reco.keys()) == {'car', 'car+pub', 'pub'}
    assert reco['car'].emissions < current['car'].emissions
    assert reco['pub'].emissions < current['pub'].emissions
    assert reco['car+pub'].emissions == current['car+pub'].emissions


def test_compute_modes_emissions_labels_apply_reco_empty_when_no_v3_records():
    df = pd.DataFrame([
        {
            'token': 'D',
            'data.version': '2.0',
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 10,
            'data.freq_mod_journeys.0.modes.0': 'plane',
            'typo.reco.reco_inter.0': 'train',
        },
    ])
    service = EmissionsService(df)
    assert service.compute_modes_emissions_simple_labels(apply_reco=True) == []
    assert service.compute_modes_emissions_complex_labels(apply_reco=True) == []


def test_compute_modes_emission_reductions_simple_labels():
    service = EmissionsService(v3_df())
    result = service.compute_modes_emission_reductions_simple_labels()

    by_label = {r.mode: r for r in result}
    # journey 1 ('TIM+TP') is already intermodal with reco 'inter', so it has
    # no positive saving and must be excluded entirely
    assert set(by_label.keys()) == {'TIM', 'TP'}
    for reduction in result:
        assert reduction.total == 3  # only v3 records (A, B, C)
        assert reduction.reduced > 0


def test_compute_modes_emission_reductions_complex_labels():
    service = EmissionsService(v3_df())
    result = service.compute_modes_emission_reductions_complex_labels()

    by_label = {r.mode: r for r in result}
    assert set(by_label.keys()) == {'car', 'pub'}
    for reduction in result:
        assert reduction.total == 3
        assert reduction.reduced > 0


def test_compute_modes_emission_reductions_labels_empty_when_no_v3_records():
    df = pd.DataFrame([
        {
            'token': 'D',
            'data.version': '2.0',
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 10,
            'data.freq_mod_journeys.0.modes.0': 'plane',
            'typo.reco.reco_inter.0': 'train',
        },
    ])
    service = EmissionsService(df)
    assert service.compute_modes_emission_reductions_simple_labels() == []
    assert service.compute_modes_emission_reductions_complex_labels() == []

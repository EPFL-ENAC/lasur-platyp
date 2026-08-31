"""
Tests for typo.reco.reco_inter (one recommendation per journey), which replaced
typo.reco.reco_dt2 (up to two general recommendations). Legacy typo.reco.reco_dt2
data must keep working (records collected before this change), while new
typo.reco.reco_inter.N must be matched 1:1 by index with the journey of the same
index in data.freq_mod_journeys and weighted accordingly.
"""
import pandas as pd
from api.services.stats.commons import BaseStatsService
from api.services.stats.frequencies import FrequenciesService
from api.services.stats.links import LinksService
from api.services.stats.equipments import EquipmentsService
from api.services.stats.energy import EnergyService
from api.services.stats.stats import StatsService
from api.services.stats.behavior_change import BehaviorChangeService


def new_style_df() -> pd.DataFrame:
    """Two people, each with two journeys and one recommendation per journey."""
    return pd.DataFrame([
        {
            'token': 'A',
            'data.version': '3.0',
            'data.travel_time': 30,
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 3,
            'data.freq_mod_journeys.0.modes.0': 'car',
            'typo.reco.simple_labels.0': 'TIM',
            'typo.reco.complex_labels.0': 'car',
            'data.freq_mod_journeys.1.days': 2,
            'data.freq_mod_journeys.1.modes.0': 'bike',
            'typo.reco.simple_labels.1': 'MD',
            'typo.reco.complex_labels.1': 'bike',
            'typo.reco.reco_inter.0': 'inter',
            'typo.reco.reco_inter.1': 'velo',
        },
        {
            'token': 'B',
            'data.version': '3.0',
            'data.travel_time': 20,
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 5,
            'data.freq_mod_journeys.0.modes.0': 'pub',
            'typo.reco.simple_labels.0': 'TP',
            'typo.reco.complex_labels.0': 'pub',
            'typo.reco.reco_inter.0': 'train',
        },
    ])


def legacy_df() -> pd.DataFrame:
    """One person with two journeys and two general (non-journey-tied) recommendations."""
    return pd.DataFrame([
        {
            'token': 'C',
            'data.version': '3.0',
            'data.travel_time': 25,
            'data.origin.lat': 46.5, 'data.origin.lon': 6.6,
            'data.workplace.lat': 46.6, 'data.workplace.lon': 6.7,
            'data.freq_mod_journeys.0.days': 4,
            'data.freq_mod_journeys.0.modes.0': 'car',
            'data.freq_mod_journeys.1.days': 1,
            'data.freq_mod_journeys.1.modes.0': 'car',
            'typo.reco.reco_dt2.0': 'train',
            'typo.reco.reco_dt2.1': 'velo',
        },
    ])


def test_build_reco_weighted_new_style_matches_journey_index_and_days():
    service = BaseStatsService(pd.DataFrame())
    df = new_style_df()
    reco_df = service._build_reco_weighted(df)

    assert reco_df is not None
    rows = {(r.token, r.journey): (r.reco_mode, r.days) for r in reco_df.itertuples()}
    assert rows[('A', '0')] == ('inter', 3)
    assert rows[('A', '1')] == ('velo', 2)
    assert rows[('B', '0')] == ('train', 5)


def test_build_reco_weighted_legacy_weighted_by_total_days():
    service = BaseStatsService(pd.DataFrame())
    df = legacy_df()
    reco_df = service._build_reco_weighted(df)

    assert reco_df is not None
    rows = {(r.token, r.journey): (r.reco_mode, r.days) for r in reco_df.itertuples()}
    # both legacy recommendations are weighted by the sum of the person's journey days (4 + 1 = 5)
    assert rows[('C', 'legacy_0')] == ('train', 5)
    assert rows[('C', 'legacy_1')] == ('velo', 5)


def test_frequencies_reco_inter_counts_and_weights_each_recommendation():
    df = new_style_df()
    result = FrequenciesService(df).compute_recommendation_frequencies()

    assert result.field == 'reco_inter'
    by_value = {f.value: f for f in result.data}
    assert by_value['inter'].count == 1
    assert by_value['inter'].sum == 3
    assert by_value['velo'].count == 1
    assert by_value['velo'].sum == 2
    assert by_value['train'].count == 1
    assert by_value['train'].sum == 5


def test_frequencies_reco_simple_counts_and_weights_each_recommendation():
    df = new_style_df()
    df['typo.reco.reco_simple.0'] = ['TP', 'TP']
    df['typo.reco.reco_simple.1'] = ['MD', None]
    result = FrequenciesService(df).compute_recommendation_simple_frequencies()

    assert result.field == 'reco_simple'
    by_value = {f.value: f for f in result.data}
    # journey 0 of A (3 days) and journey 0 of B (5 days) both recommend 'TP'
    assert by_value['TP'].count == 2
    assert by_value['TP'].sum == 8
    # journey 1 of A (2 days) recommends 'MD'
    assert by_value['MD'].count == 1
    assert by_value['MD'].sum == 2


def test_frequencies_reco_simple_ignores_legacy_recommendations():
    df = legacy_df()
    result = FrequenciesService(df).compute_recommendation_simple_frequencies()

    # typo.reco.reco_dt2 has no simple counterpart: nothing to report
    assert result.field == 'reco_simple'
    assert result.data == []


def test_stats_frequencies_include_reco_inter_and_reco_simple():
    df = new_style_df()
    df['typo.reco.reco_simple.0'] = ['TP', 'TP']
    df['typo.reco.reco_simple.1'] = ['MD', None]
    stats = StatsService().compute_stats(df)

    fields = [f.field for f in stats.frequencies]
    assert 'reco_inter' in fields
    assert 'reco_simple' in fields


def test_links_reco_inter_matches_journey_not_always_first_index():
    df = new_style_df()
    result = LinksService(df).compute_mode_reco_links_complex_labels()

    links = {(l.source, l.target): l.value for l in result.data}
    # journey 0 (label 'car', 3 days) recommends 'inter': linked to car, weighted by 3 days
    assert links[('car', 'inter')] == 3
    # journey 1 (label 'bike', 2 days) recommends 'velo': linked to bike, weighted by 2 days,
    # NOT to 'inter' (which only applies to journey 0)
    assert ('bike', 'inter') not in links
    assert links[('bike', 'velo')] == 2
    # 'pub' folds into the merged 'tp' bucket of the complex labels
    assert links[('tp', 'train')] == 5


def test_equipments_reco_inter_counts_each_journey_recommendation():
    df = new_style_df()
    df['data.equipments.0'] = ['bike', None]
    result = EquipmentsService(df).compute_equipments_stats()

    matrix = result.equipment_recommendation_matrix
    # token A contributes one 'inter' and one 'velo' recommendation, each counted
    assert matrix.inter.total == 1
    assert matrix.velo.total == 1
    assert matrix.velo.bike == 1
    assert matrix.train.total == 1


def test_completed_filter_accepts_reco_inter_and_legacy_reco_dt2():
    df = pd.concat([new_style_df(), legacy_df()], ignore_index=True)
    completed = StatsService()._filter_completed_records(df)
    assert set(completed['token']) == {'A', 'B', 'C'}


def test_energy_reco_inter_applies_per_journey_recommendation():
    df = new_style_df()
    service = EnergyService(df)
    result = service.compute_modes_energy(apply_reco=True)

    for energy in result:
        assert energy.energy_kcal >= 0
        assert energy.journeys > 0


def test_behavior_change_reads_reco_inter_not_just_legacy_reco_dt2():
    """Regression test: BehaviorChangeService must aggregate typo.reco.reco_inter.N,
    not only the legacy typo.reco.reco_dt2.N prefix, otherwise every record
    collected after the reco_inter migration is silently dropped."""
    df = new_style_df()
    df['data.changes.0.motivation'] = [5, 4]
    df['data.changes.1.motivation'] = [3, None]

    result = BehaviorChangeService(df).compute_behavior_change_stats()

    total_motivation_responses = sum(
        m.response_count for m in result.motivation.by_mode_motivation)
    # token A answered motivation for both of its recommendations (inter, velo),
    # token B answered motivation for its single recommendation (train)
    assert total_motivation_responses == 3

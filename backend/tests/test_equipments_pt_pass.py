"""
Tests for the public transport pass statistics (typo.reco.pt_pass), which back
the admin chart counting, per pass type, the participants it was recommended to
and those already holding a matching subscription.

The pass is only suggested alongside a public transport recommendation, and the
equipment question only lists Swiss products: CFF half-fare / GA say nothing
about an SNCF pass, so that count stays unknown rather than zero.
"""
import pandas as pd
from api.services.stats.equipments import EquipmentsService


def make_df(records: list[dict]) -> pd.DataFrame:
    """Minimal v3 records: a pass, a recommendation and some equipment."""
    return pd.DataFrame([{'data.version': '3.0', **record} for record in records])


def by_pass(result) -> dict:
    return {item.pass_type: item for item in result}


def compute(records: list[dict]):
    service = EquipmentsService(make_df(records))
    return service.compute_equipments_stats().pt_pass_recommendations


def test_recommended_and_already_equipped():
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'unireso',
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'tpu_unireso',
        },
    ]))

    assert result['unireso'].recommended == 1
    assert result['unireso'].already_equipped == 1


def test_recommended_but_not_equipped():
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'unireso',
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'bike',
        },
    ]))

    assert result['unireso'].recommended == 1
    assert result['unireso'].already_equipped == 0


def test_pass_without_pt_recommendation_is_not_counted():
    # The toolkit fills pt_pass for everybody, but the collect form only shows
    # it next to a public transport recommendation.
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'unireso',
            'typo.reco.reco_inter.0': 'velo',
            'data.equipments.0': 'tpu_unireso',
        },
    ]))

    assert result['unireso'].recommended == 0
    assert result['unireso'].already_equipped == 0


def test_counted_once_per_participant():
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'leman',
            'typo.reco.reco_inter.0': 'tpu',
            'typo.reco.reco_inter.1': 'train',
            'data.equipments.0': 'tpu_leman_pass',
            'data.equipments.1': 'train_demi_tarif',
        },
    ]))

    assert result['leman'].recommended == 1
    assert result['leman'].already_equipped == 1


def test_legacy_recommendation_columns_are_taken_into_account():
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'leman',
            'typo.reco.reco_dt2.0': 'tpu',
            'data.equipments.0': 'tpu_leman_pass',
        },
    ]))

    assert result['leman'].recommended == 1
    assert result['leman'].already_equipped == 1


def test_cff_counts_half_fare_and_ga():
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'cff',
            'typo.reco.reco_inter.0': 'train',
            'data.equipments.0': 'train_demi_tarif',
        },
        {
            'typo.reco.pt_pass': 'cff',
            'typo.reco.reco_inter.0': 'train',
            'data.equipments.0': 'train_abo_gen',
        },
        {
            'typo.reco.pt_pass': 'cff',
            'typo.reco.reco_inter.0': 'train',
            'data.equipments.0': 'car',
        },
    ]))

    assert result['cff'].recommended == 3
    assert result['cff'].already_equipped == 2


def test_sncf_equipment_is_unknown():
    # train_demi_tarif / train_abo_gen are CFF products: they must not leak
    # into the SNCF bar, and no French product is collected.
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'sncf',
            'typo.reco.reco_inter.0': 'train',
            'data.equipments.0': 'train_demi_tarif',
        },
    ]))

    assert result['sncf'].recommended == 1
    assert result['sncf'].already_equipped is None


def test_unknown_pass_falls_back_to_other():
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'leman_pass',
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'tpu_leman_pass',
        },
    ]))

    assert result['other'].recommended == 1
    assert result['other'].already_equipped is None
    assert result['leman'].recommended == 0


def test_all_pass_types_are_always_returned_in_order():
    result = compute([
        {
            'typo.reco.pt_pass': 'unireso',
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'tpu_unireso',
        },
    ])

    assert [item.pass_type for item in result] == [
        'unireso', 'leman', 'cff', 'sncf', 'other']


def test_missing_pt_pass_column():
    result = compute([
        {
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'tpu_unireso',
        },
    ])

    assert result == []


def test_records_without_pt_pass_value_are_ignored():
    result = by_pass(compute([
        {
            'typo.reco.pt_pass': 'unireso',
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'tpu_unireso',
        },
        {
            'typo.reco.pt_pass': None,
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'tpu_unireso',
        },
    ]))

    assert result['unireso'].recommended == 1
    assert result['other'].recommended == 0


def test_legacy_records_are_excluded():
    df = pd.DataFrame([
        {
            'data.version': '2.0',
            'typo.reco.pt_pass': 'unireso',
            'typo.reco.reco_inter.0': 'tpu',
            'data.equipments.0': 'tpu_unireso',
        },
    ])
    stats = EquipmentsService(df).compute_equipments_stats()

    assert stats.total == 0
    assert stats.pt_pass_recommendations == []

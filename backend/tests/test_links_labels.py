"""
Tests for the mode recommendation links grouped by v3 typology labels
(typo.reco.simple_labels.N / typo.reco.complex_labels.N), which source each
link from one label bucket instead of each of the journey's raw modes --
mirroring how frequencies and emissions already group journeys by label.
"""
import pandas as pd
from api.services.stats.links import LinksService


def v3_df() -> pd.DataFrame:
    """
    Two v3 respondents with a per-journey recommendation:
    - A: journey 0 is single-mode 'car' (label 'TIM' / 'car'), 3 days,
      recommended 'train'; journey 1 is intermodal 'train'+'car' (label
      'TIM+TP' / 'car+pub'), 2 days, recommended 'inter'
    - B: journey 0 is single-mode 'pub' (label 'TP' / 'pub'), 5 days,
      recommended 'vae'
    Plus one v3 journey with no label at all (must be excluded) and one v2
    record (must be excluded entirely).
    """
    return pd.DataFrame([
        {
            'token': 'A',
            'data.version': '3.0',
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
            'data.freq_mod_journeys.0.days': 5,
            'data.freq_mod_journeys.0.modes.0': 'pub',
            'typo.reco.simple_labels.0': 'TP',
            'typo.reco.complex_labels.0': 'pub',
            'typo.reco.reco_inter.0': 'vae',
        },
        {
            'token': 'C',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 4,
            'data.freq_mod_journeys.0.modes.0': 'bike',
            'typo.reco.reco_inter.0': 'velo',
            # no simple/complex label for this journey: must be excluded
        },
        {
            'token': 'D',
            'data.version': '2.0',
            'data.freq_mod_journeys.0.days': 10,
            'data.freq_mod_journeys.0.modes.0': 'plane',
            'typo.reco.reco_inter.0': 'train',
            # v2 record: even if it had labels, it must be excluded by the v3 filter
        },
    ])


def legacy_df() -> pd.DataFrame:
    """One v3 respondent with two labelled journeys and two general (non
    journey-tied) recommendations."""
    return pd.DataFrame([
        {
            'token': 'E',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 4,
            'data.freq_mod_journeys.0.modes.0': 'car',
            'typo.reco.simple_labels.0': 'TIM',
            'typo.reco.complex_labels.0': 'car',
            'data.freq_mod_journeys.1.days': 1,
            'data.freq_mod_journeys.1.modes.0': 'pub',
            'typo.reco.simple_labels.1': 'TP',
            'typo.reco.complex_labels.1': 'pub',
            'typo.reco.reco_dt2.0': 'train',
            'typo.reco.reco_dt2.1': 'velo',
        },
    ])


def as_dict(result):
    return {(link.source, link.target): link.value for link in result.data}


def test_compute_mode_reco_links_simple_labels():
    result = LinksService(v3_df()).compute_mode_reco_links_simple_labels()

    links = as_dict(result)
    assert links == {
        ('TIM', 'train'): 3,
        ('TIM+TP', 'inter'): 2,
        ('TP', 'vae'): 5,
    }
    # the intermodal journey is credited to its single label, not to each of
    # its raw modes
    assert ('car', 'inter') not in links
    assert ('train', 'inter') not in links
    # total counts all v3 records, including the unlabelled one
    assert result.total == 3
    assert result.most_recommended_target is not None
    assert result.most_recommended_target.target == 'vae'
    assert result.most_recommended_target.value == 5


def test_compute_mode_reco_links_complex_labels_merges_tp_bucket():
    result = LinksService(v3_df()).compute_mode_reco_links_complex_labels()

    links = as_dict(result)
    # 'pub' -> 'tp' and 'car+pub' -> 'car+tp', component-wise
    assert links == {
        ('car', 'train'): 3,
        ('car+tp', 'inter'): 2,
        ('tp', 'vae'): 5,
    }


def test_compute_mode_reco_links_labels_legacy_recommendations():
    """Legacy typo.reco.reco_dt2.N are not tied to a journey: every labelled
    journey links to each of them, weighted by the person's total days."""
    result = LinksService(legacy_df()).compute_mode_reco_links_simple_labels()

    links = as_dict(result)
    assert links == {
        ('TIM', 'train'): 5,
        ('TIM', 'velo'): 5,
        ('TP', 'train'): 5,
        ('TP', 'velo'): 5,
    }


def test_compute_mode_reco_links_no_labels():
    """Records without any typology label produce no links."""
    df = pd.DataFrame([
        {
            'token': 'F',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 3,
            'data.freq_mod_journeys.0.modes.0': 'car',
            'typo.reco.reco_inter.0': 'train',
        },
    ])
    service = LinksService(df)

    assert service.compute_mode_reco_links_simple_labels().data == []
    assert service.compute_mode_reco_links_complex_labels().data == []


def test_compute_mode_reco_links_labels_ignores_zero_and_invalid_days():
    df = pd.DataFrame([
        {
            'token': 'G',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 0,
            'typo.reco.simple_labels.0': 'TIM',
            'typo.reco.reco_inter.0': 'train',
            'data.freq_mod_journeys.1.days': 'n/a',
            'typo.reco.simple_labels.1': 'TP',
            'typo.reco.reco_inter.1': 'velo',
            'data.freq_mod_journeys.2.days': 2.7,
            'typo.reco.simple_labels.2': 'MD',
            'typo.reco.reco_inter.2': 'vae',
        },
    ])
    result = LinksService(df).compute_mode_reco_links_simple_labels()

    # zero-day and non-numeric journeys are dropped, fractional days truncate
    assert as_dict(result) == {('MD', 'vae'): 2}

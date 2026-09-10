"""
Tests for the person-centric home-to-work modal split (#407): the modal split,
potential modal split and modal shift charts count persons, not journeys. Each
person counts once, for their main journey: the most frequent one, ties being
broken by the first one entered.
"""
import pandas as pd
from api.services.stats.frequencies import FrequenciesService


def modal_split_df() -> pd.DataFrame:
    """
    Four v3 respondents:
    - A: 'car' 3 days a week, 'bike' 2 days -> counts as car (TIM)
    - B: 'pub' 2 days, 'car' 2 days -> tie, counts as the first entered (TP)
    - C: 'train' 5 days -> counts as public transport, 'train' folding into the
      merged 'tp' bucket of the complex labels
    - D: no journey frequency at all -> counts nowhere
    """
    return pd.DataFrame([
        {
            'token': 'A',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 3,
            'typo.reco.simple_labels.0': 'TIM',
            'typo.reco.complex_labels.0': 'car',
            'data.freq_mod_journeys.1.days': 2,
            'typo.reco.simple_labels.1': 'MD',
            'typo.reco.complex_labels.1': 'bike',
        },
        {
            'token': 'B',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 2,
            'typo.reco.simple_labels.0': 'TP',
            'typo.reco.complex_labels.0': 'pub',
            'data.freq_mod_journeys.1.days': 2,
            'typo.reco.simple_labels.1': 'TIM',
            'typo.reco.complex_labels.1': 'car',
        },
        {
            'token': 'C',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 5,
            'typo.reco.simple_labels.0': 'TP',
            'typo.reco.complex_labels.0': 'train',
        },
        {
            'token': 'D',
            'data.version': '3.0',
            'data.freq_mod_journeys.0.days': 0,
            'typo.reco.simple_labels.0': 'MD',
            'typo.reco.complex_labels.0': 'walking',
        },
    ])


def counts_by_label(frequencies) -> dict:
    return {f.field: sum(d.count for d in f.data) for f in frequencies}


def test_simple_labels_modal_split_counts_persons_once():
    result = FrequenciesService(modal_split_df()
                                ).compute_modes_frequencies_simple_labels()

    # A -> TIM (3 days beats 2), B -> TP (tie broken by the first entered),
    # C -> TP; D declared no journey frequency and counts nowhere
    # 'MD' is nobody's main mode: no empty share is reported for it
    assert counts_by_label(result) == {'TIM': 1, 'TP': 2}
    # shares are person shares: no days weighting is exposed
    assert all(d.sum is None for f in result for d in f.data)
    # the days frequency of the main journey stays the histogram key
    tim = next(f for f in result if f.field == 'TIM')
    assert [(d.value, d.count) for d in tim.data] == [('3', 1)]


def test_complex_labels_modal_split_counts_persons_once():
    result = FrequenciesService(modal_split_df()
                                ).compute_modes_frequencies_complex_labels()

    # 'train' folds into the merged 'tp' bucket, together with 'pub'
    assert counts_by_label(result) == {'car': 1, 'tp': 2}
    assert all(d.sum is None for f in result for d in f.data)


def test_modal_split_totals_are_the_number_of_records():
    df = modal_split_df()
    result = FrequenciesService(df).compute_modes_frequencies_simple_labels()

    assert all(f.total == len(df) for f in result)
    # one count per person having a journey, whatever their number of journeys
    assert sum(sum(d.count for d in f.data) for f in result) == 3

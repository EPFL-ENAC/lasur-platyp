import pandas as pd

from api.models.query import CampaignGroup
from api.services.stats.longitudinal import LongitudinalService


def make_group(name, campaign_ids):
    return CampaignGroup(name=name, campaign_ids=campaign_ids)


def test_filter_longitudinal_empty_dataframe():
    df = pd.DataFrame()
    result = LongitudinalService.filter_longitudinal(
        df, [make_group("A", [1]), make_group("B", [2])])
    assert result.empty


def test_filter_longitudinal_excludes_null_email_hash():
    df = pd.DataFrame({
        "email_hash": [None, "h1", "h1"],
        "campaign_id": [1, 1, 2],
    })
    groups = [make_group("A", [1]), make_group("B", [2])]
    result = LongitudinalService.filter_longitudinal(df, groups)
    assert result["email_hash"].notna().all()
    assert len(result) == 2


def test_filter_longitudinal_requires_all_groups():
    df = pd.DataFrame({
        "email_hash": ["h1", "h2", "h2"],
        "campaign_id": [1, 1, 2],
    })
    groups = [make_group("A", [1]), make_group("B", [2])]
    result = LongitudinalService.filter_longitudinal(df, groups)
    # h1 only appears in group A -> excluded; h2 appears in both -> kept
    assert set(result["email_hash"]) == {"h2"}
    assert len(result) == 2


def test_filter_longitudinal_excludes_partial_participation():
    """With 3 groups, being in 2 of them is not enough: the panel is the
    strict intersection of all groups."""
    df = pd.DataFrame({
        "email_hash": ["h1", "h1", "h2", "h2", "h2"],
        "campaign_id": [1, 2, 1, 2, 3],
    })
    groups = [make_group("A", [1]), make_group("B", [2]), make_group("C", [3])]
    result = LongitudinalService.filter_longitudinal(df, groups)
    assert set(result["email_hash"]) == {"h2"}
    assert len(result) == 3


def test_filter_longitudinal_any_campaign_of_a_group_counts():
    """A group made of several campaigns counts as attended if the participant
    appears in any one of its campaigns."""
    df = pd.DataFrame({
        "email_hash": ["h1", "h1"],
        "campaign_id": [1, 3],
    })
    groups = [make_group("A", [1, 2]), make_group("B", [3, 4])]
    result = LongitudinalService.filter_longitudinal(df, groups)
    assert set(result["email_hash"]) == {"h1"}
    assert len(result) == 2


def test_compute_mode_transitions_consecutive_pairs_only():
    df = pd.DataFrame({
        "email_hash": ["h1", "h1", "h1"],
        "campaign_id": [1, 2, 3],
        "typo.reco.simple_labels.0": ["car", "bike", "walk"],
    })
    groups = [make_group("A", [1]), make_group("B", [2]), make_group("C", [3])]
    result = LongitudinalService.compute_mode_transitions(df, groups)
    assert result.total == 1
    transitions = result.data

    pairs = {(t.source_group, t.target_group) for t in transitions}
    assert pairs == {("A", "B"), ("B", "C")}
    assert ("A", "C") not in pairs

    ab = next(t for t in transitions if t.source_group ==
              "A" and t.target_group == "B")
    assert ab.source_mode == "car"
    assert ab.target_mode == "bike"
    assert ab.count == 1


def test_compute_mode_transitions_dropped_group_not_bridged():
    """If a group has no surviving data (e.g. privacy-dropped), its adjacent
    transitions are omitted entirely rather than bridging A directly to C."""
    df = pd.DataFrame({
        "email_hash": ["h1", "h1"],
        "campaign_id": [1, 3],
        "typo.reco.simple_labels.0": ["car", "walk"],
    })
    groups = [make_group("A", [1]), make_group("B", [2]), make_group("C", [3])]
    result = LongitudinalService.compute_mode_transitions(df, groups)
    assert result.data == []
    assert result.total == 0


def test_compute_mode_transitions_tie_break_first_encountered():
    df = pd.DataFrame({
        "email_hash": ["h1", "h1", "h1"],
        "campaign_id": [1, 1, 2],
        "typo.reco.simple_labels.0": ["car", "bike", "walk"],
    })
    groups = [make_group("A", [1]), make_group("B", [2])]
    transitions = LongitudinalService.compute_mode_transitions(df, groups).data
    assert len(transitions) == 1
    # "car" and "bike" are tied at count 1 within group A -> first encountered wins
    assert transitions[0].source_mode == "car"
    assert transitions[0].target_mode == "walk"


def test_compute_mode_transitions_complex_labels_merges_components():
    """The detailed variant reads complex labels and folds COMPLEX_LABEL_MERGE
    component-wise, so 'pub' and 'train' journeys count as one 'tp' bucket."""
    df = pd.DataFrame({
        "email_hash": ["h1", "h1"],
        "campaign_id": [1, 2],
        "typo.reco.simple_labels.0": ["TP", "MA"],
        "typo.reco.complex_labels.0": ["pub", "car+train"],
        "typo.reco.complex_labels.1": ["train", None],
        "typo.reco.complex_labels.2": ["bike", None],
    })
    groups = [make_group("A", [1]), make_group("B", [2])]
    result = LongitudinalService.compute_mode_transitions_complex_labels(
        df, groups)
    assert result.total == 1
    transitions = result.data
    assert len(transitions) == 1
    # pub + train fold into tp (2) which beats bike (1); car+train -> car+tp
    assert transitions[0].source_mode == "tp"
    assert transitions[0].target_mode == "car+tp"
    assert transitions[0].count == 1

    # the simple variant is unaffected
    simple = LongitudinalService.compute_mode_transitions(df, groups).data
    assert (simple[0].source_mode, simple[0].target_mode) == ("TP", "MA")


def test_compute_mode_transitions_total_counts_distinct_participants():
    """A participant spanning several consecutive pairs counts once; one whose
    only groups are not consecutive contributes no transition and is not counted."""
    df = pd.DataFrame({
        "email_hash": ["h1", "h1", "h1", "h2", "h2", "h3", "h3"],
        "campaign_id": [1, 2, 3, 1, 2, 1, 3],
        "typo.reco.simple_labels.0": ["TP", "MA", "MA", "TP", "TP", "MA", "TP"],
    })
    groups = [make_group("A", [1]), make_group("B", [2]), make_group("C", [3])]
    result = LongitudinalService.compute_mode_transitions(df, groups)
    assert result.total == 2
    assert sum(t.count for t in result.data) == 3

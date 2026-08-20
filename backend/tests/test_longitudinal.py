import pandas as pd

from api.models.query import CampaignGroup, ModeTransition
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


def test_filter_longitudinal_requires_two_groups():
    df = pd.DataFrame({
        "email_hash": ["h1", "h2", "h2"],
        "campaign_id": [1, 1, 2],
    })
    groups = [make_group("A", [1]), make_group("B", [2])]
    result = LongitudinalService.filter_longitudinal(df, groups)
    # h1 only appears in group A -> excluded; h2 appears in both -> kept
    assert set(result["email_hash"]) == {"h2"}
    assert len(result) == 2


def test_compute_mode_transitions_consecutive_pairs_only():
    df = pd.DataFrame({
        "email_hash": ["h1", "h1", "h1"],
        "campaign_id": [1, 2, 3],
        "typo.reco.simple_labels.0": ["car", "bike", "walk"],
    })
    groups = [make_group("A", [1]), make_group("B", [2]), make_group("C", [3])]
    transitions = LongitudinalService.compute_mode_transitions(df, groups)

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
    transitions = LongitudinalService.compute_mode_transitions(df, groups)
    assert transitions == []


def test_compute_mode_transitions_tie_break_first_encountered():
    df = pd.DataFrame({
        "email_hash": ["h1", "h1", "h1"],
        "campaign_id": [1, 1, 2],
        "typo.reco.simple_labels.0": ["car", "bike", "walk"],
    })
    groups = [make_group("A", [1]), make_group("B", [2])]
    transitions = LongitudinalService.compute_mode_transitions(df, groups)
    assert len(transitions) == 1
    # "car" and "bike" are tied at count 1 within group A -> first encountered wins
    assert transitions[0].source_mode == "car"
    assert transitions[0].target_mode == "walk"

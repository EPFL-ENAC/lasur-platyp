import pandas as pd
from api.services.stats.behavior_change import BehaviorChangeService
from api.services.stats.stats import StatsService
from api.models.query import BehaviorChangeStats


def load_test_dataframe() -> pd.DataFrame:
    """Load test CSV into a DataFrame."""
    df = pd.read_csv('tests/data/records.csv')
    stats = StatsService()
    df = stats._preprocess_dataframe(df)
    return df


def create_test_dataframe_with_behavior_change(
    mode_counts: dict,
    motivations: dict = None,
    levers: dict = None
) -> pd.DataFrame:
    """
    Create a test DataFrame with specific mode counts and behavior change data.

    Args:
        mode_counts: {'velo': 15, 'train': 8, 'tpu': 5}
        motivations: {'velo': [5,5,4,3,2], 'train': [4,4,3]} - actual values per person
        levers: {'velo': ['finance', 'flexibility'], 'train': ['environment']} - actual values per person

    Note: People may have recommendations but not answer questions.
          len(motivations[mode]) = number of people who answered motivation for that mode
          len(levers[mode]) = number of people who answered levers for that mode
    """
    rows = []
    for mode, count in mode_counts.items():
        for i in range(count):
            row = {
                'typo.reco.reco_dt2.0': mode,
                'data.changes.0.motivation': None,
                'data.changes.0.levers.0': None,
                'data.changes.0.levers.1': None,
                'data.changes.0.levers.2': None,
                'data.changes.0.other_levers': None
            }

            # Add motivation if this person answered (based on list length)
            if motivations and mode in motivations and i < len(motivations[mode]):
                row['data.changes.0.motivation'] = motivations[mode][i]

            # Add levers if this person answered (based on list length)
            if levers and mode in levers and i < len(levers[mode]):
                lever_val = levers[mode][i]
                # Put the lever in the first column for simplicity
                row['data.changes.0.levers.0'] = lever_val

            rows.append(row)

    return pd.DataFrame(rows)


# ===== Tests for lever aggregation =====

def test_levers_less_than_10_responses_all_aggregated():
    """Test that < 10 lever responses are aggregated across all modes."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10, 'train': 10, 'tpu': 10},  # 30 recommendations
        levers={
            'velo': ['finance'] * 3,  # Only 3 answered levers
            'train': ['flexibility'] * 2,  # Only 2 answered levers
            'tpu': ['environment'] * 3  # Only 3 answered levers
        }  # Total: 8 lever responses < 10
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.levers.total_responses == 8
    assert result.levers.aggregation_type == 'all_aggregated'
    assert len(result.levers.by_mode_levers) == 1
    assert result.levers.by_mode_levers[0].mode == 'allModes'
    assert result.levers.by_mode_levers[0].response_count == 8


def test_levers_10_or_more_no_mode_above_threshold():
    """Test that >= 10 lever responses but no mode >= 10 are still aggregated."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 20, 'tpu': 20},  # 60 recommendations
        levers={
            'velo': ['finance'] * 4,  # 4 answered
            'train': ['flexibility'] * 3,  # 3 answered
            'tpu': ['environment'] * 3,  # 3 answered
            # This shouldn't appear - no recommendations
            'inter': ['other'] * 2
        }  # Total: 10 lever responses, but no mode has 10
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.levers.total_responses == 10
    assert result.levers.aggregation_type == 'all_aggregated'
    assert len(result.levers.by_mode_levers) == 1
    assert result.levers.by_mode_levers[0].mode == 'allModes'


def test_levers_one_mode_above_threshold():
    """Test lever split when one mode has >= 10 lever responses."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 10, 'tpu': 10},
        levers={
            'velo': ['finance'] * 15,  # 15 answered levers for velo
            'train': ['flexibility'] * 5,  # 5 for train
            'tpu': ['environment'] * 3  # 3 for tpu
        }
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.levers.total_responses == 23
    assert result.levers.aggregation_type == 'mixed'
    assert len(result.levers.by_mode_levers) == 3  # velo, Autres, Total

    # Check velo stats
    velo_stats = next(
        m for m in result.levers.by_mode_levers if m.mode == 'velo')
    assert velo_stats.response_count == 15

    # Check Autres stats (train + tpu)
    autres_stats = next(
        m for m in result.levers.by_mode_levers if m.mode == 'Autres')
    assert autres_stats.response_count == 8

    # Check Total stats
    total_stats = next(
        m for m in result.levers.by_mode_levers if m.mode == 'Total')
    assert total_stats.response_count == 23


def test_levers_multiple_modes_above_threshold():
    """Test lever split when multiple modes have >= 10 lever responses."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 20, 'tpu': 10},
        levers={
            'velo': ['finance'] * 15,
            'train': ['flexibility'] * 12,
            'tpu': ['environment'] * 5
        }
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.levers.total_responses == 32
    assert result.levers.aggregation_type == 'mixed'
    assert len(result.levers.by_mode_levers) == 4  # velo, train, Autres, Total

    velo_stats = next(
        m for m in result.levers.by_mode_levers if m.mode == 'velo')
    assert velo_stats.response_count == 15

    train_stats = next(
        m for m in result.levers.by_mode_levers if m.mode == 'train')
    assert train_stats.response_count == 12

    autres_stats = next(
        m for m in result.levers.by_mode_levers if m.mode == 'Autres')
    assert autres_stats.response_count == 5


# ===== Tests for motivation aggregation =====

def test_motivation_less_than_10_responses_all_aggregated():
    """Test that < 10 motivation responses are aggregated across all modes."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10, 'train': 10, 'tpu': 10},
        motivations={
            'velo': [5, 4, 3],  # Only 3 answered
            'train': [4, 3],  # Only 2 answered
            'tpu': [5, 4, 2]  # Only 3 answered
        }  # Total: 8 motivation responses < 10
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.motivation.total_responses == 8
    assert result.motivation.aggregation_type == 'all_aggregated'
    assert len(result.motivation.by_mode_motivation) == 1
    assert result.motivation.by_mode_motivation[0].mode == 'allModes'
    assert result.motivation.by_mode_motivation[0].response_count == 8


def test_motivation_10_or_more_no_mode_above_threshold():
    """Test that >= 10 motivation responses but no mode >= 10 are still aggregated."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 20, 'tpu': 20},
        motivations={
            'velo': [5, 4, 3, 2],  # 4 answered
            'train': [4, 3, 2],  # 3 answered
            'tpu': [5, 4, 3]  # 3 answered
        }  # Total: 10 motivation responses, but no mode has 10
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.motivation.total_responses == 10
    assert result.motivation.aggregation_type == 'all_aggregated'
    assert len(result.motivation.by_mode_motivation) == 1
    assert result.motivation.by_mode_motivation[0].mode == 'allModes'


def test_motivation_one_mode_above_threshold():
    """Test motivation split when one mode has >= 10 motivation responses."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 10, 'tpu': 10},
        motivations={
            'velo': [5]*8 + [4]*5 + [3]*2,  # 15 answered
            'train': [4]*3 + [3]*2,  # 5 answered
            'tpu': [5, 4, 3]  # 3 answered
        }
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.motivation.total_responses == 23
    assert result.motivation.aggregation_type == 'mixed'
    # velo, Autres, Total
    assert len(result.motivation.by_mode_motivation) == 3

    velo_stats = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'velo')
    assert velo_stats.response_count == 15

    autres_stats = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'Autres')
    assert autres_stats.response_count == 8

    total_stats = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'Total')
    assert total_stats.response_count == 23


def test_motivation_multiple_modes_above_threshold():
    """Test motivation split when multiple modes have >= 10 motivation responses."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 20, 'tpu': 10},
        motivations={
            'velo': [5]*8 + [4]*5 + [3]*2,  # 15 answered
            'train': [5]*6 + [4]*4 + [3]*2,  # 12 answered
            'tpu': [4]*3 + [3]*2  # 5 answered
        }
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.motivation.total_responses == 32
    assert result.motivation.aggregation_type == 'mixed'
    # velo, train, Autres, Total
    assert len(result.motivation.by_mode_motivation) == 4

    velo_stats = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'velo')
    assert velo_stats.response_count == 15

    train_stats = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'train')
    assert train_stats.response_count == 12

    autres_stats = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'Autres')
    assert autres_stats.response_count == 5


# ===== Tests for unified aggregation (Option A) =====

def test_independent_aggregation_different_splits():
    """
    Test unified aggregation strategy: a mode is shown individually if it reaches
    >=10 responses for EITHER levers OR motivation (Option A).

    In this test:
    - velo: 15 motivation, 8 levers -> shown individually (motivation >= 10)
    - train: 5 motivation, 12 levers -> shown individually (levers >= 10)
    - tpu: 3 motivation, 4 levers -> aggregated (neither >= 10)
    """
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 20, 'tpu': 10},
        motivations={
            'velo': [5] * 15,  # 15 motivation responses for velo (>= 10)
            'train': [4] * 5,  # 5 motivation responses for train (< 10)
            'tpu': [3] * 3  # 3 motivation responses for tpu (< 10)
        },
        levers={
            'velo': ['finance'] * 8,  # 8 lever responses for velo (< 10)
            # 12 lever responses for train (>= 10)
            'train': ['flexibility'] * 12,
            'tpu': ['environment'] * 4  # 4 lever responses for tpu (< 10)
        }
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    # Both metrics use unified aggregation: velo and train shown individually, tpu aggregated
    assert result.motivation.aggregation_type == 'mixed'
    assert result.levers.aggregation_type == 'mixed'

    # Motivation: velo and train individually, tpu in Autres, plus Total
    # velo, train, Autres, Total
    assert len(result.motivation.by_mode_motivation) == 4
    motivation_modes = [m.mode for m in result.motivation.by_mode_motivation]
    assert 'velo' in motivation_modes
    assert 'train' in motivation_modes
    assert 'Autres' in motivation_modes
    assert 'Total' in motivation_modes

    # Levers: same grouping as motivation (unified strategy)
    assert len(result.levers.by_mode_levers) == 4  # velo, train, Autres, Total
    lever_modes = [m.mode for m in result.levers.by_mode_levers]
    assert 'velo' in lever_modes
    assert 'train' in lever_modes
    assert 'Autres' in lever_modes
    assert 'Total' in lever_modes


def test_unified_aggregation_option_a_edge_cases():
    """
    Comprehensive test for Option A: Show mode individually if EITHER 
    lever count >= 10 OR motivation count >= 10.

    Test scenarios:
    1. bike: 12 levers, 7 motivation -> Individual (levers >= 10)
    2. train: 6 levers, 15 motivation -> Individual (motivation >= 10)
    3. car: 11 levers, 11 motivation -> Individual (both >= 10)
    4. walk: 8 levers, 9 motivation -> Aggregated (neither >= 10)
    5. bus: 5 levers, 3 motivation -> Aggregated (neither >= 10)
    """
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'bike': 20, 'train': 20,
                     'car': 20, 'walk': 20, 'bus': 20},
        levers={
            'bike': ['finance'] * 12,      # 12 >= 10 -> Individual
            'train': ['flexibility'] * 6,  # 6 < 10, but motivation >= 10
            'car': ['environment'] * 11,   # 11 >= 10 -> Individual
            'walk': ['finance'] * 8,       # 8 < 10
            'bus': ['flexibility'] * 5     # 5 < 10
        },
        motivations={
            'bike': [5] * 7,    # 7 < 10, but levers >= 10
            'train': [4] * 15,  # 15 >= 10 -> Individual
            'car': [3] * 11,    # 11 >= 10 -> Individual
            'walk': [2] * 9,    # 9 < 10
            'bus': [1] * 3      # 3 < 10
        }
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    # Aggregation type should be mixed
    assert result.levers.aggregation_type == 'mixed'
    assert result.motivation.aggregation_type == 'mixed'

    # Check modes: bike, train, car individually; walk+bus in Autres; plus Total
    # bike, train, car, Autres, Total
    assert len(result.levers.by_mode_levers) == 5
    lever_modes = [m.mode for m in result.levers.by_mode_levers]
    assert 'bike' in lever_modes
    assert 'train' in lever_modes
    assert 'car' in lever_modes
    assert 'Autres' in lever_modes
    assert 'Total' in lever_modes

    # Same for motivation
    assert len(result.motivation.by_mode_motivation) == 5
    motivation_modes = [m.mode for m in result.motivation.by_mode_motivation]
    assert 'bike' in motivation_modes
    assert 'train' in motivation_modes
    assert 'car' in motivation_modes
    assert 'Autres' in motivation_modes
    assert 'Total' in motivation_modes

    # Verify response counts
    bike_levers = next(
        m for m in result.levers.by_mode_levers if m.mode == 'bike')
    assert bike_levers.response_count == 12

    train_motivation = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'train')
    assert train_motivation.response_count == 15

    # Verify Autres aggregates walk and bus
    autres_levers = next(
        m for m in result.levers.by_mode_levers if m.mode == 'Autres')
    assert autres_levers.response_count == 13  # 8 + 5

    autres_motivation = next(
        m for m in result.motivation.by_mode_motivation if m.mode == 'Autres')
    assert autres_motivation.response_count == 12  # 9 + 3


# ===== Tests for percentages and counts =====

def test_lever_percentages_computed_correctly():
    """Test that lever percentages are computed correctly."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        levers={'velo': ['finance']*5 + ['flexibility']*3 + ['environment']*2}
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    mode_stats = result.levers.by_mode_levers[0]
    assert mode_stats.response_count == 10

    # Check percentages (based on total lever selections)
    finance = next(l for l in mode_stats.levers if l.category == 'finance')
    assert finance.count == 5
    assert finance.percentage == 50.0

    flexibility = next(
        l for l in mode_stats.levers if l.category == 'flexibility')
    assert flexibility.count == 3
    assert flexibility.percentage == 30.0

    environment = next(
        l for l in mode_stats.levers if l.category == 'environment')
    assert environment.count == 2
    assert environment.percentage == 20.0


def test_motivation_percentages_computed_correctly():
    """Test that motivation percentages are computed correctly."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        motivations={'velo': [5]*4 + [4]*3 + [3]*2 + [2]*1}
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    mode_stats = result.motivation.by_mode_motivation[0]
    assert mode_stats.response_count == 10

    # Check percentages
    level_5 = next(m for m in mode_stats.motivations if m.level == 5)
    assert level_5.count == 4
    assert level_5.percentage == 40.0

    level_4 = next(m for m in mode_stats.motivations if m.level == 4)
    assert level_4.count == 3
    assert level_4.percentage == 30.0

    level_3 = next(m for m in mode_stats.motivations if m.level == 3)
    assert level_3.count == 2
    assert level_3.percentage == 20.0

    level_2 = next(m for m in mode_stats.motivations if m.level == 2)
    assert level_2.count == 1
    assert level_2.percentage == 10.0


def test_zero_counts_included():
    """Test that categories with 0 count are still included."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        motivations={'velo': [5]*10},  # Only level 5
        levers={'velo': ['finance']*10}  # Only finance
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    mode_stats_motivation = result.motivation.by_mode_motivation[0]
    mode_stats_levers = result.levers.by_mode_levers[0]

    # All 5 motivation levels should be present
    assert len(mode_stats_motivation.motivations) == 5
    level_1 = next(
        m for m in mode_stats_motivation.motivations if m.level == 1)
    assert level_1.count == 0
    assert level_1.percentage == 0.0

    # All 5 lever categories should be present
    assert len(mode_stats_levers.levers) == 9
    flexibility = next(
        l for l in mode_stats_levers.levers if l.category == 'flexibility')
    assert flexibility.count == 0
    assert flexibility.percentage == 0.0


def test_empty_data_handling():
    """Test graceful handling of empty data."""
    df = pd.DataFrame({
        'typo.reco.reco_dt2.0': [],
        'data.changes.0.motivation': [],
        'data.changes.0.levers.0': [],
        'data.changes.0.levers.1': [],
        'data.changes.0.levers.2': []
    })

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    assert result.levers.total_responses == 0
    assert result.motivation.total_responses == 0
    assert len(result.levers.by_mode_levers) == 0
    assert len(result.motivation.by_mode_motivation) == 0


def test_other_levers_extracted():
    """Test that other_levers text is extracted correctly."""
    data = {
        'typo.reco.reco_dt2.0': ['velo', 'train', 'tpu'],
        'data.changes.0.motivation': [5, 4, 3],
        'data.changes.0.levers.0': ['finance', 'flexibility', 'other'],
        'data.changes.0.levers.1': [None, None, None],
        'data.changes.0.levers.2': [None, None, None],
        'data.changes.0.other_levers': ['More parking', '', 'Better infrastructure']
    }
    df = pd.DataFrame(data)

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    # Should have 2 non-empty other_levers
    assert len(result.other_levers) == 2
    assert 'More parking' in result.other_levers
    assert 'Better infrastructure' in result.other_levers


def test_integration_with_stats_service():
    """Test that behavior change stats are integrated with StatsService."""
    df = load_test_dataframe()

    stats_service = StatsService()
    stats = stats_service.compute_stats(df)

    # Should have behavior_change field
    assert stats.behavior_change is not None
    assert isinstance(stats.behavior_change, BehaviorChangeStats)
    assert stats.behavior_change.levers.total_responses >= 0
    assert stats.behavior_change.motivation.total_responses >= 0


def test_motivation_levels_ordered_highest_first():
    """Test that motivation levels are ordered from 5 (most) down to 1 (least)."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        motivations={'velo': [5]*10},
        levers={'velo': ['finance']*10}
    )

    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()

    mode_stats_motivation = result.motivation.by_mode_motivation[0]
    mode_stats_levers = result.levers.by_mode_levers[0]

    # Motivation levels run [5, 4, 3, 2, 1]
    levels = [m.level for m in mode_stats_motivation.motivations]
    assert levels == [5, 4, 3, 2, 1]

    # Lever categories include the expected keys
    categories = [l.category for l in mode_stats_levers.levers]
    assert 'finance' in categories
    assert 'flexibility' in categories
    assert 'environment' in categories

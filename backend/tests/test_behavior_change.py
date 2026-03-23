import pandas as pd
from api.services.stats.behavior_change import BehaviorChangeService
from api.services.stats.stats import StatsService
from api.models.query import (
    BehaviorChangeStats, BehaviorChangeByMode,
    BehaviorChangeLever, BehaviorChangeMotivation
)


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
                'data.change.motivation': None,
                'data.change.levers.0': None,
                'data.change.levers.1': None,
                'data.change.levers.2': None,
                'data.change.other_levers': None
            }
            
            # Add motivation if this person answered (based on list length)
            if motivations and mode in motivations and i < len(motivations[mode]):
                row['data.change.motivation'] = motivations[mode][i]
            
            # Add levers if this person answered (based on list length)
            if levers and mode in levers and i < len(levers[mode]):
                lever_val = levers[mode][i]
                # Put the lever in the first column for simplicity
                row['data.change.levers.0'] = lever_val
            
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
    
    assert result.total_lever_responses == 8
    assert result.lever_aggregation_type == 'all_aggregated'
    assert len(result.by_mode_levers) == 1
    assert result.by_mode_levers[0].mode == 'Tous modes'
    assert result.by_mode_levers[0].response_count == 8


def test_levers_10_or_more_no_mode_above_threshold():
    """Test that >= 10 lever responses but no mode >= 10 are still aggregated."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 20, 'tpu': 20},  # 60 recommendations
        levers={
            'velo': ['finance'] * 4,  # 4 answered
            'train': ['flexibility'] * 3,  # 3 answered
            'tpu': ['environment'] * 3,  # 3 answered
            'inter': ['other'] * 2  # This shouldn't appear - no recommendations
        }  # Total: 10 lever responses, but no mode has 10
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    assert result.total_lever_responses == 10
    assert result.lever_aggregation_type == 'all_aggregated'
    assert len(result.by_mode_levers) == 1
    assert result.by_mode_levers[0].mode == 'Tous modes'


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
    
    assert result.total_lever_responses == 23
    assert result.lever_aggregation_type == 'mixed'
    assert len(result.by_mode_levers) == 3  # velo, Autres, Total
    
    # Check velo stats
    velo_stats = next(m for m in result.by_mode_levers if m.mode == 'velo')
    assert velo_stats.response_count == 15
    
    # Check Autres stats (train + tpu)
    autres_stats = next(m for m in result.by_mode_levers if m.mode == 'Autres')
    assert autres_stats.response_count == 8
    
    # Check Total stats
    total_stats = next(m for m in result.by_mode_levers if m.mode == 'Total')
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
    
    assert result.total_lever_responses == 32
    assert result.lever_aggregation_type == 'mixed'
    assert len(result.by_mode_levers) == 4  # velo, train, Autres, Total
    
    velo_stats = next(m for m in result.by_mode_levers if m.mode == 'velo')
    assert velo_stats.response_count == 15
    
    train_stats = next(m for m in result.by_mode_levers if m.mode == 'train')
    assert train_stats.response_count == 12
    
    autres_stats = next(m for m in result.by_mode_levers if m.mode == 'Autres')
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
    
    assert result.total_motivation_responses == 8
    assert result.motivation_aggregation_type == 'all_aggregated'
    assert len(result.by_mode_motivation) == 1
    assert result.by_mode_motivation[0].mode == 'Tous modes'
    assert result.by_mode_motivation[0].response_count == 8


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
    
    assert result.total_motivation_responses == 10
    assert result.motivation_aggregation_type == 'all_aggregated'
    assert len(result.by_mode_motivation) == 1
    assert result.by_mode_motivation[0].mode == 'Tous modes'


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
    
    assert result.total_motivation_responses == 23
    assert result.motivation_aggregation_type == 'mixed'
    assert len(result.by_mode_motivation) == 3  # velo, Autres, Total
    
    velo_stats = next(m for m in result.by_mode_motivation if m.mode == 'velo')
    assert velo_stats.response_count == 15
    
    autres_stats = next(m for m in result.by_mode_motivation if m.mode == 'Autres')
    assert autres_stats.response_count == 8
    
    total_stats = next(m for m in result.by_mode_motivation if m.mode == 'Total')
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
    
    assert result.total_motivation_responses == 32
    assert result.motivation_aggregation_type == 'mixed'
    assert len(result.by_mode_motivation) == 4  # velo, train, Autres, Total
    
    velo_stats = next(m for m in result.by_mode_motivation if m.mode == 'velo')
    assert velo_stats.response_count == 15
    
    train_stats = next(m for m in result.by_mode_motivation if m.mode == 'train')
    assert train_stats.response_count == 12
    
    autres_stats = next(m for m in result.by_mode_motivation if m.mode == 'Autres')
    assert autres_stats.response_count == 5


# ===== Tests for independent aggregation =====

def test_independent_aggregation_different_splits():
    """
    Test that levers and motivation can have different mode groupings.
    E.g., velo shows individually for motivation but is aggregated for levers.
    """
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 20, 'train': 20, 'tpu': 10},
        motivations={
            'velo': [5] * 15,  # 15 motivation responses for velo (>= 10, split)
            'train': [4] * 5,  # 5 motivation responses for train (< 10, aggregate)
            'tpu': [3] * 3  # 3 motivation responses for tpu (< 10, aggregate)
        },
        levers={
            'velo': ['finance'] * 8,  # 8 lever responses for velo (< 10, aggregate)
            'train': ['flexibility'] * 12,  # 12 lever responses for train (>= 10, split)
            'tpu': ['environment'] * 4  # 4 lever responses for tpu (< 10, aggregate)
        }
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    # Motivation: velo split individually, train+tpu aggregated into Autres
    assert result.motivation_aggregation_type == 'mixed'
    assert len(result.by_mode_motivation) == 3  # velo, Autres, Total
    motivation_modes = [m.mode for m in result.by_mode_motivation]
    assert 'velo' in motivation_modes
    assert 'Autres' in motivation_modes
    assert 'Total' in motivation_modes
    
    # Levers: train split individually, velo+tpu aggregated into Autres
    assert result.lever_aggregation_type == 'mixed'
    assert len(result.by_mode_levers) == 3  # train, Autres, Total
    lever_modes = [m.mode for m in result.by_mode_levers]
    assert 'train' in lever_modes
    assert 'Autres' in lever_modes
    assert 'Total' in lever_modes


# ===== Tests for percentages and counts =====

def test_lever_percentages_computed_correctly():
    """Test that lever percentages are computed correctly."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        levers={'velo': ['finance']*5 + ['flexibility']*3 + ['environment']*2}
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    mode_stats = result.by_mode_levers[0]
    assert mode_stats.response_count == 10
    
    # Check percentages (based on total lever selections)
    finance = next(l for l in mode_stats.levers if l.category == 'finance')
    assert finance.count == 5
    assert finance.percentage == 50.0
    
    flexibility = next(l for l in mode_stats.levers if l.category == 'flexibility')
    assert flexibility.count == 3
    assert flexibility.percentage == 30.0
    
    environment = next(l for l in mode_stats.levers if l.category == 'environment')
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
    
    mode_stats = result.by_mode_motivation[0]
    assert mode_stats.response_count == 10
    
    # Check percentages
    level_5 = next(m for m in mode_stats.motivation if m.level == 5)
    assert level_5.count == 4
    assert level_5.percentage == 40.0
    
    level_4 = next(m for m in mode_stats.motivation if m.level == 4)
    assert level_4.count == 3
    assert level_4.percentage == 30.0
    
    level_3 = next(m for m in mode_stats.motivation if m.level == 3)
    assert level_3.count == 2
    assert level_3.percentage == 20.0
    
    level_2 = next(m for m in mode_stats.motivation if m.level == 2)
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
    
    mode_stats_motivation = result.by_mode_motivation[0]
    mode_stats_levers = result.by_mode_levers[0]
    
    # All 5 motivation levels should be present
    assert len(mode_stats_motivation.motivation) == 5
    level_1 = next(m for m in mode_stats_motivation.motivation if m.level == 1)
    assert level_1.count == 0
    assert level_1.percentage == 0.0
    
    # All 5 lever categories should be present
    assert len(mode_stats_levers.levers) == 5
    flexibility = next(l for l in mode_stats_levers.levers if l.category == 'flexibility')
    assert flexibility.count == 0
    assert flexibility.percentage == 0.0


def test_empty_data_handling():
    """Test graceful handling of empty data."""
    df = pd.DataFrame({
        'typo.reco.reco_dt2.0': [],
        'data.change.motivation': [],
        'data.change.levers.0': [],
        'data.change.levers.1': [],
        'data.change.levers.2': []
    })
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    assert result.total_lever_responses == 0
    assert result.total_motivation_responses == 0
    assert len(result.by_mode_levers) == 0
    assert len(result.by_mode_motivation) == 0


def test_other_levers_extracted():
    """Test that other_levers text is extracted correctly."""
    data = {
        'typo.reco.reco_dt2.0': ['velo', 'train', 'tpu'],
        'data.change.motivation': [5, 4, 3],
        'data.change.levers.0': ['finance', 'flexibility', 'other'],
        'data.change.levers.1': [None, None, None],
        'data.change.levers.2': [None, None, None],
        'data.change.other_levers': ['More parking', '', 'Better infrastructure']
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
    assert stats.behavior_change.total_lever_responses >= 0
    assert stats.behavior_change.total_motivation_responses >= 0


def test_labels_are_french():
    """Test that all labels are in French."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        motivations={'velo': [5]*10},
        levers={'velo': ['finance']*10}
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    mode_stats_motivation = result.by_mode_motivation[0]
    mode_stats_levers = result.by_mode_levers[0]
    
    # Check motivation labels
    assert mode_stats_motivation.motivation[0].label == 'Très motivé·e'
    assert mode_stats_motivation.motivation[4].label == 'Pas intéressé·e'
    
    # Check lever labels
    finance = next(l for l in mode_stats_levers.levers if l.category == 'finance')
    assert finance.label == 'Aide financière'

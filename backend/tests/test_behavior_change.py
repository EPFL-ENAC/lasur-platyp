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
        motivations: {'velo': [5,5,4,3,2], 'train': [4,4,3]}
        levers: {'velo': ['finance', 'flexibility'], 'train': ['environment']}
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
            
            # Add motivation if provided
            if motivations and mode in motivations and i < len(motivations[mode]):
                row['data.change.motivation'] = motivations[mode][i]
            
            # Add levers if provided
            if levers and mode in levers:
                mode_levers = levers[mode]
                if i < len(mode_levers):
                    # Distribute levers across the 3 columns
                    lever_idx = i % len(mode_levers)
                    col_idx = i % 3
                    row[f'data.change.levers.{col_idx}'] = mode_levers[lever_idx]
            
            rows.append(row)
    
    return pd.DataFrame(rows)


def test_less_than_10_responses_all_aggregated():
    """Test that < 10 responses are aggregated across all modes."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 3, 'train': 2, 'tpu': 3},
        motivations={
            'velo': [5, 4, 3],
            'train': [4, 3],
            'tpu': [5, 4, 2]
        }
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    assert result.total_responses == 8
    assert result.aggregation_type == 'all_aggregated'
    assert len(result.by_mode) == 1
    assert result.by_mode[0].mode == 'Tous modes'
    assert result.by_mode[0].total_responses == 8


def test_10_or_more_no_mode_above_threshold():
    """Test that >= 10 responses but no mode >= 10 are still aggregated."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 4, 'train': 3, 'tpu': 3, 'inter': 2},
        motivations={
            'velo': [5, 4, 3, 2],
            'train': [4, 3, 2],
            'tpu': [5, 4, 3],
            'inter': [3, 2]
        }
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    assert result.total_responses == 12
    assert result.aggregation_type == 'all_aggregated'
    assert len(result.by_mode) == 1
    assert result.by_mode[0].mode == 'Tous modes'


def test_one_mode_above_threshold():
    """Test split when one mode has >= 10 recommendations."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 15, 'train': 5, 'tpu': 3},
        motivations={
            'velo': [5]*8 + [4]*5 + [3]*2,
            'train': [4]*3 + [3]*2,
            'tpu': [5, 4, 3]
        },
        levers={
            'velo': ['finance']*5 + ['flexibility']*5 + ['environment']*3,
            'train': ['finance']*2 + ['collective']*1,
            'tpu': ['environment']*2
        }
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    assert result.total_responses == 23
    assert result.aggregation_type == 'mixed'
    assert len(result.by_mode) == 3  # velo, Autres, Total
    
    # Check velo stats
    velo_stats = next(m for m in result.by_mode if m.mode == 'velo')
    assert velo_stats.total_responses == 15
    assert velo_stats.motivation_responses == 15
    
    # Check Autres stats (train + tpu)
    autres_stats = next(m for m in result.by_mode if m.mode == 'Autres')
    assert autres_stats.total_responses == 8
    
    # Check Total stats
    total_stats = next(m for m in result.by_mode if m.mode == 'Total')
    assert total_stats.total_responses == 23


def test_multiple_modes_above_threshold():
    """Test split when multiple modes have >= 10 recommendations."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 15, 'train': 12, 'tpu': 5},
        motivations={
            'velo': [5]*8 + [4]*5 + [3]*2,
            'train': [5]*6 + [4]*4 + [3]*2,
            'tpu': [4]*3 + [3]*2
        }
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    assert result.total_responses == 32
    assert result.aggregation_type == 'mixed'
    assert len(result.by_mode) == 4  # velo, train, Autres, Total
    
    # Check individual modes
    velo_stats = next(m for m in result.by_mode if m.mode == 'velo')
    assert velo_stats.total_responses == 15
    
    train_stats = next(m for m in result.by_mode if m.mode == 'train')
    assert train_stats.total_responses == 12
    
    autres_stats = next(m for m in result.by_mode if m.mode == 'Autres')
    assert autres_stats.total_responses == 5


def test_lever_percentages_computed_correctly():
    """Test that lever percentages are computed correctly."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        levers={'velo': ['finance']*5 + ['flexibility']*3 + ['environment']*2}
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    mode_stats = result.by_mode[0]
    assert mode_stats.levers_responses == 10
    
    # Check percentages
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
    
    mode_stats = result.by_mode[0]
    assert mode_stats.motivation_responses == 10
    
    # Check percentages (stored with 2 decimals)
    level_5 = next(m for m in mode_stats.motivation if m.level == 5)
    assert level_5.count == 4
    assert level_5.percentage == 40.0
    
    level_4 = next(m for m in mode_stats.motivation if m.level == 4)
    assert level_4.count == 3
    assert level_4.percentage == 30.0


def test_empty_behavior_change_data():
    """Test handling when no behavior change data exists."""
    df = pd.DataFrame({
        'typo.reco.reco_dt2.0': ['velo', 'train', 'tpu'],
        'data.change.motivation': [None, None, None],
        'data.change.levers.0': [None, None, None]
    })
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    assert result.total_responses == 3
    assert result.aggregation_type == 'all_aggregated'
    
    mode_stats = result.by_mode[0]
    assert mode_stats.motivation_responses == 0
    assert mode_stats.levers_responses == 0
    
    # All categories should have 0 count
    for lever in mode_stats.levers:
        assert lever.count == 0
        assert lever.percentage == 0.0
    
    for motivation in mode_stats.motivation:
        assert motivation.count == 0
        assert motivation.percentage == 0.0


def test_other_levers_extraction():
    """Test extraction of free-text other_levers field."""
    df = pd.DataFrame({
        'typo.reco.reco_dt2.0': ['velo', 'train', 'tpu'],
        'data.change.other_levers': [
            'Better bike lanes',
            'More frequent trains',
            None
        ]
    })
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    mode_stats = result.by_mode[0]
    assert len(mode_stats.other_levers) == 2
    assert 'Better bike lanes' in mode_stats.other_levers
    assert 'More frequent trains' in mode_stats.other_levers


def test_zero_count_categories_included():
    """Test that categories with 0 count are still included."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        levers={'velo': ['finance']*10}  # Only finance, all others should be 0
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    mode_stats = result.by_mode[0]
    
    # Should have all 5 categories
    assert len(mode_stats.levers) == 5
    
    # Finance should have 100%
    finance = next(l for l in mode_stats.levers if l.category == 'finance')
    assert finance.count == 10
    assert finance.percentage == 100.0
    
    # All others should be 0
    for category in ['flexibility', 'collective', 'environment', 'other']:
        lever = next(l for l in mode_stats.levers if l.category == category)
        assert lever.count == 0
        assert lever.percentage == 0.0


def test_exactly_10_responses():
    """Test boundary condition with exactly 10 responses."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        motivations={'velo': [5]*5 + [4]*5}
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    # With exactly 10 responses on one mode, it should be split
    assert result.total_responses == 10
    assert result.aggregation_type == 'mixed'
    assert len(result.by_mode) == 2  # velo, Total


def test_labels_are_french():
    """Test that labels are in French as expected."""
    df = create_test_dataframe_with_behavior_change(
        mode_counts={'velo': 10},
        motivations={'velo': [5, 4, 3, 2, 1] + [5]*5},
        levers={'velo': ['finance', 'flexibility', 'collective', 'environment', 'other']*2}
    )
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    mode_stats = result.by_mode[0]
    
    # Check lever labels
    expected_lever_labels = {
        'finance': 'Aide financière',
        'flexibility': 'Flexibilité',
        'collective': 'Changement collectif',
        'environment': 'Aménagement environnement',
        'other': 'Autre'
    }
    for lever in mode_stats.levers:
        assert lever.label == expected_lever_labels[lever.category]
    
    # Check motivation labels
    expected_motivation_labels = {
        1: 'Pas intéressé·e',
        2: 'Plutôt pas',
        3: 'Neutre',
        4: 'Plutôt motivé·e',
        5: 'Très motivé·e'
    }
    for motivation in mode_stats.motivation:
        assert motivation.label == expected_motivation_labels[motivation.level]


def test_with_real_test_data():
    """Test with actual test CSV data."""
    df = load_test_dataframe()
    
    service = BehaviorChangeService(df)
    result = service.compute_behavior_change_stats()
    
    # Basic sanity checks
    assert isinstance(result, BehaviorChangeStats)
    assert result.total_responses >= 0
    assert result.aggregation_type in ['all_aggregated', 'mode_split', 'mixed']
    assert isinstance(result.by_mode, list)
    
    # Check structure of each mode
    for mode_stats in result.by_mode:
        assert isinstance(mode_stats, BehaviorChangeByMode)
        assert isinstance(mode_stats.levers, list)
        assert isinstance(mode_stats.motivation, list)
        assert len(mode_stats.levers) == 5  # All 5 categories
        assert len(mode_stats.motivation) == 5  # All 5 levels
        
        # Check that all lever categories are present
        lever_categories = [l.category for l in mode_stats.levers]
        assert set(lever_categories) == {'finance', 'flexibility', 'collective', 'environment', 'other'}
        
        # Check that all motivation levels are present
        motivation_levels = [m.level for m in mode_stats.motivation]
        assert set(motivation_levels) == {1, 2, 3, 4, 5}


def test_integration_with_stats_service():
    """Test that behavior_change is properly integrated into Stats."""
    df = load_test_dataframe()
    
    stats_service = StatsService()
    stats = stats_service.compute_stats(df)
    
    # Verify behavior_change is in the stats
    assert hasattr(stats, 'behavior_change')
    assert stats.behavior_change is not None
    assert isinstance(stats.behavior_change, BehaviorChangeStats)

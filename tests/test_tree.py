"""
Unit tests for individual tree growth.
"""
import pytest
import math
from pathlib import Path
from src.tree import Tree
from tests.utils import setup_test_output, plot_tree_growth_comparison, generate_test_report, plot_long_term_growth

# Setup output directory
output_dir = setup_test_output()
tree_test_dir = output_dir / 'tree_tests'

@pytest.fixture
def small_tree():
    """Create a small tree for testing."""
    return Tree(dbh=1.0, height=6.0, age=2)

@pytest.fixture
def large_tree():
    """Create a large tree for testing."""
    return Tree(dbh=6.0, height=40.0, age=15)

@pytest.fixture
def transition_tree():
    """Create a tree in the transition zone."""
    return Tree(dbh=2.5, height=20.0, age=8)

def test_small_tree_growth(small_tree):
    """Test small tree growth behavior."""
    # Store initial state
    initial_metrics = [{
        'age': small_tree.age,
        'dbh': small_tree.dbh,
        'height': small_tree.height,
        'crown_ratio': small_tree.crown_ratio
    }]
    
    # Grow for 5 years
    for _ in range(5):
        small_tree.grow(site_index=70, competition_factor=0.0)
        initial_metrics.append({
            'age': small_tree.age,
            'dbh': small_tree.dbh,
            'height': small_tree.height,
            'crown_ratio': small_tree.crown_ratio
        })
    
    # Create visualization and get base64 data
    plot_base64 = plot_tree_growth_comparison(
        [(initial_metrics, 'Small Tree')],
        'Small Tree Growth Test',
        tree_test_dir / 'small_tree_growth.png'
    )
    
    # Generate report with embedded plot
    generate_test_report(
        'Small Tree Growth Test',
        initial_metrics,
        tree_test_dir / 'small_tree_growth',
        plot_base64
    )
    
    # Run assertions
    assert small_tree.height > initial_metrics[0]['height']
    assert small_tree.dbh > initial_metrics[0]['dbh']
    assert 0.2 <= small_tree.crown_ratio <= 0.9
    assert small_tree.age == 7

def test_large_tree_growth(large_tree):
    """Test large tree growth behavior."""
    # Store initial state
    metrics = [{
        'age': large_tree.age,
        'dbh': large_tree.dbh,
        'height': large_tree.height,
        'crown_ratio': large_tree.crown_ratio
    }]
    
    # Grow for 5 years
    for _ in range(5):
        large_tree.grow(site_index=70, competition_factor=0.0)
        metrics.append({
            'age': large_tree.age,
            'dbh': large_tree.dbh,
            'height': large_tree.height,
            'crown_ratio': large_tree.crown_ratio
        })
    
    # Create visualization and get base64 data
    plot_base64 = plot_tree_growth_comparison(
        [(metrics, 'Large Tree')],
        'Large Tree Growth Test',
        tree_test_dir / 'large_tree_growth.png'
    )
    
    # Generate report with embedded plot
    generate_test_report(
        'Large Tree Growth Test',
        metrics,
        tree_test_dir / 'large_tree_growth',
        plot_base64
    )
    
    # Run assertions
    assert large_tree.dbh > metrics[0]['dbh']
    assert large_tree.height > metrics[0]['height']
    assert 0.2 <= large_tree.crown_ratio <= 0.9
    assert large_tree.age == 20

def test_transition_zone_growth(transition_tree):
    """Test growth behavior in transition zone."""
    initial_dbh = transition_tree.dbh
    initial_height = transition_tree.height
    
    # Grow tree for one year
    transition_tree.grow(site_index=70, competition_factor=0.0)
    
    # Both diameter and height should increase
    assert transition_tree.dbh > initial_dbh
    assert transition_tree.height > initial_height
    # Growth should be between small and large tree models
    assert 0.2 <= transition_tree.crown_ratio <= 0.9
    # Age should increment
    assert transition_tree.age == 9

def test_competition_effects(large_tree):
    """Test the effects of competition on growth."""
    # Create trees for different competition levels
    trees = {
        'No Competition': Tree(dbh=large_tree.dbh, height=large_tree.height, age=large_tree.age),
        'Medium Competition': Tree(dbh=large_tree.dbh, height=large_tree.height, age=large_tree.age),
        'High Competition': Tree(dbh=large_tree.dbh, height=large_tree.height, age=large_tree.age)
    }
    competition_levels = {'No Competition': 0.0, 'Medium Competition': 0.3, 'High Competition': 0.6}
    
    # Collect metrics for each competition level over 5 years
    metrics_by_competition = {}
    for label, tree in trees.items():
        metrics = [{
            'age': tree.age,
            'dbh': tree.dbh,
            'height': tree.height,
            'crown_ratio': tree.crown_ratio
        }]
        for _ in range(5):
            tree.grow(site_index=70, competition_factor=competition_levels[label])
            metrics.append({
                'age': tree.age,
                'dbh': tree.dbh,
                'height': tree.height,
                'crown_ratio': tree.crown_ratio
            })
        metrics_by_competition[label] = metrics
    
    # Create visualization and get base64 data
    plot_base64 = plot_tree_growth_comparison(
        [(metrics, label) for label, metrics in metrics_by_competition.items()],
        'Competition Effects Test',
        tree_test_dir / 'competition_effects.png'
    )
    
    # Generate report with embedded plot
    results = []
    for label, metrics in metrics_by_competition.items():
        final_metrics = metrics[-1]
        results.append({
            'competition_level': label,
            'dbh': final_metrics['dbh'],
            'height': final_metrics['height'],
            'crown_ratio': final_metrics['crown_ratio']
        })
    
    generate_test_report(
        'Competition Effects Test',
        results,
        tree_test_dir / 'competition_effects',
        plot_base64
    )
    
    # Run assertions
    final_metrics = {label: metrics[-1] for label, metrics in metrics_by_competition.items()}
    assert final_metrics['High Competition']['dbh'] < final_metrics['Medium Competition']['dbh'] < final_metrics['No Competition']['dbh']
    assert final_metrics['High Competition']['height'] < final_metrics['Medium Competition']['height'] < final_metrics['No Competition']['height']
    assert final_metrics['High Competition']['crown_ratio'] < final_metrics['Medium Competition']['crown_ratio'] < final_metrics['No Competition']['crown_ratio']

def test_volume_calculation(large_tree):
    """Test tree volume calculation."""
    volume = large_tree.get_volume()
    
    # Volume should be positive
    assert volume > 0
    
    # Basic volume check (cylinder * form factor)
    basal_area = math.pi * (large_tree.dbh / 24)**2
    cylinder_volume = basal_area * large_tree.height
    assert volume < cylinder_volume  # Volume should be less than cylinder

def test_long_term_growth():
    """Test tree development over multiple years."""
    tree = Tree(dbh=0.5, height=1.0, age=0)
    growth_metrics = []
    
    # Grow for 60 years
    for _ in range(60):
        growth_metrics.append({
            'age': tree.age,
            'dbh': tree.dbh,
            'height': tree.height,
            'crown_ratio': tree.crown_ratio,
            'volume': tree.get_volume()
        })
        tree.grow(site_index=70, competition_factor=0.0)
    
    # Add final state
    growth_metrics.append({
        'age': tree.age,
        'dbh': tree.dbh,
        'height': tree.height,
        'crown_ratio': tree.crown_ratio,
        'volume': tree.get_volume()
    })
    
    # Create visualization
    plot_base64 = plot_long_term_growth(
        growth_metrics,
        'Long-term Tree Development (60 years)',
        tree_test_dir / 'long_term_growth.png'
    )
    
    # Generate report
    generate_test_report(
        'Long-term Tree Growth Test',
        growth_metrics,
        tree_test_dir / 'long_term_growth',
        plot_base64
    )
    
    # Run assertions
    assert tree.age == 60
    assert tree.dbh > 8.0  # Should reach merchantable size
    assert tree.height > 60.0  # Should reach typical mature height
    assert tree.get_volume() > 0
    
    # Growth pattern assertions
    dbh_growth = [metrics['dbh'] for metrics in growth_metrics]
    height_growth = [metrics['height'] for metrics in growth_metrics]
    volume_growth = [metrics['volume'] for metrics in growth_metrics]
    
    # Height growth should follow sigmoid pattern (faster early, slower late)
    early_height_growth = height_growth[10] - height_growth[0]
    late_height_growth = height_growth[-1] - height_growth[-11]
    assert early_height_growth > late_height_growth
    
    # DBH growth should show gradual decline
    early_dbh_growth = dbh_growth[10] - dbh_growth[0]
    late_dbh_growth = dbh_growth[-1] - dbh_growth[-11]
    assert 0.25 < late_dbh_growth / early_dbh_growth < 1.5  # Later growth at least 25% of early growth
    
    # Volume growth should accelerate then level off
    mid_point = len(volume_growth) // 2
    early_volume_growth = volume_growth[mid_point] - volume_growth[0]
    late_volume_growth = volume_growth[-1] - volume_growth[mid_point]
    assert early_volume_growth < late_volume_growth  # Accelerating early
    
    # Crown ratio should decrease with age
    crown_ratios = [metrics['crown_ratio'] for metrics in growth_metrics]
    assert crown_ratios[-1] < crown_ratios[0]  # Should decrease over time 
"""Unit tests for TreeGrowthSimulator class."""

import pytest
import math
from fvs_python.modeling.growth.tree_growth_simulator import TreeGrowthSimulator
from tests.modeling.growth.test_utils import TestTree, TEST_COEFFICIENTS, SAMPLE_STAND_CONDITIONS

def test_initialization():
    """Test TreeGrowthSimulator initialization."""
    # Test valid initialization
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    assert simulator.species == 'LP'
    assert simulator.site_index == 70.0
    
    # Test invalid species code
    with pytest.raises(ValueError):
        TreeGrowthSimulator('XX', 70.0, TEST_COEFFICIENTS)

def test_stand_conditions_validation():
    """Test validation of stand conditions."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    
    # Test with missing required keys
    invalid_conditions = {
        'basal_area': 100.0,
        'relative_height': 0.8
    }
    
    with pytest.raises(ValueError) as exc_info:
        simulator._validate_stand_conditions(invalid_conditions)
    assert 'Missing required stand conditions' in str(exc_info.value)
    
    # Test with all required keys
    simulator._validate_stand_conditions(SAMPLE_STAND_CONDITIONS)

def test_small_tree_growth():
    """Test growth calculations for small trees (DBH < 2.0)."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    tree = TestTree(
        species='LP',
        dbh=1.5,
        height=8.0,
        crown_ratio=0.6
    )
    
    growth = simulator.simulate_growth(tree, SAMPLE_STAND_CONDITIONS)
    
    # Verify growth components are present and reasonable
    assert 'height_growth' in growth
    assert 'dbh_growth' in growth
    assert 'crown_ratio_change' in growth
    
    # Basic sanity checks
    assert growth['height_growth'] > 0
    assert growth['dbh_growth'] > 0
    assert -0.1 <= growth['crown_ratio_change'] <= 0.1

def test_large_tree_growth():
    """Test growth calculations for large trees (DBH >= 3.0)."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    tree = TestTree(
        species='LP',
        dbh=5.0,
        height=25.0,
        crown_ratio=0.5
    )
    
    growth = simulator.simulate_growth(tree, SAMPLE_STAND_CONDITIONS)
    
    # Verify growth components
    assert 'height_growth' in growth
    assert 'dbh_growth' in growth
    assert 'crown_ratio_change' in growth
    
    # Basic sanity checks
    assert growth['height_growth'] > 0
    assert growth['dbh_growth'] > 0
    assert -0.1 <= growth['crown_ratio_change'] <= 0.1

def test_transition_growth():
    """Test growth calculations for transition zone trees (2.0 <= DBH <= 3.0)."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    tree = TestTree(
        species='LP',
        dbh=2.5,
        height=15.0,
        crown_ratio=0.55
    )
    
    growth = simulator.simulate_growth(tree, SAMPLE_STAND_CONDITIONS)
    
    # Verify growth components
    assert 'height_growth' in growth
    assert 'dbh_growth' in growth
    assert 'crown_ratio_change' in growth
    
    # Basic sanity checks
    assert growth['height_growth'] > 0
    assert growth['dbh_growth'] > 0
    assert -0.1 <= growth['crown_ratio_change'] <= 0.1
    
    # Test that growth is between small and large tree predictions
    small_tree = TestTree('LP', 1.5, 8.0, 0.6)
    large_tree = TestTree('LP', 3.5, 20.0, 0.5)
    
    small_growth = simulator.simulate_growth(small_tree, SAMPLE_STAND_CONDITIONS)
    large_growth = simulator.simulate_growth(large_tree, SAMPLE_STAND_CONDITIONS)
    
    # Growth should be intermediate
    assert small_growth['height_growth'] <= growth['height_growth'] <= large_growth['height_growth'] or \
           large_growth['height_growth'] <= growth['height_growth'] <= small_growth['height_growth']

def test_competition_modifier():
    """Test competition modifier calculations."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    tree = TestTree('LP', 3.0, 15.0, 0.5)
    
    # Test with different competition levels
    low_competition = {**SAMPLE_STAND_CONDITIONS, 'crown_competition_factor': 50.0}
    high_competition = {**SAMPLE_STAND_CONDITIONS, 'crown_competition_factor': 250.0}
    
    low_mod = simulator._competition_modifier(tree, low_competition)
    high_mod = simulator._competition_modifier(tree, high_competition)
    
    # Higher competition should result in lower modifier
    assert low_mod > high_mod
    # Modifiers should be bounded
    assert 0.05 <= low_mod <= 1.0
    assert 0.05 <= high_mod <= 1.0

def test_crown_ratio_bounds():
    """Test that crown ratio changes stay within bounds."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    
    # Test near lower bound
    low_cr_tree = TestTree('LP', 3.0, 15.0, 0.21)
    low_cr_growth = simulator.simulate_growth(low_cr_tree, SAMPLE_STAND_CONDITIONS)
    assert low_cr_tree.crown_ratio + low_cr_growth['crown_ratio_change'] >= 0.2
    
    # Test near upper bound
    high_cr_tree = TestTree('LP', 3.0, 15.0, 0.89)
    high_cr_growth = simulator.simulate_growth(high_cr_tree, SAMPLE_STAND_CONDITIONS)
    assert high_cr_tree.crown_ratio + high_cr_growth['crown_ratio_change'] <= 0.9 
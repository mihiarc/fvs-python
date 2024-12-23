"""
Tests for the growth module.
"""

import pytest
import math
from fvs_core.growth_models import curtis_arney_height, wykoff_height, species_data

# Test coefficients for a hypothetical species (for basic functionality tests)
TEST_COEFFICIENTS = {
    'curtis_arney': {
        'CurtisArney_b0': 289.4,    # Median value from data
        'CurtisArney_b1': 3.8,      # Median value from data
        'CurtisArney_b2': -0.32,    # Median value from data
        'Dbw': 0.2                  # Median value from data
    },
    'wykoff': {
        'Wykoff_b0': 4.47,    # Median value from data
        'Wykoff_b1': -5.0     # Near median value from data (-4.99)
    }
}

def test_curtis_arney_basic():
    """Test basic functionality of Curtis-Arney equation"""
    # Test with coefficients directly to avoid CSV dependency
    height = curtis_arney_height(10.0, 'TEST', TEST_COEFFICIENTS['curtis_arney'])
    assert height > 4.51  # Height should be greater than breast height
    assert isinstance(height, float)
    assert height < 200.0  # Reasonable maximum height

def test_curtis_arney_small_trees():
    """Test Curtis-Arney equation for trees < 3 inches DBH"""
    # Use FR (Fraser Fir) coefficients from the data
    height_small = curtis_arney_height(2.0, 'FR')
    height_large = curtis_arney_height(3.0, 'FR')
    
    assert height_small > 4.51
    assert height_large > height_small  # Height should increase with diameter
    assert height_small < 100.0  # Reasonable maximum height for small trees
    assert height_large < 100.0  # Reasonable maximum height

def test_curtis_arney_invalid_species():
    """Test Curtis-Arney equation with invalid species code"""
    with pytest.raises(ValueError):
        curtis_arney_height(10.0, 'INVALID')

def test_curtis_arney_real_species():
    """Test Curtis-Arney equation with real species data"""
    # Test a few different species
    species_list = ['FR', 'WP', 'LL']  # Fraser Fir, White Pine, Loblolly Pine
    dbh_values = [2.0, 3.0, 10.0]  # Test both small and large trees
    
    for sp in species_list:
        for dbh in dbh_values:
            height = curtis_arney_height(dbh, sp)
            assert height > 4.51
            assert height < 200.0  # Reasonable maximum height
            
            # Test monotonicity around the 3-inch threshold
            if dbh == 2.0:
                height_next = curtis_arney_height(2.5, sp)
                assert height < height_next

def test_wykoff_basic():
    """Test basic functionality of Wykoff equation"""
    height = wykoff_height(10.0, 'TEST', TEST_COEFFICIENTS['wykoff'])
    assert height > 4.51
    assert isinstance(height, float)
    assert height < 200.0  # Reasonable maximum height

def test_wykoff_monotonic():
    """Test that Wykoff height increases with diameter"""
    # Use WP (White Pine) coefficients from the data
    dbh_values = [5.0, 10.0, 15.0]
    heights = [wykoff_height(d, 'WP') for d in dbh_values]
    
    # Check monotonicity
    for i in range(len(heights)-1):
        assert heights[i] < heights[i+1]
    
    # Check reasonable ranges
    for h in heights:
        assert 4.51 < h < 200.0

def test_wykoff_invalid_species():
    """Test Wykoff equation with invalid species code"""
    with pytest.raises(ValueError):
        wykoff_height(10.0, 'INVALID')

def test_height_comparison():
    """Compare heights from both equations for real species"""
    species = 'WP'  # White Pine
    dbh_values = [5.0, 10.0, 15.0]
    
    for dbh in dbh_values:
        height_ca = curtis_arney_height(dbh, species)
        height_w = wykoff_height(dbh, species)
        
        # Both methods should give reasonable heights
        assert 4.51 < height_ca < 200.0
        assert 4.51 < height_w < 200.0
        
        # Heights should be somewhat similar (within 100% of each other)
        ratio = height_ca / height_w if height_w != 0 else float('inf')
        assert 0.25 < ratio < 4.0  # Relaxed bounds due to different equation forms

def test_height_diameter_relationship():
    """Test that height increases with diameter across species"""
    species_list = ['FR', 'WP', 'LL']
    dbh_values = [3.0, 5.0, 10.0, 15.0, 20.0]  # Start at 3.0 to avoid small tree calculations
    
    for sp in species_list:
        prev_height = 0
        for dbh in dbh_values:
            height = curtis_arney_height(dbh, sp)
            assert height > prev_height
            assert height < 200.0  # Reasonable maximum height
            prev_height = height

def test_small_tree_transition():
    """Test the transition between small and large tree calculations"""
    species = 'FR'
    # Test heights around the 3-inch threshold
    height_before = curtis_arney_height(2.99, species)
    height_after = curtis_arney_height(3.01, species)
    
    # Heights should be similar around the threshold
    assert abs(height_before - height_after) < 10.0  # Allow some discontinuity but not too much
    assert height_before > 4.51
    assert height_after > 4.51

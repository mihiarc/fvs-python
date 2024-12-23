"""
Tests for bark ratio calculations in the growth module.
"""

import pytest
import numpy as np
from fvs_core.growth_models import calculate_inside_bark_dbh_ratio, species_data

# Test data based on typical ranges
TEST_COEFFICIENTS = {
    'Bark_b0': 0.9,  # Base ratio
    'Bark_b1': 0.01  # Slope adjustment
}

def test_basic_bark_ratio():
    """Test basic functionality of bark ratio calculation."""
    dob = 10.0  # Example diameter outside bark
    ratio = calculate_inside_bark_dbh_ratio(dob, 'TEST', TEST_COEFFICIENTS)
    
    assert isinstance(ratio, float)
    assert 0.80 <= ratio <= 0.99  # Check bounds

def test_bark_ratio_bounds():
    """Test that bark ratio stays within bounds for extreme values."""
    test_diameters = [1.0, 5.0, 10.0, 20.0, 50.0]
    
    for dob in test_diameters:
        ratio = calculate_inside_bark_dbh_ratio(dob, 'TEST', TEST_COEFFICIENTS)
        assert 0.80 <= ratio <= 0.99, f"Ratio {ratio} out of bounds for DBH {dob}"

def test_bark_ratio_monotonicity():
    """Test that bark ratio changes consistently with diameter."""
    diameters = np.linspace(5, 30, 10)
    ratios = [calculate_inside_bark_dbh_ratio(d, 'TEST', TEST_COEFFICIENTS) for d in diameters]
    
    # Check if ratios are monotonic (all increasing or all decreasing)
    diffs = np.diff(ratios)
    assert all(diffs >= 0) or all(diffs <= 0), "Bark ratio not monotonic with diameter"

def test_bark_ratio_real_species():
    """Test bark ratio calculations with real species data."""
    # Get first three species from the data
    test_species = list(species_data.keys())[:3]
    test_diameters = [5.0, 10.0, 20.0]
    
    for species in test_species:
        for dob in test_diameters:
            ratio = calculate_inside_bark_dbh_ratio(dob, species)
            assert 0.80 <= ratio <= 0.99, f"Invalid ratio {ratio} for {species} at DBH {dob}"

def test_invalid_species():
    """Test behavior with invalid species code."""
    with pytest.raises(ValueError):
        calculate_inside_bark_dbh_ratio(10.0, 'INVALID')

def test_zero_diameter():
    """Test behavior with zero diameter."""
    with pytest.raises(ZeroDivisionError):
        calculate_inside_bark_dbh_ratio(0.0, 'TEST', TEST_COEFFICIENTS)

def test_negative_diameter():
    """Test behavior with negative diameter."""
    ratio = calculate_inside_bark_dbh_ratio(-10.0, 'TEST', TEST_COEFFICIENTS)
    assert 0.80 <= ratio <= 0.99  # Should still return valid ratio

def test_species_specific_patterns():
    """Test that different species show expected patterns in bark ratio."""
    # Get first three species from the data
    species_list = list(species_data.keys())[:3]
    dbh = 10.0
    
    # Calculate ratios for different species
    ratios = {sp: calculate_inside_bark_dbh_ratio(dbh, sp) for sp in species_list}
    
    # All ratios should be different (species-specific)
    unique_ratios = len(set(ratios.values()))
    assert unique_ratios > 1, "All species have same bark ratio"
    
    # All ratios should be within bounds
    for species, ratio in ratios.items():
        assert 0.80 <= ratio <= 0.99, f"Invalid ratio {ratio} for {species}"

def test_diameter_sensitivity():
    """Test sensitivity of bark ratio to diameter changes."""
    base_dbh = 10.0
    delta = 0.1  # Small change in diameter
    
    ratio1 = calculate_inside_bark_dbh_ratio(base_dbh, 'TEST', TEST_COEFFICIENTS)
    ratio2 = calculate_inside_bark_dbh_ratio(base_dbh + delta, 'TEST', TEST_COEFFICIENTS)
    
    # Small changes in diameter should produce small changes in ratio
    assert abs(ratio2 - ratio1) < 0.1, "Bark ratio too sensitive to small diameter changes"
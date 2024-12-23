"""
Tests for crown ratio calculations.
"""

import pytest
import numpy as np
from fvs_core.crown_ratio import (
    calculate_dubbed_crown_ratio,
    calculate_acr,
    calculate_crown_ratio_weibull,
    calculate_weibull_parameters,
    calculate_scale,
    calculate_crown_ratio_change
)

# Test data based on real coefficients from species_crown_ratio.csv
TEST_SPECIES = 'FR'  # Fraser Fir
TEST_COEFFICIENTS = {
    'a': 406.59,  # Actual value * 100
    'b0': -687.08,  # Actual value * 100
    'b1': 105.10,  # Actual value * 100
    'c': 4.1741
}

def test_dubbed_crown_ratio():
    """Test dubbed crown ratio calculation for dead trees."""
    # Test small DBH (< 24 inches)
    np.random.seed(42)  # For reproducibility
    cr_small = calculate_dubbed_crown_ratio(12.0, 0.1)
    assert 0.05 <= cr_small <= 0.95
    
    # Test large DBH (>= 24 inches)
    cr_large = calculate_dubbed_crown_ratio(30.0, 0.1)
    assert 0.05 <= cr_large <= 0.95
    
    # Test boundary case
    cr_boundary = calculate_dubbed_crown_ratio(24.0, 0.1)
    assert 0.05 <= cr_boundary <= 0.95

def test_acr_calculation():
    """Test average crown ratio calculation."""
    # Test each ACR equation type
    relsdi = 50.0  # Example relative SDI value
    
    # Test equation 1
    acr1 = calculate_acr(relsdi, TEST_SPECIES)
    assert acr1 is not None
    assert 0.0 < acr1 < 1.0
    
    # Test invalid species
    acr_invalid = calculate_acr(relsdi, 'INVALID')
    assert acr_invalid is None

def test_weibull_parameters():
    """Test Weibull parameter calculations."""
    acr = 0.5  # Example ACR value
    a0, b0, b1, c0 = TEST_COEFFICIENTS.values()
    
    a, b, c = calculate_weibull_parameters(acr, a0, b0, b1, c0)
    
    # Check parameter bounds
    assert b >= 0.03  # b should be bounded by 0.03 after scaling
    assert c >= 2.0  # c should be bounded by 2.0
    assert isinstance(a, float)
    assert isinstance(b, float)
    assert isinstance(c, float)
    
    # Check scaling
    assert a == pytest.approx(a0 / 100.0)  # Should be scaled by 100
    assert b >= (b0 + b1 * acr) / 100.0  # Should be scaled by 100 and bounded

def test_crown_ratio_weibull():
    """Test crown ratio calculation using Weibull distribution."""
    x = 0.5  # Example crown ratio value
    scale = 0.8  # Example scale factor
    a0, b0, b1, c0 = TEST_COEFFICIENTS.values()
    
    # Calculate parameters
    a, b, c = calculate_weibull_parameters(0.5, a0, b0, b1, c0)
    
    # Test crown ratio calculation
    cr = calculate_crown_ratio_weibull(x, a, b, c, scale)
    
    # Check bounds
    assert 0.05 <= cr <= 0.95
    assert isinstance(cr, float)

def test_scale_factor():
    """Test density-dependent scale factor calculation."""
    # Test various CCF values
    ccf_values = [50, 100, 150, 200]
    
    for ccf in ccf_values:
        scale = calculate_scale(ccf)
        assert 0.3 <= scale <= 1.0
        
    # Test boundary cases
    assert calculate_scale(0) == pytest.approx(1.0)
    assert calculate_scale(1000) == pytest.approx(0.3)

def test_crown_ratio_change():
    """Test crown ratio change calculation."""
    current_cr = 0.5
    new_cr = 0.6
    
    change = calculate_crown_ratio_change(current_cr, new_cr)
    assert change == pytest.approx(0.1)
    assert isinstance(change, float)

def test_crown_ratio_bounds():
    """Test that crown ratios stay within bounds."""
    x_values = [-0.1, 0.0, 0.5, 1.0, 1.1]
    scale = 0.8
    a0, b0, b1, c0 = TEST_COEFFICIENTS.values()
    a, b, c = calculate_weibull_parameters(0.5, a0, b0, b1, c0)
    
    for x in x_values:
        cr = calculate_crown_ratio_weibull(x, a, b, c, scale)
        assert 0.05 <= cr <= 0.95

def test_acr_equation_types():
    """Test different ACR equation types."""
    relsdi = 50.0
    
    # Test with species using different equation types
    species_list = ['FR', 'JU', 'PI']  # Species with different equation types
    
    for species in species_list:
        acr = calculate_acr(relsdi, species)
        assert acr is not None
        assert isinstance(acr, float)
        assert 0.0 < acr < 1.0

def test_crown_ratio_sensitivity():
    """Test sensitivity of crown ratio to input parameters."""
    x = 0.5
    scale = 0.8
    a0, b0, b1, c0 = TEST_COEFFICIENTS.values()
    
    # Base calculation
    a, b, c = calculate_weibull_parameters(0.5, a0, b0, b1, c0)
    base_cr = calculate_crown_ratio_weibull(x, a, b, c, scale)
    
    # Test sensitivity to scale
    cr_scale_up = calculate_crown_ratio_weibull(x, a, b, c, scale * 1.1)
    assert abs(cr_scale_up - base_cr) < 0.2  # Change should be moderate
    
    # Test sensitivity to x
    cr_x_up = calculate_crown_ratio_weibull(x * 1.1, a, b, c, scale)
    assert abs(cr_x_up - base_cr) < 0.2  # Change should be moderate 
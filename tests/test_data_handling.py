import pytest
from fvs_core.data_handling import calculate_site_index, species_data

def test_calculate_site_index_valid():
    # Test case 1: Valid site species and target species in group 4 (WP group)
    sisp = calculate_site_index("WP", 80, "LL")
    assert sisp is not None  # Check that a value is returned
    
    # Test case 2: Another valid combination in group 1 (SP group)
    sisp = calculate_site_index("SP", 60, "HM")
    assert sisp is not None

def test_calculate_site_index_invalid_site_species():
    # Test case: Invalid species (should default to WO)
    sisp = calculate_site_index("XXX", 80, "RM")  # WO and RM are in group 9
    assert sisp is not None  # Should still return a value because it defaults to WO

def test_calculate_site_index_invalid_target_species():
    # Test case: Invalid target species (should return None)
    sisp = calculate_site_index("WP", 80, "XXX")
    assert sisp is None

def test_calculate_site_index_boundary_conditions():
    # Test cases for min/max SI values for WP and LL (both in group 4)
    wp_min = species_data["WP"]["si_min"]
    wp_max = species_data["WP"]["si_max"]
    ll_min = species_data["LL"]["si_min"]
    ll_max = species_data["LL"]["si_max"]
    
    # Use values well within the valid range to test the transformation
    wp_test = (wp_min + wp_max) / 2  # Use the midpoint
    sisp_test = calculate_site_index("WP", wp_test, "LL")
    
    assert sisp_test is not None
    # The transformed site index should be within the target species' valid range
    assert ll_min <= sisp_test <= ll_max

def test_calculate_site_index_different_groups():
    # Test cases for different site index groups
    sisp_group_1 = calculate_site_index("SP", 70, "HM")  # Group 1
    sisp_group_9 = calculate_site_index("WO", 70, "RM")  # Group 9
    
    assert sisp_group_1 is not None
    assert sisp_group_9 is not None
    
    # Check if results are within valid ranges
    assert species_data["HM"]["si_min"] <= sisp_group_1 <= species_data["HM"]["si_max"]
    assert species_data["RM"]["si_min"] <= sisp_group_9 <= species_data["RM"]["si_max"]
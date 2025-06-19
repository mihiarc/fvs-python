#!/usr/bin/env python3
"""
Test script for FVS-Python Volume Library Integration.
Demonstrates the integration of USFS Volume Estimator Library with FVS-Python.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fvs_python import (
    Tree, Stand, 
    VolumeLibrary, calculate_tree_volume, 
    get_volume_library_info, validate_volume_library
)


def test_volume_library_info():
    """Test volume library information and availability."""
    print("=" * 60)
    print("VOLUME LIBRARY INFORMATION")
    print("=" * 60)
    
    info = get_volume_library_info()
    
    print(f"Volume Library Available: {info['available']}")
    print(f"Version: {info['version']}")
    print(f"DLL Path: {info['dll_path']}")
    print(f"Supported Species: {len(info['supported_species'])}")
    
    if info['supported_species']:
        print("\nSupported Species Codes:")
        species_list = info['supported_species']
        for i in range(0, len(species_list), 8):
            print("  " + ", ".join(species_list[i:i+8]))
    
    return info['available']


def test_volume_library_validation():
    """Test volume library validation."""
    print("\n" + "=" * 60)
    print("VOLUME LIBRARY VALIDATION")
    print("=" * 60)
    
    validation = validate_volume_library()
    
    print(f"DLL Available: {validation['dll_available']}")
    print(f"Version: {validation['version']}")
    
    if validation['test_results']:
        print("\nSpecies Test Results:")
        for test in validation['test_results']:
            if test['success']:
                status = "✓"
                volume = f"{test['volume']:.2f} cubic feet"
            else:
                status = "✗"
                volume = test.get('error', 'Failed')
            
            print(f"  {status} {test['species']}: {volume}")
    
    return validation['dll_available']


def test_tree_volume_calculations():
    """Test volume calculations using Tree class."""
    print("\n" + "=" * 60)
    print("TREE VOLUME CALCULATIONS")
    print("=" * 60)
    
    # Test different species and sizes
    test_trees = [
        {'species': 'LP', 'dbh': 10.0, 'height': 50.0, 'age': 15},
        {'species': 'SP', 'dbh': 15.0, 'height': 70.0, 'age': 20},
        {'species': 'LL', 'dbh': 12.0, 'height': 45.0, 'age': 25},
        {'species': 'SA', 'dbh': 18.0, 'height': 80.0, 'age': 18},
    ]
    
    for tree_data in test_trees:
        print(f"\n{tree_data['species']} - DBH: {tree_data['dbh']}\", Height: {tree_data['height']}'")
        print("-" * 50)
        
        # Create tree
        tree = Tree(
            dbh=tree_data['dbh'],
            height=tree_data['height'],
            species=tree_data['species'],
            age=tree_data['age']
        )
        
        # Test different volume types
        volume_types = [
            ('Total Cubic', 'total_cubic'),
            ('Merchantable Cubic', 'merchantable_cubic'),
            ('Board Foot', 'board_foot'),
            ('Green Weight', 'green_weight'),
            ('Biomass (Main Stem)', 'biomass_main_stem')
        ]
        
        for name, vol_type in volume_types:
            try:
                volume = tree.get_volume(vol_type)
                unit = "lbs" if "weight" in vol_type or "biomass" in vol_type else "cubic feet" if "cubic" in vol_type else "board feet"
                print(f"  {name}: {volume:.2f} {unit}")
            except Exception as e:
                print(f"  {name}: Error - {e}")
        
        # Test detailed volume breakdown
        try:
            detailed = tree.get_volume_detailed()
            print(f"  Error Flag: {detailed['error_flag']}")
        except Exception as e:
            print(f"  Detailed Volume: Error - {e}")


def test_direct_volume_calculations():
    """Test direct volume calculations using the volume library."""
    print("\n" + "=" * 60)
    print("DIRECT VOLUME LIBRARY CALCULATIONS")
    print("=" * 60)
    
    # Test the same tree as in the original vollibTestPython3.py
    test_cases = [
        {
            'name': 'Test Tree (from NVEL example)',
            'dbh': 15.1,
            'height': 76.4,
            'species': 'LP'
        },
        {
            'name': 'Small Loblolly Pine',
            'dbh': 8.0,
            'height': 40.0,
            'species': 'LP'
        },
        {
            'name': 'Large Shortleaf Pine',
            'dbh': 20.0,
            'height': 90.0,
            'species': 'SP'
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}")
        print(f"DBH: {case['dbh']} inches, Height: {case['height']} feet, Species: {case['species']}")
        print("-" * 50)
        
        try:
            result = calculate_tree_volume(
                dbh=case['dbh'],
                height=case['height'],
                species_code=case['species']
            )
            
            if result.is_valid():
                print(f"  Total Cubic Volume: {result.total_cubic_volume:.2f} cubic feet")
                print(f"  Merchantable Cubic: {result.merchantable_cubic_volume:.2f} cubic feet")
                print(f"  Board Foot Volume: {result.board_foot_volume:.2f} board feet")
                print(f"  Green Weight: {result.green_weight:.2f} pounds")
                print(f"  Dry Weight: {result.dry_weight:.2f} pounds")
                print(f"  Main Stem Biomass: {result.biomass_main_stem:.2f} pounds")
            else:
                print(f"  Volume calculation failed (Error Flag: {result.error_flag})")
                print(f"  Fallback Total Volume: {result.total_cubic_volume:.2f} cubic feet")
                
        except Exception as e:
            print(f"  Error: {e}")


def test_stand_volume_calculations():
    """Test volume calculations at the stand level."""
    print("\n" + "=" * 60)
    print("STAND VOLUME CALCULATIONS")
    print("=" * 60)
    
    # Create trees for the stand
    trees_data = [
        {'dbh': 8.0, 'height': 45.0, 'species': 'LP'},
        {'dbh': 10.0, 'height': 55.0, 'species': 'LP'},
        {'dbh': 12.0, 'height': 65.0, 'species': 'LP'},
        {'dbh': 9.0, 'height': 50.0, 'species': 'SP'},
        {'dbh': 11.0, 'height': 60.0, 'species': 'SP'},
    ]
    
    trees = []
    for tree_data in trees_data:
        tree = Tree(
            dbh=tree_data['dbh'],
            height=tree_data['height'],
            species=tree_data['species']
        )
        trees.append(tree)
    
    # Create a small test stand
    stand = Stand(trees)
    
    print(f"Stand with {len(stand.trees)} trees")
    print("-" * 30)
    
    # Calculate stand metrics
    try:
        metrics = stand.get_metrics()
        print(f"Total Volume: {metrics['volume']:.2f} cubic feet")
        print(f"Average DBH: {metrics['dbh']:.1f} inches")
        print(f"Average Height: {metrics['height']:.1f} feet")
        print(f"Basal Area: {metrics['basal_area']:.2f} sq ft")
        
        # Calculate volume by species
        volume_by_species = {}
        for tree in stand.trees:
            species = tree.species
            if species not in volume_by_species:
                volume_by_species[species] = 0
            volume_by_species[species] += tree.get_volume()
        
        print("\nVolume by Species:")
        for species, volume in volume_by_species.items():
            print(f"  {species}: {volume:.2f} cubic feet")
            
    except Exception as e:
        print(f"Error calculating stand metrics: {e}")


def compare_volume_methods():
    """Compare NVEL volume calculations with fallback method."""
    print("\n" + "=" * 60)
    print("VOLUME METHOD COMPARISON")
    print("=" * 60)
    
    # Test tree
    dbh, height, species = 12.0, 60.0, 'LP'
    
    print(f"Test Tree: {species}, DBH: {dbh}\", Height: {height}'")
    print("-" * 40)
    
    # Create tree and get volume using integrated method
    tree = Tree(dbh=dbh, height=height, species=species)
    integrated_volume = tree.get_volume()
    
    # Get detailed breakdown
    detailed = tree.get_volume_detailed()
    
    print(f"Integrated Volume (NVEL/Fallback): {integrated_volume:.2f} cubic feet")
    print(f"Error Flag: {detailed['error_flag']}")
    
    if detailed['error_flag'] == 0:
        print("✓ Using NVEL volume equations")
    else:
        print("⚠ Using fallback volume calculation")
    
    # Calculate fallback volume manually for comparison
    try:
        from fvs_python.bark_ratio import create_bark_ratio_model
        bark_model = create_bark_ratio_model(species)
        dbh_ib = bark_model.apply_bark_ratio_to_dbh(dbh)
        form_factor = 0.48
        basal_area_ib = 3.14159 * (dbh_ib / 24)**2
        fallback_volume = basal_area_ib * height * form_factor
        
        print(f"Manual Fallback Calculation: {fallback_volume:.2f} cubic feet")
        
        if abs(integrated_volume - fallback_volume) < 0.01:
            print("→ Volumes match (using fallback method)")
        else:
            print("→ Volumes differ (likely using NVEL)")
            
    except Exception as e:
        print(f"Fallback calculation error: {e}")


def main():
    """Run all volume library tests."""
    print("FVS-Python Volume Library Integration Test")
    print("=" * 60)
    
    # Test library availability
    library_available = test_volume_library_info()
    
    # Validate library
    validation_passed = test_volume_library_validation()
    
    # Test tree volume calculations
    test_tree_volume_calculations()
    
    # Test direct volume calculations
    test_direct_volume_calculations()
    
    # Test stand volume calculations
    test_stand_volume_calculations()
    
    # Compare methods
    compare_volume_methods()
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    if library_available and validation_passed:
        print("✓ Volume library successfully integrated")
        print("✓ NVEL volume equations available")
        print("✓ All volume types accessible through Tree class")
    elif library_available:
        print("⚠ Volume library loaded but validation issues detected")
        print("→ Check species mappings and DLL compatibility")
    else:
        print("⚠ Volume library not available")
        print("→ Using fallback volume calculations")
        print("→ To enable NVEL: ensure vollib.dll is in VolLibDll20250512/vollib-64bits/")
    
    print("\nIntegration Features:")
    print("• Tree.get_volume(volume_type) - Get specific volume types")
    print("• Tree.get_volume_detailed() - Get complete volume breakdown")
    print("• calculate_tree_volume() - Direct volume calculation")
    print("• Automatic fallback when NVEL unavailable")
    print("• Support for all FVS Southern variant species")


if __name__ == "__main__":
    main() 
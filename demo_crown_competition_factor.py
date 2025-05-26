#!/usr/bin/env python3
"""
Demonstration of Crown Competition Factor (CCF) calculations using FVS-Python.

This script demonstrates the new CCF module functionality including:
- Individual tree CCF calculations
- Stand-level CCF calculations
- CCF interpretation and management recommendations
- Thinning impact analysis
- Validation of implementation
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fvs_python.crown_competition_factor import (
    create_ccf_model,
    calculate_individual_ccf,
    calculate_stand_ccf,
    interpret_ccf,
    validate_ccf_implementation
)
from fvs_python.stand import Stand
from fvs_python.tree import Tree


def demo_individual_ccf():
    """Demonstrate individual tree CCF calculations."""
    print("Individual Tree CCF Calculations")
    print("-" * 40)
    
    model = create_ccf_model()
    
    # Test different tree sizes
    test_trees = [
        {"dbh": 0.1, "description": "Very small tree (at threshold)"},
        {"dbh": 5.0, "description": "Small tree"},
        {"dbh": 10.0, "description": "Medium tree"},
        {"dbh": 15.0, "description": "Large tree"},
        {"dbh": 20.0, "description": "Very large tree"}
    ]
    
    for tree in test_trees:
        ccf = model.calculate_individual_ccf(tree["dbh"], species_code="LP")
        print(f"  {tree['description']} (DBH = {tree['dbh']} in): CCF = {ccf:.4f}")
    
    print()


def demo_stand_ccf():
    """Demonstrate stand-level CCF calculations."""
    print("Stand-Level CCF Calculations")
    print("-" * 40)
    
    model = create_ccf_model()
    
    # Create example stands with different characteristics
    stands = {
        "Young plantation": [
            {"dbh": 2.0}, {"dbh": 2.5}, {"dbh": 1.8}, {"dbh": 2.2}, {"dbh": 2.1},
            {"dbh": 1.9}, {"dbh": 2.3}, {"dbh": 2.0}, {"dbh": 2.4}, {"dbh": 1.7}
        ],
        "Mature stand": [
            {"dbh": 12.0}, {"dbh": 14.0}, {"dbh": 10.0}, {"dbh": 16.0}, {"dbh": 13.0},
            {"dbh": 11.0}, {"dbh": 15.0}, {"dbh": 9.0}, {"dbh": 17.0}, {"dbh": 12.5}
        ],
        "Old growth": [
            {"dbh": 20.0}, {"dbh": 22.0}, {"dbh": 18.0}, {"dbh": 24.0}, {"dbh": 19.0}
        ]
    }
    
    for stand_name, trees in stands.items():
        ccf = model.calculate_stand_ccf(trees, "LP")
        mean_dbh = sum(t["dbh"] for t in trees) / len(trees)
        
        print(f"  {stand_name}:")
        print(f"    Trees: {len(trees)}, Mean DBH: {mean_dbh:.1f} in")
        print(f"    Stand CCF: {ccf:.1f}")
        
        # Get interpretation
        interpretation = model.interpret_ccf_value(ccf)
        print(f"    Stocking: {interpretation['stocking_level']}")
        print(f"    Recommendation: {interpretation['management_recommendation']}")
        print()


def demo_ccf_with_stand_object():
    """Demonstrate CCF calculation using Stand objects."""
    print("CCF Calculation with Stand Objects")
    print("-" * 40)
    
    # Create a stand with Tree objects
    trees = []
    dbh_values = [8.0, 10.0, 12.0, 14.0, 16.0, 9.0, 11.0, 13.0, 15.0, 17.0]
    
    for dbh in dbh_values:
        tree = Tree(dbh=dbh, height=50.0, species="LP")
        trees.append(tree)
    
    stand = Stand(trees, site_index=70)
    
    # Calculate CCF using the new module
    from fvs_python.crown_competition_factor import calculate_ccf_from_stand
    ccf = calculate_ccf_from_stand(stand)
    
    print(f"  Stand with {len(trees)} trees")
    print(f"  Mean DBH: {sum(t.dbh for t in trees) / len(trees):.1f} inches")
    print(f"  Stand CCF: {ccf:.1f}")
    
    # Interpret the CCF value
    interpretation = interpret_ccf(ccf)
    print(f"  Interpretation: {interpretation['stocking_level']}")
    print(f"  Management: {interpretation['management_recommendation']}")
    print()


def demo_thinning_analysis():
    """Demonstrate CCF analysis for thinning operations."""
    print("Thinning Impact Analysis")
    print("-" * 40)
    
    model = create_ccf_model()
    
    # Pre-thinning stand
    pre_thin_trees = [
        {"dbh": 8.0}, {"dbh": 9.0}, {"dbh": 10.0}, {"dbh": 11.0}, {"dbh": 12.0},
        {"dbh": 13.0}, {"dbh": 14.0}, {"dbh": 15.0}, {"dbh": 16.0}, {"dbh": 17.0},
        {"dbh": 7.0}, {"dbh": 8.5}, {"dbh": 9.5}, {"dbh": 10.5}, {"dbh": 11.5}
    ]
    
    # Trees to be removed (smaller trees)
    removed_trees = [
        {"dbh": 7.0}, {"dbh": 8.0}, {"dbh": 8.5}, {"dbh": 9.0}, {"dbh": 9.5}
    ]
    
    # Calculate thinning impact
    thinning_results = model.calculate_ccf_change_after_thinning(
        pre_thin_trees, removed_trees, "LP"
    )
    
    print(f"  Pre-thinning trees: {len(pre_thin_trees)}")
    print(f"  Trees removed: {len(removed_trees)}")
    print(f"  Post-thinning trees: {len(pre_thin_trees) - len(removed_trees)}")
    print()
    print(f"  Pre-thinning CCF: {thinning_results['pre_thin_ccf']:.1f}")
    print(f"  CCF removed: {thinning_results['removed_ccf']:.1f}")
    print(f"  Post-thinning CCF: {thinning_results['post_thin_ccf']:.1f}")
    print(f"  CCF reduction: {thinning_results['ccf_reduction_percent']:.1f}%")
    
    # Interpret before and after
    pre_interp = model.interpret_ccf_value(thinning_results['pre_thin_ccf'])
    post_interp = model.interpret_ccf_value(thinning_results['post_thin_ccf'])
    
    print()
    print(f"  Before thinning: {pre_interp['stocking_level']}")
    print(f"  After thinning: {post_interp['stocking_level']}")
    print()


def demo_target_density_planning():
    """Demonstrate planning for target CCF values."""
    print("Target Density Planning")
    print("-" * 40)
    
    model = create_ccf_model()
    
    target_ccf_values = [100, 150, 200]
    mean_dbh_values = [8.0, 12.0, 16.0]
    
    print("  Trees per acre needed to achieve target CCF:")
    print("  " + "-" * 50)
    print(f"  {'Target CCF':<12} {'Mean DBH':<10} {'Trees/Acre':<12}")
    print("  " + "-" * 50)
    
    for target_ccf in target_ccf_values:
        for mean_dbh in mean_dbh_values:
            tpa = model.estimate_trees_per_acre_at_ccf(target_ccf, mean_dbh, "LP")
            print(f"  {target_ccf:<12} {mean_dbh:<10.1f} {tpa:<12.0f}")
    
    print()


def demo_validation():
    """Demonstrate implementation validation."""
    print("Implementation Validation")
    print("-" * 40)
    
    validation_results = validate_ccf_implementation()
    
    print(f"  Total tests: {validation_results['passed'] + validation_results['failed']}")
    print(f"  Tests passed: {validation_results['passed']}")
    print(f"  Tests failed: {validation_results['failed']}")
    
    if validation_results['failed'] > 0:
        print("\n  Failed test details:")
        for detail in validation_results['details']:
            if not detail['passed']:
                print(f"    {detail['description']}: Error = {detail['error']:.6f}")
    else:
        print("  ✓ All validation tests passed!")
    
    print()


def main():
    """Run all CCF demonstrations."""
    print("FVS-Python Crown Competition Factor (CCF) Module Demonstration")
    print("=" * 65)
    print()
    
    # Run all demonstrations
    demo_individual_ccf()
    demo_stand_ccf()
    demo_ccf_with_stand_object()
    demo_thinning_analysis()
    demo_target_density_planning()
    demo_validation()
    
    print("CCF Module Demonstration Complete!")
    print()
    print("Key Features Demonstrated:")
    print("- Individual tree CCF calculations using equation 4.5.1")
    print("- Stand-level CCF as sum of individual tree values")
    print("- CCF interpretation and management recommendations")
    print("- Thinning impact analysis")
    print("- Target density planning")
    print("- Integration with existing Stand and Tree classes")
    print("- Implementation validation against known values")


if __name__ == "__main__":
    main() 
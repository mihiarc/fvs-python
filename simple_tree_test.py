#!/usr/bin/env python3
"""
Simple test script for loblolly pine single tree growth.
Demonstrates basic tree growth mechanics and key parameters.
"""

import sys
import os

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fvs_python.tree import Tree

def simple_tree_growth_test():
    """Simple demonstration of loblolly pine tree growth."""
    
    print("=== Simple Loblolly Pine Tree Growth Test ===\n")
    
    # Create a young loblolly pine tree
    tree = Tree(
        dbh=2.0,           # 2 inches diameter at breast height
        height=12.0,       # 12 feet tall
        species="LP",      # Loblolly Pine
        age=10,            # 10 years old
        crown_ratio=0.8    # 80% live crown
    )
    
    print("Initial Tree Characteristics:")
    print(f"  Species: {tree.species} (Loblolly Pine)")
    print(f"  Age: {tree.age} years")
    print(f"  DBH: {tree.dbh:.1f} inches")
    print(f"  Height: {tree.height:.1f} feet")
    print(f"  Crown Ratio: {tree.crown_ratio:.2f}")
    print(f"  Volume: {tree.get_volume('total_cubic'):.2f} cubic feet")
    
    # Site and stand conditions
    site_index = 70      # Site index (base age 25) - moderate productivity
    ba = 80              # Stand basal area (sq ft/acre)
    pbal = 40            # Plot basal area in larger trees
    competition = 0.3    # Competition factor (0-1)
    
    print(f"\nSite Conditions:")
    print(f"  Site Index: {site_index} feet (base age 25)")
    print(f"  Stand Basal Area: {ba} sq ft/acre")
    print(f"  Competition Factor: {competition}")
    
    print(f"\n{'Age':<5} {'DBH':<6} {'Height':<8} {'Crown':<7} {'Volume':<8} {'Growth Type'}")
    print(f"{'(yr)':<5} {'(in)':<6} {'(ft)':<8} {'Ratio':<7} {'(cu ft)':<8}")
    print("-" * 50)
    
    # Print initial state
    volume = tree.get_volume('total_cubic')
    growth_type = get_growth_model_type(tree.dbh)
    print(f"{tree.age:<5} {tree.dbh:<6.1f} {tree.height:<8.1f} {tree.crown_ratio:<7.2f} {volume:<8.2f} {growth_type}")
    
    # Simulate growth for 40 years (8 periods of 5 years each)
    for period in range(8):
        # Grow the tree for 5 years
        tree.grow(
            site_index=site_index,
            competition_factor=competition,
            rank=0.5,           # Middle of diameter distribution
            relsdi=5.0,         # Relative stand density index
            ba=ba,
            pbal=pbal,
            slope=0.05,         # 5% slope
            aspect=0,           # North-facing
            time_step=5         # 5-year growth period
        )
        
        # Print updated state
        volume = tree.get_volume('total_cubic')
        growth_type = get_growth_model_type(tree.dbh)
        print(f"{tree.age:<5} {tree.dbh:<6.1f} {tree.height:<8.1f} {tree.crown_ratio:<7.2f} {volume:<8.2f} {growth_type}")
    
    print(f"\nFinal Tree Characteristics:")
    print(f"  Age: {tree.age} years")
    print(f"  DBH: {tree.dbh:.1f} inches")
    print(f"  Height: {tree.height:.1f} feet")
    print(f"  Crown Ratio: {tree.crown_ratio:.2f}")
    print(f"  Volume: {tree.get_volume('total_cubic'):.2f} cubic feet")
    
    # Calculate total growth
    initial_dbh = 2.0
    initial_height = 12.0
    dbh_growth = tree.dbh - initial_dbh
    height_growth = tree.height - initial_height
    
    print(f"\nTotal Growth Over 40 Years:")
    print(f"  DBH Growth: +{dbh_growth:.1f} inches")
    print(f"  Height Growth: +{height_growth:.1f} feet")
    print(f"  Average Annual DBH Growth: {dbh_growth/40:.2f} inches/year")
    print(f"  Average Annual Height Growth: {height_growth/40:.1f} feet/year")

def get_growth_model_type(dbh):
    """Determine which growth model is being used based on DBH."""
    xmin, xmax = 1.0, 3.0
    
    if dbh < xmin:
        return "Small tree"
    elif dbh > xmax:
        return "Large tree"
    else:
        weight = (dbh - xmin) / (xmax - xmin)
        return f"Blended ({weight:.1f})"

def test_different_site_indices():
    """Test how site index affects tree growth."""
    
    print("\n\n=== Site Index Comparison ===\n")
    
    site_indices = [50, 70, 90]  # Poor, average, excellent sites
    
    print(f"Comparing growth on different site qualities:")
    print(f"(Starting with 2\" DBH, 12' height, age 10)")
    print()
    
    for si in site_indices:
        # Create identical trees
        tree = Tree(dbh=2.0, height=12.0, species="LP", age=10, crown_ratio=0.8)
        
        # Grow for 20 years
        for _ in range(4):  # 4 periods of 5 years = 20 years
            tree.grow(
                site_index=si,
                competition_factor=0.3,
                rank=0.5,
                relsdi=5.0,
                ba=80,
                pbal=40,
                slope=0.05,
                aspect=0,
                time_step=5
            )
        
        site_quality = "Poor" if si == 50 else "Average" if si == 70 else "Excellent"
        print(f"Site Index {si} ({site_quality}):")
        print(f"  Final DBH: {tree.dbh:.1f} inches")
        print(f"  Final Height: {tree.height:.1f} feet")
        print(f"  Final Volume: {tree.get_volume('total_cubic'):.2f} cubic feet")
        print()

def test_competition_effects():
    """Test how competition affects tree growth."""
    
    print("\n=== Competition Effects Test ===\n")
    
    competition_levels = [0.1, 0.5, 0.9]  # Low, moderate, high competition
    
    print(f"Comparing growth under different competition levels:")
    print(f"(Starting with 2\" DBH, 12' height, age 10, Site Index 70)")
    print()
    
    for comp in competition_levels:
        # Create identical trees
        tree = Tree(dbh=2.0, height=12.0, species="LP", age=10, crown_ratio=0.8)
        
        # Grow for 20 years
        for _ in range(4):  # 4 periods of 5 years = 20 years
            tree.grow(
                site_index=70,
                competition_factor=comp,
                rank=0.5,
                relsdi=5.0,
                ba=80,
                pbal=40,
                slope=0.05,
                aspect=0,
                time_step=5
            )
        
        comp_level = "Low" if comp == 0.1 else "Moderate" if comp == 0.5 else "High"
        print(f"Competition {comp} ({comp_level}):")
        print(f"  Final DBH: {tree.dbh:.1f} inches")
        print(f"  Final Height: {tree.height:.1f} feet")
        print(f"  Final Volume: {tree.get_volume('total_cubic'):.2f} cubic feet")
        print()

if __name__ == "__main__":
    # Run the basic growth test
    simple_tree_growth_test()
    
    # Test site index effects
    test_different_site_indices()
    
    # Test competition effects
    test_competition_effects()
    
    print("=== Test Complete ===")
    print("This demonstrates the basic mechanics of single tree growth")
    print("for loblolly pine using the FVS-Python growth models.") 
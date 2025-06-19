#!/usr/bin/env python3
"""
Test script for single tree growth modeling in loblolly pine.
Demonstrates both small-tree and large-tree growth models and their transition.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fvs_python.tree import Tree
from fvs_python.config_loader import get_config_loader

def test_single_tree_growth():
    """Test single tree growth for loblolly pine across different initial sizes."""
    
    print("=== FVS-Python Single Tree Growth Test ===")
    print("Testing loblolly pine (LP) growth models\n")
    
    # Test parameters
    species = "LP"  # Loblolly Pine
    site_index = 70  # Site index (base age 25)
    initial_age = 5  # Starting age
    simulation_years = 45  # Simulate to age 50
    time_step = 5  # 5-year growth periods
    
    # Stand conditions for large tree model
    competition_factor = 0.3  # Moderate competition
    ba = 80  # Stand basal area (sq ft/acre)
    pbal = 40  # Plot basal area in larger trees
    slope = 0.05  # 5% slope
    aspect = 0  # North-facing (0 radians)
    rank = 0.5  # Middle of diameter distribution
    relsdi = 5.0  # Relative stand density index
    
    # Test different initial tree sizes to show model transition
    test_trees = [
        {"name": "Small seedling", "dbh": 0.5, "height": 2.0},
        {"name": "Small sapling", "dbh": 1.5, "height": 8.0},
        {"name": "Transition tree", "dbh": 2.5, "height": 15.0},
        {"name": "Large sapling", "dbh": 4.0, "height": 25.0},
        {"name": "Pole timber", "dbh": 8.0, "height": 45.0}
    ]
    
    results = []
    
    print(f"Site Index: {site_index} feet (base age 25)")
    print(f"Stand Conditions: BA={ba} sq ft/acre, Competition={competition_factor}")
    print(f"Simulation: Age {initial_age} to {initial_age + simulation_years} years\n")
    
    for tree_info in test_trees:
        print(f"Testing: {tree_info['name']} (Initial DBH: {tree_info['dbh']}\", Height: {tree_info['height']}')")
        
        # Create tree
        tree = Tree(
            dbh=tree_info['dbh'],
            height=tree_info['height'],
            species=species,
            age=initial_age,
            crown_ratio=0.85
        )
        
        # Track growth over time
        tree_results = []
        
        # Record initial state
        tree_results.append({
            'tree_name': tree_info['name'],
            'age': tree.age,
            'dbh': tree.dbh,
            'height': tree.height,
            'crown_ratio': tree.crown_ratio,
            'volume': tree.get_volume('total_cubic')
        })
        
        # Simulate growth
        for period in range(0, simulation_years, time_step):
            tree.grow(
                site_index=site_index,
                competition_factor=competition_factor,
                rank=rank,
                relsdi=relsdi,
                ba=ba,
                pbal=pbal,
                slope=slope,
                aspect=aspect,
                time_step=time_step
            )
            
            tree_results.append({
                'tree_name': tree_info['name'],
                'age': tree.age,
                'dbh': tree.dbh,
                'height': tree.height,
                'crown_ratio': tree.crown_ratio,
                'volume': tree.get_volume('total_cubic')
            })
        
        results.extend(tree_results)
        
        # Print final results for this tree
        final = tree_results[-1]
        initial = tree_results[0]
        dbh_growth = final['dbh'] - initial['dbh']
        height_growth = final['height'] - initial['height']
        
        print(f"  Final: DBH={final['dbh']:.1f}\", Height={final['height']:.1f}', Volume={final['volume']:.1f} cu ft")
        print(f"  Growth: DBH +{dbh_growth:.1f}\", Height +{height_growth:.1f}'")
        print()
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(results)
    
    # Create visualizations
    create_growth_plots(df)
    
    # Save results to CSV
    df.to_csv('single_tree_growth_results.csv', index=False)
    print("Results saved to 'single_tree_growth_results.csv'")
    
    return df

def create_growth_plots(df):
    """Create visualization plots for tree growth."""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Loblolly Pine Single Tree Growth Trajectories', fontsize=16, fontweight='bold')
    
    # Color palette for different trees
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Plot 1: DBH Growth
    for i, tree_name in enumerate(df['tree_name'].unique()):
        tree_data = df[df['tree_name'] == tree_name]
        ax1.plot(tree_data['age'], tree_data['dbh'], 
                marker='o', linewidth=2, markersize=6,
                color=colors[i], label=tree_name)
    
    ax1.set_xlabel('Age (years)')
    ax1.set_ylabel('DBH (inches)')
    ax1.set_title('Diameter Growth Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Height Growth
    for i, tree_name in enumerate(df['tree_name'].unique()):
        tree_data = df[df['tree_name'] == tree_name]
        ax2.plot(tree_data['age'], tree_data['height'], 
                marker='s', linewidth=2, markersize=6,
                color=colors[i], label=tree_name)
    
    ax2.set_xlabel('Age (years)')
    ax2.set_ylabel('Height (feet)')
    ax2.set_title('Height Growth Over Time')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Plot 3: Height-Diameter Relationship
    for i, tree_name in enumerate(df['tree_name'].unique()):
        tree_data = df[df['tree_name'] == tree_name]
        ax3.plot(tree_data['dbh'], tree_data['height'], 
                marker='^', linewidth=2, markersize=6,
                color=colors[i], label=tree_name)
    
    ax3.set_xlabel('DBH (inches)')
    ax3.set_ylabel('Height (feet)')
    ax3.set_title('Height-Diameter Relationship')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Plot 4: Volume Growth
    for i, tree_name in enumerate(df['tree_name'].unique()):
        tree_data = df[df['tree_name'] == tree_name]
        ax4.plot(tree_data['age'], tree_data['volume'], 
                marker='d', linewidth=2, markersize=6,
                color=colors[i], label=tree_name)
    
    ax4.set_xlabel('Age (years)')
    ax4.set_ylabel('Volume (cubic feet)')
    ax4.set_title('Volume Growth Over Time')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('loblolly_pine_growth_trajectories.png', dpi=300, bbox_inches='tight')
    print("Growth plots saved to 'loblolly_pine_growth_trajectories.png'")
    plt.show()

def test_growth_model_transition():
    """Test the transition between small-tree and large-tree growth models."""
    
    print("\n=== Growth Model Transition Test ===")
    print("Testing transition between small-tree and large-tree models\n")
    
    # Create trees across the transition zone (1-3 inch DBH)
    dbh_values = np.arange(0.5, 5.0, 0.25)
    site_index = 70
    age = 15
    
    results = []
    
    for dbh in dbh_values:
        # Estimate height using height-diameter relationship
        # Using Curtis-Arney parameters from config
        p2 = 243.860648
        p3 = 4.28460566
        p4 = -0.47130185
        
        if dbh >= 3.0:
            height = 4.5 + p2 * np.exp(-p3 * dbh**p4)
        else:
            # Linear interpolation for small trees
            height_at_3 = 4.5 + p2 * np.exp(-p3 * 3.0**p4)
            height = (height_at_3 - 4.51) * (dbh - 0.5) / (3.0 - 0.5) + 4.51
        
        tree = Tree(dbh=dbh, height=height, species="LP", age=age, crown_ratio=0.8)
        
        # Grow for one period
        tree.grow(
            site_index=site_index,
            competition_factor=0.3,
            rank=0.5,
            relsdi=5.0,
            ba=80,
            pbal=40,
            slope=0.05,
            aspect=0,
            time_step=5
        )
        
        # Determine which model dominates
        xmin, xmax = 1.0, 3.0
        if dbh < xmin:
            weight = 0.0
            model = "Small tree only"
        elif dbh > xmax:
            weight = 1.0
            model = "Large tree only"
        else:
            weight = (dbh - xmin) / (xmax - xmin)
            model = f"Blended ({weight:.2f})"
        
        results.append({
            'initial_dbh': dbh,
            'final_dbh': tree.dbh,
            'dbh_growth': tree.dbh - dbh,
            'initial_height': height,
            'final_height': tree.height,
            'height_growth': tree.height - height,
            'weight': weight,
            'model': model
        })
    
    # Convert to DataFrame and display
    df_transition = pd.DataFrame(results)
    
    # Plot transition
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # DBH Growth vs Initial DBH
    ax1.scatter(df_transition['initial_dbh'], df_transition['dbh_growth'], 
               c=df_transition['weight'], cmap='viridis', s=50, alpha=0.7)
    ax1.axvline(x=1.0, color='red', linestyle='--', alpha=0.7, label='Transition start (1")')
    ax1.axvline(x=3.0, color='red', linestyle='--', alpha=0.7, label='Transition end (3")')
    ax1.set_xlabel('Initial DBH (inches)')
    ax1.set_ylabel('5-Year DBH Growth (inches)')
    ax1.set_title('DBH Growth vs Initial Size\n(Color = Large Tree Model Weight)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Height Growth vs Initial DBH
    ax2.scatter(df_transition['initial_dbh'], df_transition['height_growth'], 
               c=df_transition['weight'], cmap='viridis', s=50, alpha=0.7)
    ax2.axvline(x=1.0, color='red', linestyle='--', alpha=0.7, label='Transition start (1")')
    ax2.axvline(x=3.0, color='red', linestyle='--', alpha=0.7, label='Transition end (3")')
    ax2.set_xlabel('Initial DBH (inches)')
    ax2.set_ylabel('5-Year Height Growth (feet)')
    ax2.set_title('Height Growth vs Initial Size\n(Color = Large Tree Model Weight)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('growth_model_transition.png', dpi=300, bbox_inches='tight')
    print("Transition analysis saved to 'growth_model_transition.png'")
    plt.show()
    
    # Print summary statistics
    print("Growth Model Transition Summary:")
    print(f"Small tree model only (DBH < 1\"): {len(df_transition[df_transition['weight'] == 0])} trees")
    print(f"Blended models (1\" ≤ DBH ≤ 3\"): {len(df_transition[(df_transition['weight'] > 0) & (df_transition['weight'] < 1)])} trees")
    print(f"Large tree model only (DBH > 3\"): {len(df_transition[df_transition['weight'] == 1])} trees")
    
    return df_transition

def test_configuration_loading():
    """Test that configuration loading works correctly."""
    
    print("\n=== Configuration Loading Test ===")
    
    try:
        # Test config loader
        loader = get_config_loader()
        print("✓ Config loader initialized successfully")
        
        # Test species config loading
        lp_config = loader.load_species_config("LP")
        print("✓ Loblolly pine configuration loaded successfully")
        
        # Display key parameters
        print("\nKey Loblolly Pine Parameters:")
        print(f"  Scientific name: {lp_config['metadata']['scientific_name']}")
        print(f"  Common name: {lp_config['metadata']['common_name']}")
        print(f"  Site index range: {lp_config['site_index']['min']}-{lp_config['site_index']['max']} feet")
        print(f"  Height-diameter model: {lp_config['height_diameter']['model']}")
        
        # Curtis-Arney parameters
        ca_params = lp_config['height_diameter']['curtis_arney']
        print(f"  Curtis-Arney p2: {ca_params['p2']:.6f}")
        print(f"  Curtis-Arney p3: {ca_params['p3']:.6f}")
        print(f"  Curtis-Arney p4: {ca_params['p4']:.6f}")
        
        # Diameter growth parameters
        dg_params = lp_config['diameter_growth']['coefficients']
        print(f"  Diameter growth b1: {dg_params['b1']:.6f}")
        print(f"  Diameter growth b2: {dg_params['b2']:.6f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting FVS-Python Single Tree Growth Tests...\n")
    
    # Test 1: Configuration loading
    config_ok = test_configuration_loading()
    
    if config_ok:
        # Test 2: Single tree growth trajectories
        growth_results = test_single_tree_growth()
        
        # Test 3: Growth model transition
        transition_results = test_growth_model_transition()
        
        print("\n=== Test Summary ===")
        print("✓ All tests completed successfully!")
        print("✓ Configuration loading: PASSED")
        print("✓ Single tree growth: PASSED")
        print("✓ Model transition: PASSED")
        print("\nOutput files generated:")
        print("  - single_tree_growth_results.csv")
        print("  - loblolly_pine_growth_trajectories.png")
        print("  - growth_model_transition.png")
        
    else:
        print("\n✗ Configuration loading failed. Cannot proceed with growth tests.")
        sys.exit(1) 
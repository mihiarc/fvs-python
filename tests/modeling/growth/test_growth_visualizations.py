"""Visualization-based tests for TreeGrowthSimulator class."""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple

from fvs_python.modeling.growth.tree_growth_simulator import TreeGrowthSimulator
from tests.modeling.growth.test_tree_growth_simulator import TestTree, TEST_COEFFICIENTS, SAMPLE_STAND_CONDITIONS

def simulate_growth_series(
    simulator: TreeGrowthSimulator,
    initial_tree: TestTree,
    stand_conditions: Dict,
    steps: int = 10
) -> Tuple[List[float], List[float], List[float]]:
    """Simulate growth over multiple time steps."""
    dbh_series = [initial_tree.dbh]
    height_series = [initial_tree.height]
    cr_series = [initial_tree.crown_ratio]
    
    current_tree = initial_tree
    for _ in range(steps):
        growth = simulator.simulate_growth(current_tree, stand_conditions)
        new_dbh = current_tree.dbh + growth['dbh_growth']
        new_height = current_tree.height + growth['height_growth']
        new_cr = current_tree.crown_ratio + growth['crown_ratio_change']
        
        dbh_series.append(new_dbh)
        height_series.append(new_height)
        cr_series.append(new_cr)
        
        # Update tree for next iteration
        current_tree = TestTree(
            species=current_tree.species,
            dbh=new_dbh,
            height=new_height,
            crown_ratio=new_cr,
            age=current_tree.age + 5  # 5-year growth periods
        )
    
    return dbh_series, height_series, cr_series

def test_visualize_height_diameter_relationship(tmp_path):
    """Test and visualize height-diameter relationship across growth periods."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    
    # Create trees of different initial sizes
    initial_trees = [
        TestTree('LP', 1.0, 6.0, 0.6),  # Small tree
        TestTree('LP', 2.5, 15.0, 0.5),  # Transition
        TestTree('LP', 4.0, 25.0, 0.4)   # Large tree
    ]
    
    plt.figure(figsize=(10, 6))
    
    for tree in initial_trees:
        dbh_series, height_series, _ = simulate_growth_series(
            simulator, tree, SAMPLE_STAND_CONDITIONS)
        
        plt.plot(dbh_series, height_series, 'o-', 
                label=f'Initial DBH: {tree.dbh:.1f}"')
    
    plt.xlabel('DBH (inches)')
    plt.ylabel('Height (feet)')
    plt.title('Height-Diameter Growth Trajectories')
    plt.legend()
    plt.grid(True)
    
    # Save plot
    plt.savefig(tmp_path / 'height_diameter_relationship.png')
    plt.close()

def test_visualize_growth_rates(tmp_path):
    """Test and visualize growth rates across different size classes."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    
    # Generate range of initial DBH values
    dbh_range = np.linspace(0.5, 8.0, 20)
    height_growth_rates = []
    dbh_growth_rates = []
    
    for initial_dbh in dbh_range:
        # Estimate initial height using H-D relationship
        initial_height = 4.51 + TEST_COEFFICIENTS['c1'] * np.exp(
            -TEST_COEFFICIENTS['c2'] * initial_dbh**TEST_COEFFICIENTS['c3'])
        
        tree = TestTree('LP', initial_dbh, initial_height, 0.5)
        growth = simulator.simulate_growth(tree, SAMPLE_STAND_CONDITIONS)
        
        height_growth_rates.append(growth['height_growth'])
        dbh_growth_rates.append(growth['dbh_growth'])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot height growth rates
    ax1.plot(dbh_range, height_growth_rates, 'b.-')
    ax1.set_xlabel('Initial DBH (inches)')
    ax1.set_ylabel('Height Growth (feet/period)')
    ax1.set_title('Height Growth Rate vs Initial DBH')
    ax1.grid(True)
    
    # Plot DBH growth rates
    ax2.plot(dbh_range, dbh_growth_rates, 'r.-')
    ax2.set_xlabel('Initial DBH (inches)')
    ax2.set_ylabel('DBH Growth (inches/period)')
    ax2.set_title('DBH Growth Rate vs Initial DBH')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(tmp_path / 'growth_rates.png')
    plt.close()

def test_visualize_competition_effects(tmp_path):
    """Test and visualize effects of competition on growth."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    tree = TestTree('LP', 4.0, 25.0, 0.5)
    
    ccf_range = np.linspace(50, 300, 15)
    height_growth_rates = []
    dbh_growth_rates = []
    
    for ccf in ccf_range:
        conditions = {**SAMPLE_STAND_CONDITIONS, 'crown_competition_factor': ccf}
        growth = simulator.simulate_growth(tree, conditions)
        
        height_growth_rates.append(growth['height_growth'])
        dbh_growth_rates.append(growth['dbh_growth'])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot height growth response to competition
    ax1.plot(ccf_range, height_growth_rates, 'b.-')
    ax1.set_xlabel('Crown Competition Factor')
    ax1.set_ylabel('Height Growth (feet/period)')
    ax1.set_title('Height Growth Response to Competition')
    ax1.grid(True)
    
    # Plot DBH growth response to competition
    ax2.plot(ccf_range, dbh_growth_rates, 'r.-')
    ax2.set_xlabel('Crown Competition Factor')
    ax2.set_ylabel('DBH Growth (inches/period)')
    ax2.set_title('DBH Growth Response to Competition')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(tmp_path / 'competition_effects.png')
    plt.close()

def test_visualize_crown_ratio_dynamics(tmp_path):
    """Test and visualize crown ratio changes over time."""
    simulator = TreeGrowthSimulator('LP', 70.0, TEST_COEFFICIENTS)
    
    # Test different initial crown ratios
    initial_crs = [0.3, 0.5, 0.7]
    plt.figure(figsize=(10, 6))
    
    for initial_cr in initial_crs:
        tree = TestTree('LP', 3.0, 20.0, initial_cr)
        _, _, cr_series = simulate_growth_series(
            simulator, tree, SAMPLE_STAND_CONDITIONS, steps=15)
        
        periods = range(len(cr_series))
        plt.plot(periods, cr_series, 'o-', 
                label=f'Initial CR: {initial_cr:.1f}')
    
    plt.xlabel('Growth Periods')
    plt.ylabel('Crown Ratio')
    plt.title('Crown Ratio Dynamics Over Time')
    plt.legend()
    plt.grid(True)
    plt.ylim(0.1, 1.0)
    
    # Add bounds
    plt.axhline(y=0.2, color='r', linestyle='--', alpha=0.5, label='Lower Bound')
    plt.axhline(y=0.9, color='r', linestyle='--', alpha=0.5, label='Upper Bound')
    
    plt.savefig(tmp_path / 'crown_ratio_dynamics.png')
    plt.close() 
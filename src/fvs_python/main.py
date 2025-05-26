#!/usr/bin/env python3

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import os
import csv
import yaml

# Import package modules
from .stand import Stand
from .tree import Tree
from .growth_plots import (
    plot_stand_trajectories,
    plot_size_distributions,
    plot_mortality_patterns,
    plot_competition_effects
)

def initialize_planted_stand(species: str, tpa: int, site_index: float) -> Stand:
    """Initialize a planted pine stand with given specifications.
    
    Args:
        species: Species code ('LP', 'SP', 'LL', 'SA')
        tpa: Trees per acre at planting
        site_index: Site index (base age 25)
    
    Returns:
        Stand object initialized with trees
    """
    stand = Stand()
    stand.site_index = site_index
    
    # Set initial tree attributes with random variation
    dbh_mean = 0.5  # inches at age 0
    dbh_sd = 0.1    # standard deviation
    
    # Generate initial tree list
    for _ in range(tpa):
        dbh = max(0.1, np.random.normal(dbh_mean, dbh_sd))
        height = 1.0  # feet at age 0
        
        tree = Tree(
            species=species,
            dbh=dbh,
            height=height,
            expansion_factor=1.0
        )
        stand.add_tree(tree)
    
    return stand

def simulate_stand_growth(stand: Stand, end_age: int = 50, timestep: int = 5) -> list:
    """Simulate stand growth from age 0 to end_age."""
    results = []
    
    for age in range(0, end_age + 1, timestep):
        # Update stand competition metrics
        stand.update_competition()
        
        # Grow each tree
        for tree in stand.trees:
            # Calculate and apply growth
            tree.grow(stand, age)
        
        # Apply mortality
        stand.apply_mortality()
        
        # Calculate and store stand metrics
        metrics = stand.calculate_metrics()
        metrics['age'] = age
        results.append(metrics)
        
        logging.info(f"Completed age {age} simulation")
    
    return results

def generate_yield_table(species: str, site_classes: list, tpa_range: list) -> pd.DataFrame:
    """Generate yield tables for different site classes and planting densities."""
    results = []
    
    for site_index in site_classes:
        for initial_tpa in tpa_range:
            logging.info(f"Simulating {species} SI={site_index} TPA={initial_tpa}")
            
            # Initialize and simulate stand
            stand = initialize_planted_stand(species, initial_tpa, site_index)
            growth_results = simulate_stand_growth(stand)
            
            # Add simulation parameters to results
            for period in growth_results:
                period.update({
                    'species': species,
                    'site_index': site_index,
                    'initial_tpa': initial_tpa
                })
                results.append(period)
    
    return pd.DataFrame(results)

def run_simulation(years=50, timestep=5):
    """Run stand growth simulation.
    
    Args:
        years: Total simulation length in years
        timestep: Years between measurements
    
    Returns:
        List of dictionaries containing stand metrics at each timestep
    """
    # Load configuration using new config system
    from .config_loader import load_stand_config
    params = load_stand_config('LP')
    
    # Initialize stand
    stand = Stand.initialize_planted(trees_per_acre=500)
    
    # Store metrics over time
    metrics = []
    
    # Run simulation
    for year in range(0, years + 1, timestep):
        # Record metrics at current age
        metrics.append(stand.get_metrics())
        
        # Generate size distribution plots at key ages
        if year in [0, 10, 25, 50]:
            plot_size_distributions(
                stand,
                save_path=f'output/size_distributions_age_{year}.png'
            )
        
        # Generate competition plots at key ages
        if year in [10, 25, 50]:
            plot_competition_effects(
                stand,
                save_path=f'output/competition_age_{year}.png'
            )
        
        # Grow stand for next period
        if year < years:
            stand.grow(years=timestep)
    
    return metrics

def save_yield_table(metrics, output_path):
    """Save stand metrics as CSV yield table.
    
    Args:
        metrics: List of metric dictionaries
        output_path: Path to save CSV file
    """
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics[0].keys())
        writer.writeheader()
        writer.writerows(metrics)

def main():
    """Main execution function."""
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # Run simulation
    print("Starting stand growth simulation...")
    metrics = run_simulation()
    
    # Save yield table
    yield_table_path = output_dir / 'yield_table.csv'
    save_yield_table(metrics, yield_table_path)
    print(f"Yield table saved to {yield_table_path}")
    
    # Generate trajectory plots
    plot_stand_trajectories(
        metrics,
        save_path=output_dir / 'stand_trajectories.png'
    )
    print("Stand trajectory plots saved")
    
    # Generate mortality plot
    plot_mortality_patterns(
        metrics,
        save_path=output_dir / 'mortality_patterns.png'
    )
    print("Mortality pattern plot saved")
    
    print("\nSimulation Results Summary:")
    print("-" * 40)
    print(f"Initial trees per acre: {metrics[0]['tpa']:.0f}")
    print(f"Final trees per acre: {metrics[-1]['tpa']:.0f}")
    print(f"Final stand age: {metrics[-1]['age']} years")
    print(f"Final mean DBH: {metrics[-1]['mean_dbh']:.1f} inches")
    print(f"Final mean height: {metrics[-1]['mean_height']:.1f} feet")
    print(f"Final volume: {metrics[-1]['volume']:.0f} cubic feet/acre")

if __name__ == '__main__':
    main()
"""
Visualization tests for the growth module.
These tests generate plots to visually inspect height-diameter relationships.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from src.growth_models import curtis_arney_height, wykoff_height, species_data
import sqlite3
import pandas as pd
from src.growth_models import calculate_small_tree_height_growth

# Ensure plots directory exists
PLOTS_DIR = Path(__file__).parent / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)

def test_plot_height_diameter_curves():
    """Generate plots comparing height-diameter relationships for different species."""
    # Select a few representative species
    species_list = ['FR', 'WP', 'LL']  # Fraser Fir, White Pine, Loblolly Pine
    dbh_values = np.linspace(1, 30, 100)  # DBH range from 1 to 30 inches
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot Curtis-Arney curves
    for species in species_list:
        heights = [curtis_arney_height(dbh, species) for dbh in dbh_values]
        ax1.plot(dbh_values, heights, label=f'{species}')
    
    ax1.set_title('Curtis-Arney Height-Diameter Curves')
    ax1.set_xlabel('DBH (inches)')
    ax1.set_ylabel('Height (feet)')
    ax1.grid(True)
    ax1.legend()
    
    # Plot Wykoff curves
    for species in species_list:
        heights = [wykoff_height(dbh, species) for dbh in dbh_values]
        ax2.plot(dbh_values, heights, label=f'{species}')
    
    ax2.set_title('Wykoff Height-Diameter Curves')
    ax2.set_xlabel('DBH (inches)')
    ax2.set_ylabel('Height (feet)')
    ax2.grid(True)
    ax2.legend()
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'height_diameter_curves.png')
    plt.close()

def test_plot_small_tree_transition():
    """Generate plots showing the transition between small and large tree calculations."""
    species = 'FR'  # Use Fraser Fir as an example
    dbh_values = np.linspace(1, 5, 100)  # Focus on the transition region
    
    # Calculate heights
    heights = [curtis_arney_height(dbh, species) for dbh in dbh_values]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(dbh_values, heights, label='Height curve')
    plt.axvline(x=3, color='r', linestyle='--', label='3-inch threshold')
    
    plt.title(f'Small-Large Tree Transition for {species}')
    plt.xlabel('DBH (inches)')
    plt.ylabel('Height (feet)')
    plt.grid(True)
    plt.legend()
    
    # Save the plot
    plt.savefig(PLOTS_DIR / 'small_tree_transition.png')
    plt.close()

def test_plot_species_comparison():
    """Generate a plot comparing height predictions between methods for a single species."""
    species = 'WP'  # White Pine
    dbh_values = np.linspace(3, 30, 100)  # Focus on larger trees
    
    # Calculate heights using both methods
    heights_ca = [curtis_arney_height(dbh, species) for dbh in dbh_values]
    heights_w = [wykoff_height(dbh, species) for dbh in dbh_values]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(dbh_values, heights_ca, label='Curtis-Arney')
    plt.plot(dbh_values, heights_w, label='Wykoff')
    
    plt.title(f'Method Comparison for {species}')
    plt.xlabel('DBH (inches)')
    plt.ylabel('Height (feet)')
    plt.grid(True)
    plt.legend()
    
    # Save the plot
    plt.savefig(PLOTS_DIR / 'method_comparison.png')
    plt.close()

def test_plot_coefficient_sensitivity():
    """Generate plots showing sensitivity to coefficient changes."""
    base_coeffs = {
        'CurtisArney_b0': 289.4,
        'CurtisArney_b1': 3.8,
        'CurtisArney_b2': -0.32,
        'Dbw': 0.2
    }
    
    dbh_values = np.linspace(3, 30, 100)
    variations = [-0.1, 0, 0.1]  # -10%, base, +10%
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    params = ['CurtisArney_b0', 'CurtisArney_b1', 'CurtisArney_b2']
    
    for i, param in enumerate(params):
        for var in variations:
            coeffs = base_coeffs.copy()
            coeffs[param] = base_coeffs[param] * (1 + var)
            heights = [curtis_arney_height(dbh, 'TEST', coeffs) for dbh in dbh_values]
            axes[i].plot(dbh_values, heights, 
                        label=f'{param} {"-10%" if var<0 else "+10%" if var>0 else "base"}')
        
        axes[i].set_title(f'Sensitivity to {param}')
        axes[i].set_xlabel('DBH (inches)')
        axes[i].set_ylabel('Height (feet)')
        axes[i].grid(True)
        axes[i].legend()
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'coefficient_sensitivity.png')
    plt.close()

def test_plot_small_tree_growth_trajectories():
    """Generate plots showing small tree growth trajectories at different site indices."""
    # Get coefficients from database
    with sqlite3.connect('data/sqlite_databases/fvspy.db') as conn:
        # Get small tree growth coefficients for Loblolly Pine
        query = "SELECT * FROM small_tree_growth WHERE species_code = 'LP'"
        df = pd.read_sql_query(query, conn)
        if df.empty:
            raise ValueError("No small tree growth coefficients found for LP")
        coeffs = df.iloc[0]
        
        # Get site index bounds
        query = "SELECT si_min, si_max FROM site_index_range WHERE species_code = 'LP'"
        df = pd.read_sql_query(query, conn)
        if df.empty:
            raise ValueError("No site index bounds found for LP")
        si_min = df.iloc[0]['si_min']
        si_max = df.iloc[0]['si_max']
    
    # Create plot
    plt.figure(figsize=(12, 8))
    
    # Test different site indices
    si_values = [
        si_min,
        si_min + (si_max - si_min) * 0.25,
        si_min + (si_max - si_min) * 0.5,
        si_min + (si_max - si_min) * 0.75,
        si_max
    ]
    
    ages = np.arange(2, 21, 1)  # Ages from 2 to 20 years
    initial_height = 10.0
    
    for si in si_values:
        heights = []
        current_height = initial_height
        
        for age in ages:
            current_height = calculate_small_tree_height_growth(
                si=si,
                aget=age,
                c1=coeffs['small_tree_b0'],
                c2=coeffs['small_tree_b1'],
                c3=coeffs['small_tree_b2'],
                c4=coeffs['small_tree_b3'],
                c5=coeffs['small_tree_b4'],
                ht=current_height,
                random_error_sd=0.0  # Disable random error for smooth curves
            )
            heights.append(current_height)
        
        plt.plot(ages, heights, label=f'SI={si:.0f}')
    
    plt.title('Small Tree Height Growth Trajectories\nLoblolly Pine at Different Site Indices')
    plt.xlabel('Age (years)')
    plt.ylabel('Height (feet)')
    plt.grid(True)
    plt.legend(title='Site Index', loc='upper left')
    
    # Save the plot
    plt.savefig(PLOTS_DIR / 'small_tree_growth_trajectories.png')
    plt.close()

def test_plot_initial_height_effect():
    """Generate plots showing growth patterns with different initial heights."""
    # Get coefficients from database
    with sqlite3.connect('data/sqlite_databases/fvspy.db') as conn:
        # Get small tree growth coefficients for Loblolly Pine
        query = "SELECT * FROM small_tree_growth WHERE species_code = 'LP'"
        df = pd.read_sql_query(query, conn)
        if df.empty:
            raise ValueError("No small tree growth coefficients found for LP")
        coeffs = df.iloc[0]
        
        # Get site index bounds
        query = "SELECT si_min, si_max FROM site_index_range WHERE species_code = 'LP'"
        df = pd.read_sql_query(query, conn)
        if df.empty:
            raise ValueError("No site index bounds found for LP")
        si_min = df.iloc[0]['si_min']
        si_max = df.iloc[0]['si_max']
    
    # Create plot
    plt.figure(figsize=(12, 8))
    
    # Use middle of SI range
    si = si_min + (si_max - si_min) / 2
    
    # Test different initial heights
    initial_heights = [5.0, 10.0, 15.0, 20.0]
    ages = np.arange(2, 21, 1)  # Ages from 2 to 20 years
    
    for initial_height in initial_heights:
        heights = []
        current_height = initial_height
        
        for age in ages:
            current_height = calculate_small_tree_height_growth(
                si=si,
                aget=age,
                c1=coeffs['small_tree_b0'],
                c2=coeffs['small_tree_b1'],
                c3=coeffs['small_tree_b2'],
                c4=coeffs['small_tree_b3'],
                c5=coeffs['small_tree_b4'],
                ht=current_height,
                random_error_sd=0.0  # Disable random error for smooth curves
            )
            heights.append(current_height)
        
        plt.plot(ages, heights, label=f'Initial Height={initial_height:.1f} ft')
    
    plt.title(f'Small Tree Height Growth Patterns\nLoblolly Pine at SI={si:.0f}')
    plt.xlabel('Age (years)')
    plt.ylabel('Height (feet)')
    plt.grid(True)
    plt.legend(title='Initial Height', loc='upper left')
    
    # Save the plot
    plt.savefig(PLOTS_DIR / 'small_tree_initial_height_effect.png')
    plt.close()

def test_plot_age_effect():
    """Generate plots showing the effect of age on height growth across yellow pine species."""
    species_list = ['LP', 'SA', 'SP', 'LL']  # Loblolly, Slash, Shortleaf, Longleaf
    species_names = {
        'LP': 'Loblolly Pine',
        'SA': 'Slash Pine',
        'SP': 'Shortleaf Pine',
        'LL': 'Longleaf Pine'
    }
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Process each species
    for species_code in species_list:
        # Get coefficients from database
        with sqlite3.connect('data/sqlite_databases/fvspy.db') as conn:
            # Get small tree growth coefficients
            query = "SELECT * FROM small_tree_growth WHERE species_code = ?"
            df = pd.read_sql_query(query, conn, params=(species_code,))
            if df.empty:
                print(f"Warning: No small tree growth coefficients found for {species_code}")
                continue
            coeffs = df.iloc[0]
            
            # Get site index bounds
            query = "SELECT si_min, si_max FROM site_index_range WHERE species_code = ?"
            df = pd.read_sql_query(query, conn, params=(species_code,))
            if df.empty:
                print(f"Warning: No site index bounds found for {species_code}")
                continue
            si_min = df.iloc[0]['si_min']
            si_max = df.iloc[0]['si_max']
        
        # Use middle of SI range
        si = si_min + (si_max - si_min) / 2
        initial_height = 10.0
        
        # Calculate growth rates at different ages
        ages = np.arange(2, 21, 1)  # Ages from 2 to 20 years
        heights = [initial_height]  # Start with initial height
        growth_rates = []
        
        current_height = initial_height
        for age in ages[:-1]:  # Go up to second-to-last age
            next_height = calculate_small_tree_height_growth(
                si=si,
                aget=age,
                c1=coeffs['small_tree_b0'],
                c2=coeffs['small_tree_b1'],
                c3=coeffs['small_tree_b2'],
                c4=coeffs['small_tree_b3'],
                c5=coeffs['small_tree_b4'],
                ht=current_height,
                random_error_sd=0.0  # Disable random error for smooth curves
            )
            growth_rate = (next_height - current_height) / 5  # 5-year growth rate converted to annual
            growth_rates.append(growth_rate)
            heights.append(next_height)
            current_height = next_height
        
        # Plot growth rates
        ax1.plot(ages[:-1], growth_rates, '-o', label=species_names[species_code])
        
        # Plot cumulative height
        ax2.plot(ages, heights, '-o', label=species_names[species_code])
    
    ax1.set_title('Annual Height Growth Rate\nYellow Pine Species Comparison')
    ax1.set_xlabel('Age (years)')
    ax1.set_ylabel('Annual Height Growth (feet/year)')
    ax1.grid(True)
    ax1.legend(title='Species', loc='upper right')
    
    # Add explanatory text to growth rate plot
    ax1.text(0.02, 0.98, 
            'Growth rates shown are average annual rates\nover a 5-year growth period',
            transform=ax1.transAxes,
            verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.8))
    
    ax2.set_title('Cumulative Height Growth\nYellow Pine Species Comparison')
    ax2.set_xlabel('Age (years)')
    ax2.set_ylabel('Height (feet)')
    ax2.grid(True)
    ax2.legend(title='Species', loc='upper left')
    
    # Add note about site index
    fig.text(0.5, 0.02, 
             'Note: Each species uses the middle of its respective site index range',
             ha='center', fontsize=10)
    
    plt.tight_layout()
    # Save the plot
    plt.savefig(PLOTS_DIR / 'small_tree_age_effect.png')
    plt.close() 
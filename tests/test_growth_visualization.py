"""
Visualization tests for the growth module.
These tests generate plots to visually inspect height-diameter relationships.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from fvs_core.growth import curtis_arney_height, wykoff_height, species_data

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
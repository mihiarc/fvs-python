"""
Visualization tests for bark ratio relationships.
These tests generate plots to visually inspect bark ratio patterns.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from fvs_core.growth import calculate_inside_bark_dbh_ratio, species_data

# Ensure plots directory exists
PLOTS_DIR = Path(__file__).parent / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)

def test_plot_bark_ratio_curves():
    """Generate plots comparing bark ratio relationships for different species."""
    # Select a few representative species
    species_list = ['FR', 'JU', 'PI']  # Fraser Fir, Juniper, Pine
    dbh_values = np.linspace(1, 30, 100)  # DBH range from 1 to 30 inches
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    for species in species_list:
        ratios = [calculate_inside_bark_dbh_ratio(dbh, species) for dbh in dbh_values]
        plt.plot(dbh_values, ratios, label=f'{species}')
    
    plt.title('Bark Ratio vs DBH by Species')
    plt.xlabel('DBH (inches)')
    plt.ylabel('Inside Bark to Outside Bark Ratio')
    plt.grid(True)
    plt.legend()
    
    # Save the plot
    plt.savefig(PLOTS_DIR / 'bark_ratio_curves.png')
    plt.close()

def test_plot_bark_ratio_bounds():
    """Generate plots showing the bounding behavior of bark ratios."""
    species = 'FR'  # Use Fraser Fir as an example
    dbh_values = np.linspace(0.1, 50, 200)  # Wide range of DBH values
    
    # Calculate ratios
    ratios = [calculate_inside_bark_dbh_ratio(dbh, species) for dbh in dbh_values]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(dbh_values, ratios, label='Bark ratio')
    plt.axhline(y=0.80, color='r', linestyle='--', label='Lower bound (0.80)')
    plt.axhline(y=0.99, color='g', linestyle='--', label='Upper bound (0.99)')
    
    plt.title(f'Bark Ratio Bounds for {species}')
    plt.xlabel('DBH (inches)')
    plt.ylabel('Inside Bark to Outside Bark Ratio')
    plt.grid(True)
    plt.legend()
    
    # Save the plot
    plt.savefig(PLOTS_DIR / 'bark_ratio_bounds.png')
    plt.close()

def test_plot_species_comparison():
    """Generate a plot comparing bark ratios across multiple species."""
    # Get species with valid bark coefficients
    valid_species = [sp for sp in species_data.keys() 
                    if not np.isnan(species_data[sp]['Bark_b0'])][:5]
    dbh = 10.0  # Fixed DBH for comparison
    
    # Calculate ratios for each species
    ratios = {sp: calculate_inside_bark_dbh_ratio(dbh, sp) for sp in valid_species}
    
    # Create bar plot
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(ratios)), list(ratios.values()))
    plt.xticks(range(len(ratios)), list(ratios.keys()), rotation=45)
    
    plt.title(f'Bark Ratio Comparison at DBH = {dbh} inches')
    plt.xlabel('Species')
    plt.ylabel('Inside Bark to Outside Bark Ratio')
    plt.grid(True, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(ratios.values()):
        plt.text(i, v, f'{v:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'species_comparison.png')
    plt.close()

def test_plot_coefficient_sensitivity():
    """Generate plots showing sensitivity to coefficient changes."""
    base_coeffs = {
        'Bark_b0': 0.05119,  # Using FR coefficients as base
        'Bark_b1': 0.89372
    }
    
    dbh_values = np.linspace(1, 30, 100)
    variations = [-0.1, 0, 0.1]  # -10%, base, +10%
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Test sensitivity to b0
    for var in variations:
        coeffs = base_coeffs.copy()
        coeffs['Bark_b0'] = base_coeffs['Bark_b0'] * (1 + var)
        ratios = [calculate_inside_bark_dbh_ratio(dbh, 'TEST', coeffs) for dbh in dbh_values]
        ax1.plot(dbh_values, ratios, 
                label=f'b0 {"-10%" if var<0 else "+10%" if var>0 else "base"}')
    
    ax1.set_title('Sensitivity to b0')
    ax1.set_xlabel('DBH (inches)')
    ax1.set_ylabel('Inside Bark to Outside Bark Ratio')
    ax1.grid(True)
    ax1.legend()
    
    # Test sensitivity to b1
    for var in variations:
        coeffs = base_coeffs.copy()
        coeffs['Bark_b1'] = base_coeffs['Bark_b1'] * (1 + var)
        ratios = [calculate_inside_bark_dbh_ratio(dbh, 'TEST', coeffs) for dbh in dbh_values]
        ax2.plot(dbh_values, ratios, 
                label=f'b1 {"-10%" if var<0 else "+10%" if var>0 else "base"}')
    
    ax2.set_title('Sensitivity to b1')
    ax2.set_xlabel('DBH (inches)')
    ax2.set_ylabel('Inside Bark to Outside Bark Ratio')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'coefficient_sensitivity.png')
    plt.close() 
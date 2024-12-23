"""
Tests for crown ratio visualizations.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from fvs_core.crown_ratio import (
    calculate_dubbed_crown_ratio,
    calculate_acr,
    calculate_crown_ratio_weibull,
    calculate_weibull_parameters,
    calculate_scale
)

def test_plot_crown_ratio_curves():
    """
    Test plotting crown ratio curves for different species.
    Expected pattern: Crown ratio should decrease with increasing stand density (RelSDI)
    because trees in denser stands compete more for light and have smaller crowns.
    """
    plt.figure(figsize=(10, 6))
    
    # Test species with different equation types
    species_list = ['FR', 'JU', 'PI']  # Fraser Fir, Juniper, Pine
    species_names = ['Fraser Fir', 'Juniper', 'Pine']
    colors = ['b', 'g', 'r']
    
    # Generate x values (relative SDI from low to high density)
    relsdi_values = np.linspace(1, 12, 100)
    
    for species, name, color in zip(species_list, species_names, colors):
        acr_values = [calculate_acr(relsdi, species) for relsdi in relsdi_values]
        plt.plot(relsdi_values, acr_values, color=color, label=name)
    
    plt.xlabel('Relative Stand Density Index (RelSDI)')
    plt.ylabel('Average Crown Ratio')
    plt.title('Crown Ratio Response to Stand Density by Species')
    plt.legend()
    plt.grid(True)
    
    # Add explanatory text
    plt.text(0.02, 0.02, 
             'Expected pattern: Crown ratios decrease with increasing density\n' +
             'as trees compete more for light in denser stands.',
             transform=plt.gca().transAxes, fontsize=8, 
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig('crown_ratio_curves.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_plot_weibull_distribution():
    """
    Test plotting Weibull distribution for crown ratios.
    Expected pattern: Larger trees (higher percentile) should have larger crown ratios,
    and the relationship should follow a sigmoid-like curve due to the Weibull distribution.
    """
    plt.figure(figsize=(10, 6))
    
    # Test parameters for Fraser Fir
    a0, b0, b1, c0 = 406.59, -687.08, 105.10, 4.1741
    scale = 0.8  # Moderate stand density
    
    # Calculate parameters for different ACR values
    acr_values = [0.3, 0.5, 0.7]  # Low, medium, high average crown ratios
    colors = ['b', 'g', 'r']
    x = np.linspace(0.05, 0.95, 100)  # Tree rank percentile
    
    for acr, color in zip(acr_values, colors):
        a, b, c = calculate_weibull_parameters(acr, a0, b0, b1, c0)
        cr_values = [calculate_crown_ratio_weibull(xi, a, b, c, scale) for xi in x]
        plt.plot(x, cr_values, color=color, 
                label=f'Stand Average CR = {acr:.1f}')
    
    plt.xlabel('Tree Rank (0=smallest, 1=largest)')
    plt.ylabel('Individual Tree Crown Ratio')
    plt.title('Crown Ratio Distribution by Tree Size')
    plt.legend()
    plt.grid(True)
    
    # Add explanatory text
    plt.text(0.02, 0.02,
             'Expected pattern: Larger trees (higher rank) have larger crown ratios\n' +
             'Different curves show stands with different average crown ratios',
             transform=plt.gca().transAxes, fontsize=8,
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig('crown_ratio_weibull.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_plot_density_effects():
    """
    Test plotting density effects on crown ratios.
    Expected pattern: Higher CCF (denser stands) should result in smaller crown ratios
    across all tree ranks, but especially for smaller trees.
    """
    plt.figure(figsize=(10, 6))
    
    # Test parameters for Fraser Fir
    a0, b0, b1, c0 = 406.59, -687.08, 105.10, 4.1741
    
    # Test different CCF values (stand densities)
    ccf_values = [50, 100, 150, 200]  # Open to very dense
    ccf_labels = ['Open (CCF=50)', 'Medium (CCF=100)', 
                 'Dense (CCF=150)', 'Very Dense (CCF=200)']
    colors = ['g', 'b', 'orange', 'r']
    x = np.linspace(0.05, 0.95, 100)  # Tree rank percentile
    
    for ccf, label, color in zip(ccf_values, ccf_labels, colors):
        # Calculate ACR based on density
        relsdi = ccf / 10.0  # Approximate conversion
        acr = calculate_acr(relsdi, 'FR')
        
        # Calculate Weibull parameters
        a, b, c = calculate_weibull_parameters(acr, a0, b0, b1, c0)
        
        # Calculate crown ratios with density scaling
        scale = calculate_scale(ccf)
        cr_values = [calculate_crown_ratio_weibull(xi, a, b, c, scale) for xi in x]
        plt.plot(x, cr_values, color=color, label=label)
    
    plt.xlabel('Tree Rank (0=smallest, 1=largest)')
    plt.ylabel('Crown Ratio')
    plt.title('Effect of Stand Density on Crown Ratios')
    plt.legend()
    plt.grid(True)
    
    # Add explanatory text
    plt.text(0.02, 0.02,
             'Expected pattern: Denser stands (higher CCF) have smaller crown ratios\n' +
             'Effect is stronger on smaller trees (lower rank)',
             transform=plt.gca().transAxes, fontsize=8,
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig('crown_ratio_density.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_plot_dubbed_crown_ratios():
    """
    Test plotting dubbed crown ratios for dead trees.
    Expected pattern: Crown ratio should decrease with DBH up to 24 inches,
    then level off. Higher SD values should show more variation.
    """
    plt.figure(figsize=(10, 6))
    
    # Generate DBH values
    dbh_values = np.linspace(0, 40, 100)
    
    # Calculate dubbed crown ratios for different standard deviations
    sd_values = [0.05, 0.1, 0.2]
    sd_labels = ['Low Variation (SD=0.05)', 
                'Medium Variation (SD=0.1)',
                'High Variation (SD=0.2)']
    colors = ['b', 'g', 'r']
    
    for sd, label, color in zip(sd_values, sd_labels, colors):
        np.random.seed(42)  # For reproducibility
        cr_values = [calculate_dubbed_crown_ratio(dbh, sd) for dbh in dbh_values]
        plt.plot(dbh_values, cr_values, color=color, label=label)
    
    plt.axvline(x=24, color='k', linestyle='--', label='DBH Threshold (24 in)')
    plt.xlabel('DBH (inches)')
    plt.ylabel('Dubbed Crown Ratio')
    plt.title('Dubbed Crown Ratios for Dead Trees')
    plt.legend()
    plt.grid(True)
    
    # Add explanatory text
    plt.text(0.02, 0.02,
             'Expected pattern: Crown ratio decreases with DBH up to 24 inches\n' +
             'then levels off. Higher SD values show more random variation.',
             transform=plt.gca().transAxes, fontsize=8,
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig('dubbed_crown_ratios.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_plot_parameter_sensitivity():
    """
    Test plotting sensitivity to Weibull parameters.
    This test is less relevant for users and more for debugging/validation.
    Consider removing or moving to a separate diagnostic module.
    """
    pass  # Removing this test as it's less relevant for understanding the model 
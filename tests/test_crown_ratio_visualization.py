"""
Tests for crown ratio visualizations.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from fvs_core import data_handling
from fvs_core.crown_ratio import (
    calculate_dubbed_crown_ratio,
    calculate_acr,
    calculate_crown_ratio_weibull,
    calculate_weibull_parameters,
    calculate_scale
)

# Ensure test output directory exists
output_dir = Path(__file__).parent / 'test_output'
output_dir.mkdir(exist_ok=True)

# Southern yellow pine species codes and names
PINE_SPECIES = {
    'SP': 'Shortleaf Pine',
    'SA': 'Slash Pine',
    'LL': 'Longleaf Pine',
    'LP': 'Loblolly Pine'
}

def test_plot_crown_ratio_curves():
    """
    Test plotting crown ratio curves for different species.
    Expected pattern: Crown ratio should decrease with increasing stand density (RelSDI)
    because trees in denser stands compete more for light and have smaller crowns.
    """
    plt.figure(figsize=(10, 6))
    
    # Use southern yellow pines
    species_list = []
    for species in PINE_SPECIES.keys():
        try:
            # Test if we can calculate ACR for this species
            test_acr = calculate_acr(5.0, species)  # Test with middle RelSDI value
            if test_acr is not None:
                species_list.append(species)
        except (KeyError, ValueError) as e:
            print(f"Warning: Species {species} not available: {e}")
            continue
    
    if not species_list:
        pytest.skip("No southern pine species found in crown ratio data")
    
    species_names = [PINE_SPECIES[code] for code in species_list]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Distinct colors
    
    # Generate x values (relative SDI from low to high density)
    relsdi_values = np.linspace(2, 10, 100)  # More realistic range for managed stands
    
    for species, name, color in zip(species_list, species_names, colors):
        acr_values = []
        for relsdi in relsdi_values:
            try:
                acr = calculate_acr(relsdi, species)
                acr_values.append(acr)
            except (ValueError, KeyError) as e:
                print(f"Error calculating ACR for {name} at RelSDI {relsdi}: {e}")
                continue
        
        if acr_values:
            plt.plot(relsdi_values[:len(acr_values)], acr_values, color=color, label=name)
            print(f"{name} ACR range: {min(acr_values):.3f} to {max(acr_values):.3f}")
    
    plt.xlabel('Relative Stand Density Index (RelSDI)')
    plt.ylabel('Average Crown Ratio')
    plt.title('Crown Ratio Response to Stand Density\nSouthern Yellow Pines')
    plt.legend()
    plt.grid(True)
    
    # Add explanatory text
    plt.text(0.02, 0.02, 
             'Expected pattern: Crown ratios decrease with increasing density\n' +
             'as trees compete more for light in denser stands.',
             transform=plt.gca().transAxes, fontsize=8, 
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig(output_dir / 'crown_ratio_curves.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_plot_weibull_distribution():
    """
    Test plotting Weibull distribution for crown ratios.
    Expected pattern: Larger trees (higher percentile) should have larger crown ratios,
    and the relationship should follow a sigmoid-like curve due to the Weibull distribution.
    """
    plt.figure(figsize=(12, 8))
    
    # Use Loblolly Pine as the representative species
    species = 'LP'
    if species not in data_handling.species_crown_ratio_data:
        pytest.skip(f"{PINE_SPECIES[species]} not found in crown ratio data")
    
    # Use wider range of CCF values to better show density effect
    ccf_values = [75, 125, 175]  # Open, Dense, Very Dense
    scale_values = [calculate_scale(ccf) for ccf in ccf_values]
    
    # Calculate ACR based on approximate RelSDI from CCF
    relsdi_values = [ccf/10.0 for ccf in ccf_values]  # Approximate conversion from CCF to RelSDI
    acr_values = [calculate_acr(relsdi, species) for relsdi in relsdi_values]
    
    # Use a color map for better visualization of density gradient
    colors = plt.cm.viridis(np.linspace(0, 1, len(ccf_values)))
    x = np.linspace(0.05, 0.95, 100)  # Tree rank percentile
    
    for ccf, relsdi, scale, acr, color in zip(ccf_values, relsdi_values, scale_values, acr_values, colors):
        cr_values = []
        for xi in x:
            try:
                cr = calculate_crown_ratio_weibull(xi, species, acr, scale)
                cr_values.append(cr)
            except ValueError as e:
                print(f"Error calculating crown ratio at x={xi}, CCF={ccf}: {e}")
                cr_values.append(None)
        
        if any(cr_values):
            valid_x = [x[i] for i, cr in enumerate(cr_values) if cr is not None]
            valid_cr = [cr for cr in cr_values if cr is not None]
            plt.plot(valid_x, valid_cr, color=color, linewidth=2,
                    label=f'CCF={ccf} (RelSDI={relsdi:.1f}, Scale={scale:.2f}, ACR={acr:.3f})')
            print(f"CCF {ccf}: CR range {min(valid_cr):.3f} to {max(valid_cr):.3f}")
    
    plt.xlabel('Tree Rank Percentile (0=smallest, 1=largest)', fontsize=10)
    plt.ylabel('Individual Tree Crown Ratio (proportion)', fontsize=10)
    plt.title(f'Crown Ratio Distribution by Tree Size and Stand Density\n{PINE_SPECIES[species]}', 
             fontsize=12, pad=20)
    
    # Move legend inside plot area (top left) with increased font size
    plt.legend(title='Stand Density Parameters:', 
              loc='upper left',
              fontsize=11,
              title_fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Move explanatory text to bottom right with increased font size
    plt.text(0.98, 0.02,
             'Parameters:\n' +
             '- CCF: Crown Competition Factor (measure of stand density)\n' +
             '- RelSDI: Relative Stand Density Index (CCF/10)\n' +
             '- Scale: Density adjustment factor = 1 - 0.00167(CCF-100)\n' +
             '- ACR: Average Crown Ratio (function of RelSDI)',
             fontsize=10, bbox=dict(facecolor='white', alpha=0.8),
             transform=plt.gca().transAxes,
             horizontalalignment='right',
             verticalalignment='bottom')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'crown_ratio_weibull.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_plot_density_effects():
    """
    Test plotting density effects on crown ratios.
    Expected pattern: Higher CCF (denser stands) should result in smaller crown ratios
    across all tree ranks, but especially for smaller trees.
    """
    plt.figure(figsize=(10, 6))
    
    # Use Shortleaf Pine as the representative species
    species = 'SP'
    if species not in data_handling.species_crown_ratio_data:
        pytest.skip(f"{PINE_SPECIES[species]} not found in crown ratio data")
    
    # Test different CCF values (stand densities)
    ccf_values = [50, 100, 150, 200]  # Open to very dense
    ccf_labels = ['Open (CCF=50)', 'Medium (CCF=100)', 
                 'Dense (CCF=150)', 'Very Dense (CCF=200)']
    colors = ['g', 'b', 'orange', 'r']
    x = np.linspace(0.05, 0.95, 100)  # Tree rank percentile
    
    for ccf, label, color in zip(ccf_values, ccf_labels, colors):
        # Calculate ACR based on density
        relsdi = ccf / 10.0  # Approximate conversion
        acr = calculate_acr(relsdi, species)
        
        # Calculate crown ratios with density scaling
        scale = calculate_scale(ccf)
        cr_values = []
        for xi in x:
            try:
                cr = calculate_crown_ratio_weibull(xi, species, acr, scale)
                cr_values.append(cr)
            except ValueError as e:
                print(f"Error calculating crown ratio at x={xi}, CCF={ccf}: {e}")
                cr_values.append(None)
        
        if any(cr_values):
            valid_x = [x[i] for i, cr in enumerate(cr_values) if cr is not None]
            valid_cr = [cr for cr in cr_values if cr is not None]
            plt.plot(valid_x, valid_cr, color=color, 
                    label=f'{label} (scale={scale:.2f})')
            print(f"CCF {ccf}: CR range {min(valid_cr):.3f} to {max(valid_cr):.3f}")
    
    plt.xlabel('Tree Rank (0=smallest, 1=largest)')
    plt.ylabel('Crown Ratio')
    plt.title(f'Effect of Stand Density on Crown Ratios\n{PINE_SPECIES[species]}')
    plt.legend()
    plt.grid(True)
    
    # Add explanatory text
    plt.text(0.02, 0.02,
             'Expected pattern: Denser stands (higher CCF) have smaller crown ratios\n' +
             'Effect is stronger on smaller trees (lower rank)',
             transform=plt.gca().transAxes, fontsize=8,
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.savefig(output_dir / 'crown_ratio_density.png', dpi=300, bbox_inches='tight')
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
    
    plt.savefig(output_dir / 'dubbed_crown_ratios.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_plot_parameter_sensitivity():
    """
    Test plotting sensitivity to Weibull parameters.
    This test is less relevant for users and more for debugging/validation.
    Consider removing or moving to a separate diagnostic module.
    """
    pass  # Removing this test as it's less relevant for understanding the model 
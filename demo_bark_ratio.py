#!/usr/bin/env python3
"""
Demo script showing how to use the bark ratio module.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from src.fvs_python.bark_ratio import (
    create_bark_ratio_model, 
    calculate_dib_from_dob, 
    calculate_bark_ratio,
    compare_bark_ratios
)

def main():
    print("FVS-Python Bark Ratio Module Demo")
    print("=" * 50)
    
    # Example 1: Basic usage for a single species
    print("\n1. Basic Usage - Loblolly Pine (LP)")
    print("-" * 30)
    
    # Create a bark ratio model for loblolly pine
    lp_model = create_bark_ratio_model("LP")
    
    # Convert outside bark diameter to inside bark
    dob = 12.5  # inches
    dib = lp_model.calculate_dib_from_dob(dob)
    bark_ratio = lp_model.calculate_bark_ratio(dob)
    bark_thickness = lp_model.calculate_bark_thickness(dob)
    
    print(f"Tree with DOB = {dob} inches:")
    print(f"  DIB = {dib:.2f} inches")
    print(f"  Bark ratio = {bark_ratio:.3f}")
    print(f"  Bark thickness = {bark_thickness:.3f} inches")
    
    # Example 2: Using standalone functions
    print("\n2. Standalone Functions")
    print("-" * 30)
    
    species = "SA"  # Slash pine
    dob = 15.0
    
    dib = calculate_dib_from_dob(species, dob)
    ratio = calculate_bark_ratio(species, dob)
    
    print(f"{species} with DOB = {dob} inches:")
    print(f"  DIB = {dib:.2f} inches")
    print(f"  Bark ratio = {ratio:.3f}")
    
    # Example 3: Compare multiple species
    print("\n3. Species Comparison")
    print("-" * 30)
    
    species_list = ["LP", "SP", "SA", "LL"]
    dob_values = [8.0, 12.0, 16.0, 20.0]
    
    comparison = compare_bark_ratios(species_list, dob_values)
    
    print("Species comparison for different diameters:")
    print("DOB (in)  LP     SP     SA     LL")
    print("-" * 35)
    
    for i, dob in enumerate(dob_values):
        line = f"{dob:6.1f}  "
        for species in species_list:
            ratio = comparison['species_results'][species]['bark_ratio'][i]
            line += f"{ratio:.3f}  "
        print(line)
    
    # Example 4: Practical application - volume calculations
    print("\n4. Practical Application - Volume Calculations")
    print("-" * 50)
    
    print("Converting field measurements (outside bark) to volume calculations (inside bark):")
    
    # Simulate field measurements
    field_trees = [
        {"species": "LP", "dbh_ob": 10.5, "height": 65},
        {"species": "SP", "dbh_ob": 8.2, "height": 55},
        {"species": "SA", "dbh_ob": 14.8, "height": 78},
    ]
    
    print("Tree  Species  DBH_OB  DBH_IB  Height  Volume_IB")
    print("-" * 50)
    
    for i, tree in enumerate(field_trees, 1):
        model = create_bark_ratio_model(tree["species"])
        dbh_ib = model.apply_bark_ratio_to_dbh(tree["dbh_ob"])
        
        # Simple volume calculation using inside bark diameter
        # Volume = π * (DBH_IB/24)² * Height * Form_Factor
        form_factor = 0.48
        basal_area_ib = 3.14159 * (dbh_ib / 24) ** 2
        volume_ib = basal_area_ib * tree["height"] * form_factor
        
        print(f"{i:4d}  {tree['species']:7s}  {tree['dbh_ob']:6.1f}  {dbh_ib:6.2f}  {tree['height']:6.0f}  {volume_ib:8.1f}")
    
    print("\nNote: Volume calculations use inside bark diameter as required by FVS standards.")
    
    # Example 5: Visualization plots
    print("\n5. Visualization Plots")
    print("-" * 30)
    
    create_bark_ratio_plots()
    print("Bark ratio plots saved to test_output/ directory")


def create_bark_ratio_plots():
    """Create visualization plots for bark ratio relationships."""
    # Create test_output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Define species and diameter range for plotting
    species_list = ["LP", "SP", "SA", "LL", "FR", "BY", "WO", "SU"]
    species_names = {
        "LP": "Loblolly Pine",
        "SP": "Shortleaf Pine", 
        "SA": "Slash Pine",
        "LL": "Longleaf Pine",
        "FR": "Fraser Fir",
        "BY": "Bald Cypress",
        "WO": "White Oak",
        "SU": "Sweetgum"
    }
    
    dob_range = np.linspace(2, 24, 50)  # 2 to 24 inches
    
    # Plot 1: Bark Ratio vs DOB for multiple species
    plt.figure(figsize=(12, 8))
    
    for species in species_list:
        try:
            model = create_bark_ratio_model(species)
            bark_ratios = [model.calculate_bark_ratio(dob) for dob in dob_range]
            plt.plot(dob_range, bark_ratios, label=f"{species} - {species_names.get(species, species)}", linewidth=2)
        except Exception as e:
            print(f"Warning: Could not plot {species}: {e}")
    
    plt.xlabel('Diameter Outside Bark (inches)', fontsize=12)
    plt.ylabel('Bark Ratio (DIB/DOB)', fontsize=12)
    plt.title('Bark Ratio Relationships by Species\n(SN Southern Variant - Clark 1991)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.ylim(0.75, 1.0)
    plt.tight_layout()
    plt.savefig(output_dir / 'bark_ratio_by_species.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 2: DIB vs DOB comparison
    plt.figure(figsize=(12, 8))
    
    # Plot perfect correlation line (DIB = DOB)
    plt.plot(dob_range, dob_range, 'k--', alpha=0.5, label='Perfect correlation (DIB = DOB)')
    
    for species in species_list[:4]:  # Limit to 4 species for clarity
        try:
            model = create_bark_ratio_model(species)
            dib_values = [model.calculate_dib_from_dob(dob) for dob in dob_range]
            plt.plot(dob_range, dib_values, label=f"{species} - {species_names.get(species, species)}", linewidth=2)
        except Exception as e:
            print(f"Warning: Could not plot {species}: {e}")
    
    plt.xlabel('Diameter Outside Bark (inches)', fontsize=12)
    plt.ylabel('Diameter Inside Bark (inches)', fontsize=12)
    plt.title('Diameter Inside Bark vs Outside Bark\n(Selected Pine Species)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'dib_vs_dob_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 3: Bark thickness by species
    plt.figure(figsize=(12, 8))
    
    for species in species_list:
        try:
            model = create_bark_ratio_model(species)
            bark_thickness = [model.calculate_bark_thickness(dob) for dob in dob_range]
            plt.plot(dob_range, bark_thickness, label=f"{species} - {species_names.get(species, species)}", linewidth=2)
        except Exception as e:
            print(f"Warning: Could not plot {species}: {e}")
    
    plt.xlabel('Diameter Outside Bark (inches)', fontsize=12)
    plt.ylabel('Bark Thickness (inches)', fontsize=12)
    plt.title('Bark Thickness by Species\n(Radius difference: (DOB - DIB) / 2)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(output_dir / 'bark_thickness_by_species.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 4: Coefficient comparison bar chart
    plt.figure(figsize=(14, 8))
    
    coefficients_data = {"species": [], "b1": [], "b2": []}
    
    for species in species_list:
        try:
            model = create_bark_ratio_model(species)
            coeffs = model.get_species_coefficients()
            coefficients_data["species"].append(f"{species}\n{species_names.get(species, species)}")
            coefficients_data["b1"].append(coeffs["b1"])
            coefficients_data["b2"].append(coeffs["b2"])
        except Exception as e:
            print(f"Warning: Could not get coefficients for {species}: {e}")
    
    x = np.arange(len(coefficients_data["species"]))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # B1 coefficients
    bars1 = ax1.bar(x, coefficients_data["b1"], width, label='b1 (Intercept)', color='skyblue', alpha=0.8)
    ax1.set_xlabel('Species', fontsize=12)
    ax1.set_ylabel('b1 Coefficient', fontsize=12)
    ax1.set_title('Bark Ratio Equation Coefficients: b1 (Intercept)', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(coefficients_data["species"], rotation=45, ha='right')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    # B2 coefficients
    bars2 = ax2.bar(x, coefficients_data["b2"], width, label='b2 (Slope)', color='lightcoral', alpha=0.8)
    ax2.set_xlabel('Species', fontsize=12)
    ax2.set_ylabel('b2 Coefficient', fontsize=12)
    ax2.set_title('Bark Ratio Equation Coefficients: b2 (Slope)', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(coefficients_data["species"], rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Perfect correlation (b2=1.0)')
    ax2.legend()
    
    # Add value labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'bark_ratio_coefficients.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 5: Practical application - Volume impact
    plt.figure(figsize=(12, 8))
    
    # Calculate volume differences between using OB vs IB
    heights = [40, 60, 80]  # Different tree heights
    form_factor = 0.48
    
    for height in heights:
        volume_diff_percent = []
        for dob in dob_range:
            # Volume using outside bark (incorrect)
            vol_ob = np.pi * (dob / 24)**2 * height * form_factor
            
            # Volume using inside bark (correct) - use LP as example
            model = create_bark_ratio_model("LP")
            dib = model.calculate_dib_from_dob(dob)
            vol_ib = np.pi * (dib / 24)**2 * height * form_factor
            
            # Percent difference
            diff_percent = ((vol_ob - vol_ib) / vol_ib) * 100
            volume_diff_percent.append(diff_percent)
        
        plt.plot(dob_range, volume_diff_percent, label=f'Height = {height} ft', linewidth=2)
    
    plt.xlabel('Diameter Outside Bark (inches)', fontsize=12)
    plt.ylabel('Volume Overestimate (%)', fontsize=12)
    plt.title('Volume Calculation Error When Using Outside Bark Diameter\n(Loblolly Pine Example)', 
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'volume_calculation_impact.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    main() 
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

if __name__ == "__main__":
    main() 
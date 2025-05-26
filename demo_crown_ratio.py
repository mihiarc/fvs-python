#!/usr/bin/env python3

"""
Demonstration of the crown ratio module functionality.
Shows basic usage and model comparisons across species.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fvs_python.crown_ratio import create_crown_ratio_model, compare_crown_ratio_models

def main():
    print("FVS-Python Crown Ratio Module Demonstration")
    print("=" * 50)
    
    # Create models for different species
    species_list = ["LP", "SP", "WO", "RM", "CA", "AB"]
    
    print("\n1. Basic Crown Ratio Predictions")
    print("-" * 35)
    relsdi_values = [2.0, 5.0, 8.0, 11.0]
    
    for species in species_list:
        model = create_crown_ratio_model(species)
        print(f"\n{species} ({model.coefficients['acr_equation']}):")
        
        for relsdi in relsdi_values:
            acr = model.calculate_average_crown_ratio(relsdi)
            # Individual crown ratios for different tree sizes
            small_tree_cr = model.predict_individual_crown_ratio(0.2, relsdi)  # Small tree
            large_tree_cr = model.predict_individual_crown_ratio(0.8, relsdi)  # Large tree
            
            print(f"  RELSDI {relsdi:4.1f}: ACR={acr:.3f}, Small={small_tree_cr:.3f}, Large={large_tree_cr:.3f}")
    
    print("\n\n2. Dead Tree Crown Ratio Predictions")
    print("-" * 40)
    dbh_values = [5, 10, 15, 20, 25]
    
    model = create_crown_ratio_model("LP")
    print("DBH (inches) -> Crown Ratio")
    for dbh in dbh_values:
        cr = model.predict_dead_tree_crown_ratio(dbh, random_seed=42)
        print(f"  {dbh:2d}         -> {cr:.3f}")
    
    print("\n\n3. Regeneration Crown Ratio Predictions")
    print("-" * 45)
    pccf_values = [50, 100, 150, 200, 250]
    
    print("PCCF -> Crown Ratio")
    for pccf in pccf_values:
        cr = model.predict_regeneration_crown_ratio(pccf, random_seed=42)
        print(f"  {pccf:3d} -> {cr:.3f}")
    
    print("\n\n4. Crown Ratio Change with Bounds")
    print("-" * 35)
    current_cr = 0.6
    predicted_cr_values = [0.5, 0.7, 0.8, 0.9]
    height_growth = 3.0
    
    print(f"Current CR: {current_cr:.3f}, Height Growth: {height_growth} ft")
    print("Predicted CR -> Actual CR (Change)")
    
    for predicted_cr in predicted_cr_values:
        new_cr = model.update_crown_ratio_change(current_cr, predicted_cr, height_growth)
        change = new_cr - current_cr
        print(f"  {predicted_cr:.3f}       -> {new_cr:.3f} ({change:+.3f})")
    
    print("\n\n5. Species Comparison at Different Densities")
    print("-" * 50)
    
    # Compare models across species
    relsdi_range = [1.0, 3.0, 5.0, 8.0, 12.0]
    results = compare_crown_ratio_models(species_list, relsdi_range)
    
    print("Average Crown Ratio by Species and Density:")
    print("Species  ", end="")
    for relsdi in relsdi_range:
        print(f"RELSDI{relsdi:4.1f}", end="  ")
    print()
    print("-" * 60)
    
    for species in species_list:
        print(f"{species:7s}  ", end="")
        acr_values = results['species_results'][species]['average_crown_ratio']
        for acr in acr_values:
            print(f"{acr:8.3f}", end="  ")
        print()
    
    print("\n\n6. Weibull Parameter Comparison")
    print("-" * 35)
    
    print("Species  Equation    A      B      C")
    print("-" * 40)
    
    for species in species_list:
        model = create_crown_ratio_model(species)
        equation = model.coefficients['acr_equation']
        
        # Calculate Weibull parameters for moderate density
        acr = model.calculate_average_crown_ratio(5.0)
        A, B, C = model.calculate_weibull_parameters(acr)
        
        print(f"{species:7s}  {equation:8s}  {A:5.2f}  {B:5.2f}  {C:5.2f}")
    
    print("\n\n7. Crown Competition Factor Effects")
    print("-" * 40)
    
    model = create_crown_ratio_model("LP")
    ccf_values = [50, 100, 150, 200, 300]
    
    print("CCF -> Scale Factor")
    for ccf in ccf_values:
        scale = model.calculate_scale_factor(ccf)
        print(f"{ccf:3d} -> {scale:.3f}")
    
    print("\n" + "=" * 50)
    print("Crown Ratio Module Demonstration Complete!")
    print("\nKey Features Demonstrated:")
    print("• Species-specific crown ratio equations (4.3.1.3 - 4.3.1.7)")
    print("• Weibull-based individual tree crown ratio prediction")
    print("• Dead tree crown ratio estimation")
    print("• Regeneration crown ratio prediction")
    print("• Crown ratio change bounds checking")
    print("• Density-dependent scaling factors")
    print("• Multi-species model comparison")
    print("\nNote: This demo shows console output only.")
    print("For visualizations, see the test_output/ directory for other module plots.")

if __name__ == "__main__":
    main() 
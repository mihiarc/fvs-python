#!/usr/bin/env python3
"""
Demonstration of the height-diameter module functionality.
Shows basic usage and model comparisons.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fvs_python.height_diameter import create_height_diameter_model, compare_models

def main():
    print("FVS-Python Height-Diameter Module Demonstration")
    print("=" * 50)
    
    # Create models for different species
    species_list = ["LP", "SP", "WO", "RM"]
    
    print("\n1. Basic Height Predictions")
    print("-" * 30)
    dbh_values = [5, 10, 15, 20]
    
    for species in species_list:
        model = create_height_diameter_model(species)
        print(f"\n{species} (Loblolly Pine, Shortleaf Pine, White Oak, Red Maple):")
        
        for dbh in dbh_values:
            ca_height = model.curtis_arney_height(dbh)
            wy_height = model.wykoff_height(dbh)
            print(f"  DBH {dbh:2d}\" -> Curtis-Arney: {ca_height:5.1f}ft, Wykoff: {wy_height:5.1f}ft")
    
    print("\n\n2. Model Parameters")
    print("-" * 30)
    lp_model = create_height_diameter_model("LP")
    ca_params = lp_model.get_model_parameters("curtis_arney")
    wy_params = lp_model.get_model_parameters("wykoff")
    
    print("Loblolly Pine (LP) Parameters:")
    print(f"  Curtis-Arney: P2={ca_params['p2']:.2f}, P3={ca_params['p3']:.6f}, P4={ca_params['p4']:.6f}, Dbw={ca_params['dbw']:.1f}")
    print(f"  Wykoff: B1={wy_params['b1']:.4f}, B2={wy_params['b2']:.4f}")
    
    print("\n\n3. Inverse Calculation (Height -> DBH)")
    print("-" * 30)
    target_heights = [30, 50, 70, 90]
    
    for height in target_heights:
        dbh = lp_model.solve_dbh_from_height(height)
        predicted_height = lp_model.predict_height(dbh)
        print(f"  Target: {height}ft -> DBH: {dbh:.2f}\" -> Predicted: {predicted_height:.1f}ft")
    
    print("\n\n4. Species Comparison at DBH = 12 inches")
    print("-" * 30)
    test_dbh = 12.0
    
    for species in ["LP", "SP", "SA", "WO", "RM", "SU"]:
        try:
            model = create_height_diameter_model(species)
            height = model.predict_height(test_dbh)
            print(f"  {species}: {height:.1f} feet")
        except Exception as e:
            print(f"  {species}: Error - {e}")
    
    print("\n\n5. Model Comparison for Loblolly Pine")
    print("-" * 30)
    dbh_range = [1, 3, 5, 8, 12, 16, 20, 25]
    results = compare_models(dbh_range, "LP")
    
    print("DBH (in)  Curtis-Arney (ft)  Wykoff (ft)  Difference (ft)")
    print("-" * 55)
    for i, dbh in enumerate(results['dbh']):
        ca_h = results['curtis_arney'][i]
        wy_h = results['wykoff'][i]
        diff = ca_h - wy_h
        print(f"{dbh:8.0f}  {ca_h:14.1f}  {wy_h:11.1f}  {diff:12.1f}")
    
    print("\n\nDemonstration complete!")
    print("Note: This demo shows console output only.")
    print("For visualizations, see the test_output/ directory for other module plots.")

if __name__ == "__main__":
    main() 
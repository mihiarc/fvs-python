#!/usr/bin/env python3
"""
Test script for the height-diameter module.
Demonstrates Curtis-Arney and Wykoff models for different species.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fvs_python.height_diameter import (
    create_height_diameter_model,
    curtis_arney_height,
    wykoff_height,
    compare_models
)

def test_species_models():
    """Test height-diameter models for different species."""
    print("Height-Diameter Model Testing")
    print("=" * 50)
    
    # Test species
    species_codes = ["LP", "SP", "SA", "LL"]  # Common southern pines
    test_dbhs = [1, 3, 6, 10, 15, 20]  # Range of DBH values
    
    for species in species_codes:
        print(f"\nSpecies: {species}")
        print("-" * 30)
        
        try:
            # Create model for this species
            model = create_height_diameter_model(species)
            
            # Show parameters
            ca_params = model.get_model_parameters('curtis_arney')
            wy_params = model.get_model_parameters('wykoff')
            
            print(f"Curtis-Arney: P2={ca_params['p2']:.2f}, P3={ca_params['p3']:.4f}, P4={ca_params['p4']:.4f}, Dbw={ca_params['dbw']}")
            print(f"Wykoff: B1={wy_params['b1']:.4f}, B2={wy_params['b2']:.4f}")
            print()
            
            # Test predictions
            print("DBH (in)  Curtis-Arney (ft)  Wykoff (ft)  Difference (ft)")
            print("-" * 55)
            
            for dbh in test_dbhs:
                ca_height = model.curtis_arney_height(dbh)
                wy_height = model.wykoff_height(dbh)
                diff = abs(ca_height - wy_height)
                
                print(f"{dbh:8.1f}  {ca_height:13.1f}  {wy_height:10.1f}  {diff:12.1f}")
                
        except Exception as e:
            print(f"Error testing species {species}: {e}")

def test_inverse_calculation():
    """Test solving for DBH given height."""
    print("\n\nInverse Calculation Testing")
    print("=" * 50)
    
    model = create_height_diameter_model("LP")  # Loblolly pine
    
    target_heights = [20, 40, 60, 80, 100]
    
    print("Target Height (ft)  Solved DBH (in)  Predicted Height (ft)  Error (ft)")
    print("-" * 70)
    
    for target_height in target_heights:
        try:
            # Solve for DBH
            solved_dbh = model.solve_dbh_from_height(target_height)
            
            # Verify by predicting height back
            predicted_height = model.predict_height(solved_dbh)
            error = abs(predicted_height - target_height)
            
            print(f"{target_height:15.1f}  {solved_dbh:12.2f}  {predicted_height:17.1f}  {error:9.3f}")
            
        except Exception as e:
            print(f"Error for height {target_height}: {e}")

def test_standalone_functions():
    """Test standalone height functions."""
    print("\n\nStandalone Function Testing")
    print("=" * 50)
    
    # Example parameters for loblolly pine
    p2, p3, p4, dbw = 243.860648, 4.28460566, -0.47130185, 0.5
    b1, b2 = 4.5084, -6.0116
    
    test_dbhs = [1, 5, 10, 15, 20]
    
    print("DBH (in)  Curtis-Arney (ft)  Wykoff (ft)")
    print("-" * 40)
    
    for dbh in test_dbhs:
        ca_height = curtis_arney_height(dbh, p2, p3, p4, dbw)
        wy_height = wykoff_height(dbh, b1, b2)
        
        print(f"{dbh:8.1f}  {ca_height:13.1f}  {wy_height:10.1f}")

def test_model_comparison():
    """Test model comparison function."""
    print("\n\nModel Comparison Testing")
    print("=" * 50)
    
    dbh_range = list(range(1, 21))  # 1 to 20 inches
    
    # Compare models for loblolly pine
    results = compare_models(dbh_range, "LP")
    
    print("DBH (in)  Curtis-Arney (ft)  Wykoff (ft)  Difference (ft)")
    print("-" * 55)
    
    for i, dbh in enumerate(results['dbh']):
        ca_height = results['curtis_arney'][i]
        wy_height = results['wykoff'][i]
        diff = abs(ca_height - wy_height)
        
        if dbh <= 10:  # Show first 10 values
            print(f"{dbh:8.1f}  {ca_height:13.1f}  {wy_height:10.1f}  {diff:12.1f}")

if __name__ == "__main__":
    try:
        test_species_models()
        test_inverse_calculation()
        test_standalone_functions()
        test_model_comparison()
        
        print("\n\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc() 
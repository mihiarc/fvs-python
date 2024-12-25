import unittest
import sqlite3
from unittest.mock import patch, Mock
import numpy as np
import pandas as pd
from fvs_core.grow_stand import grow_stand
from fvs_core.growth_models import (
    calculate_small_tree_height_growth,
    calculate_large_tree_diameter_growth,
    curtis_arney_height,
    calculate_inside_bark_dbh_ratio
)

class TestStandGrowth(unittest.TestCase):
    def setUp(self):
        # Get coefficients from database
        with sqlite3.connect('fvspy.db') as conn:
            # Get small tree growth coefficients
            small_tree_query = "SELECT * FROM small_tree_coefficients WHERE species_code = 'LP'"
            small_tree_df = pd.read_sql_query(small_tree_query, conn)
            if small_tree_df.empty:
                raise ValueError("No small tree coefficients found for LP")
            small_tree_coeffs = small_tree_df.iloc[0]
            
            # Get height-diameter coefficients
            hd_query = "SELECT * FROM height_diameter_coefficients WHERE species_code = 'LP'"
            hd_df = pd.read_sql_query(hd_query, conn)
            if hd_df.empty:
                raise ValueError("No height-diameter coefficients found for LP")
            hd_coeffs = hd_df.iloc[0]
            
            # Get large tree coefficients
            large_tree_query = "SELECT * FROM large_tree_coefficients WHERE species_code = 'LP'"
            large_tree_df = pd.read_sql_query(large_tree_query, conn)
            if large_tree_df.empty:
                raise ValueError("No large tree coefficients found for LP")
            large_tree_coeffs = large_tree_df.iloc[0]
        
        # Create species data using database coefficients
        self.species_data = {
            "LP": {  # Loblolly Pine
                # Small tree height growth coefficients
                "SmallTreeGrowth_c1": small_tree_coeffs['b0'],
                "SmallTreeGrowth_c2": small_tree_coeffs['b1'],
                "SmallTreeGrowth_c3": small_tree_coeffs['b2'],
                "SmallTreeGrowth_c4": small_tree_coeffs['b3'],
                "SmallTreeGrowth_c5": small_tree_coeffs['b4'],
                # Height-diameter coefficients
                "CurtisArney_b0": hd_coeffs['CurtisArney_b0'],
                "CurtisArney_b1": hd_coeffs['CurtisArney_b1'],
                "CurtisArney_b2": hd_coeffs['CurtisArney_b2'],
                # Bark coefficients (using default values since they're not in DB)
                "Bark_b0": 0.9,
                "Bark_b1": 0.01,
                # Volume coefficients (placeholder values)
                "Volume_b0": 0.002,
                "Volume_b1": 1.8,
                "Volume_b2": 1.1,
                # Diameter growth coefficients
                "Lower_Diameter_Limit": 12,
                "Upper_Diameter_Limit": 24,
                "LargeTreeGrowth_b1": large_tree_coeffs['b0'],
                "LargeTreeGrowth_b2": large_tree_coeffs['b1'],
                "LargeTreeGrowth_b3": large_tree_coeffs['b2'],
                "LargeTreeGrowth_b4": large_tree_coeffs['b3'],
                "LargeTreeGrowth_b5": large_tree_coeffs['b4'],
                "LargeTreeGrowth_b6": large_tree_coeffs['b5'],
                "LargeTreeGrowth_b7": 0.0000001,  # Additional coefficients not in database
                "LargeTreeGrowth_b8": 0.0000001,
                "LargeTreeGrowth_b9": 0.0000001,
                "LargeTreeGrowth_b10": 0.0000001,
                "LargeTreeGrowth_b11": 0.0000001
            }
        }
        
        # Crown data (using small values since we don't have crown coefficients in database)
        self.species_crown_data = {
            "LP": {
                "a": 0.0000001,
                "b0": 0.0000001,
                "b1": 0.0000001,
                "c": 0.0000001
            }
        }
        
        # Create a test stand with both small and large trees
        self.stand = [
            # Small tree (DBH < 3.0)
            type('obj', (object,), {
                "species": "LP",
                "dbh": 2.0,
                "height": 15.0,
                "age": 5,
                "si": 80,
                "trees_per_acre": 100,
                "RELSDI": 0.5,
                "CCF": 100,
                "PCCF": 50,
                "BA": 120,
                "PBAL": 80,
                "RELHT": 0.6,
                "Slope": 0.1,
                "Aspect": 0,
                "Fortype": 0.5,
                "Ecounit": 0.2,
                "Plant": 0.1
            }),
            # Large tree (DBH >= 3.0)
            type('obj', (object,), {
                "species": "LP",
                "dbh": 8.0,
                "height": 60.0,
                "age": 20,
                "si": 80,
                "trees_per_acre": 50,
                "RELSDI": 0.7,
                "CCF": 100,
                "PCCF": 30,
                "BA": 120,
                "PBAL": 40,
                "RELHT": 0.9,
                "Slope": 0.1,
                "Aspect": 0,
                "Fortype": 0.5,
                "Ecounit": 0.2,
                "Plant": 0.1
            })
        ]

    def test_individual_growth_functions(self):
        """Test individual growth functions before testing stand growth."""
        # Test small tree height growth
        small_tree = self.stand[0]
        
        # Print coefficients for debugging
        print("\nSmall Tree Growth Coefficients:")
        print(f"si: {small_tree.si}")
        print(f"age: {small_tree.age}")
        print(f"c1: {self.species_data['LP']['SmallTreeGrowth_c1']}")
        print(f"c2: {self.species_data['LP']['SmallTreeGrowth_c2']}")
        print(f"c3: {self.species_data['LP']['SmallTreeGrowth_c3']}")
        print(f"c4: {self.species_data['LP']['SmallTreeGrowth_c4']}")
        print(f"c5: {self.species_data['LP']['SmallTreeGrowth_c5']}")
        print(f"height: {small_tree.height}")
        
        new_height = calculate_small_tree_height_growth(
            small_tree.si,
            small_tree.age,
            self.species_data["LP"]["SmallTreeGrowth_c1"],
            self.species_data["LP"]["SmallTreeGrowth_c2"],
            self.species_data["LP"]["SmallTreeGrowth_c3"],
            self.species_data["LP"]["SmallTreeGrowth_c4"],
            self.species_data["LP"]["SmallTreeGrowth_c5"],
            small_tree.height
        )
        print(f"\nSmall Tree Height Growth:")
        print(f"Initial Height: {small_tree.height:.2f} feet")
        print(f"Predicted Height: {new_height:.2f} feet")
        print(f"Height Growth: {(new_height - small_tree.height):.2f} feet")
        self.assertGreater(new_height, small_tree.height)
        
        # Test large tree diameter growth
        large_tree = self.stand[1]
        b_coeffs = {k.replace('LargeTreeGrowth_', ''): v 
                   for k, v in self.species_data["LP"].items() 
                   if k.startswith('LargeTreeGrowth_')}
        ln_dds = calculate_large_tree_diameter_growth(
            large_tree.dbh,
            0.4,  # crown ratio
            large_tree.RELHT,
            large_tree.si,
            large_tree.BA,
            large_tree.PBAL,
            large_tree.Slope,
            large_tree.Aspect,
            large_tree.Fortype,
            large_tree.Ecounit,
            large_tree.Plant,
            b_coeffs
        )
        print(f"\nLarge Tree Growth:")
        print(f"Initial DBH: {large_tree.dbh:.2f} inches")
        print(f"ln(DDS): {ln_dds:.4f}")
        
        # Test height-diameter relationship
        height = curtis_arney_height(large_tree.dbh, "LP", self.species_data["LP"])
        print(f"Predicted Height from DBH: {height:.2f} feet")
        
        # Test bark ratio
        bark_ratio = calculate_inside_bark_dbh_ratio(large_tree.dbh, "LP", self.species_data["LP"])
        print(f"Inside Bark to Outside Bark Ratio: {bark_ratio:.4f}")
        self.assertGreaterEqual(bark_ratio, 0.80)
        self.assertLessEqual(bark_ratio, 0.99)

if __name__ == '__main__':
    unittest.main()
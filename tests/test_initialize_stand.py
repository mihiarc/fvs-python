import unittest
import sqlite3
import pandas as pd
from src.initialize_stand import initialize_from_fia

class TestFIAInitialization(unittest.TestCase):
    def setUp(self):
        # Get a valid stand_cn from the test database
        with sqlite3.connect('data/test_coastal_loblolly.db') as conn:
            query = "SELECT DISTINCT STAND_CN FROM trees LIMIT 1;"
            df = pd.read_sql_query(query, conn)
            if df.empty:
                raise ValueError("No stands found in database")
            self.stand_cn = df.iloc[0]['STAND_CN']
            
            # Get a sample tree to check its species
            query = "SELECT SPECIES FROM trees WHERE STAND_CN = ? LIMIT 1;"
            df = pd.read_sql_query(query, conn, params=(self.stand_cn,))
            if df.empty:
                raise ValueError("No trees found in stand")
            self.species = "LP"  # We know FIA code 131 maps to LP

    def test_fia_initialization_success(self):
        """Test initializing a stand from FIA data."""
        db_path = "data/test_coastal_loblolly.db"
        
        # Initialize stand from FIA data
        stand = initialize_from_fia(db_path, self.stand_cn)
        
        # Basic structure tests
        self.assertIsInstance(stand, list)
        self.assertGreaterEqual(len(stand), 1)  # Expect at least one tree
        
        # Test each tree's attributes
        for tree in stand:
            # Required attributes
            self.assertTrue(hasattr(tree, "species"))
            self.assertTrue(hasattr(tree, "dbh"))
            self.assertTrue(hasattr(tree, "height"))
            self.assertTrue(hasattr(tree, "trees_per_acre"))
            
            # Value range tests
            self.assertGreater(tree.dbh, 0)
            self.assertGreater(tree.height, 0)
            self.assertGreater(tree.trees_per_acre, 0)
            
            # Species code test
            self.assertEqual(tree.species, self.species)  # Using actual species from database
            
            # Print tree details for inspection
            print(f"\nTree from stand {self.stand_cn}:")
            print(f"Species: {tree.species}")
            print(f"DBH: {tree.dbh:.1f} inches")
            print(f"Height: {tree.height:.1f} feet")
            print(f"Trees per acre: {tree.trees_per_acre:.1f}")

    def test_fia_initialization_error_no_stand(self):
        """Test error handling when stand is not found."""
        db_path = "data/test_coastal_loblolly.db"
        invalid_stand_cn = "INVALID_CN"  # Invalid stand CN
        
        with self.assertRaises(ValueError):
            initialize_from_fia(db_path, invalid_stand_cn)

if __name__ == '__main__':
    unittest.main()
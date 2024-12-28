import unittest
import sqlite3
import pandas as pd
import numpy as np
from src import crown_width
from pathlib import Path

class TestCrownWidth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Update the database path to point to the correct location
        cls.db_path = Path("data/sqlite_databases/fvspy.db")
        
    def test_hopkins_index(self):
        """Test Hopkins index calculation"""
        elevation = 1000  # feet
        latitude = 35.0   # degrees
        longitude = -82.0 # degrees
        
        hopkins_index = crown_width.calculate_hopkins_index(elevation, latitude, longitude)
        self.assertIsInstance(hopkins_index, float)
        
    def test_forest_grown_crown_width_bechtold(self):
        """Test forest-grown crown width calculation using Bechtold equation"""
        # Test with Sassafras (species code SA) which has complete coefficients
        dbh = 10.0  # inches
        crown_ratio = 0.5  # proportion
        hopkins_index = 2.0
        species_code = "SA"  # Sassafras
        
        width = crown_width.calculate_forest_grown_crown_width_bechtold(
            dbh, crown_ratio, hopkins_index, species_code
        )
        self.assertIsInstance(width, float)
        self.assertGreater(width, 0)
        
        # Test small tree case (dbh < 5)
        small_dbh = 3.0
        small_width = crown_width.calculate_forest_grown_crown_width_bechtold(
            small_dbh, crown_ratio, hopkins_index, species_code
        )
        self.assertIsInstance(small_width, float)
        self.assertGreater(small_width, 0)
        self.assertLess(small_width, width)  # Small tree should have smaller crown
        
    def test_crown_area(self):
        """Test crown area calculation"""
        crown_width_ft = 10.0
        area = crown_width.calculate_crown_area(crown_width_ft)
        expected_area = np.pi * (crown_width_ft/2)**2
        self.assertAlmostEqual(area, expected_area)
        
    def test_open_grown_crown_width_elk(self):
        """Test open-grown crown width calculation using Elk equation"""
        # Test with American Elm (species code AE) which has complete coefficients
        dbh = 10.0  # inches
        species_code = "AE"  # American Elm
        
        width = crown_width.calculate_open_grown_crown_width_elk(dbh, species_code)
        self.assertIsInstance(width, float)
        self.assertGreater(width, 0)
        
        # Test small tree case (dbh < 3)
        small_dbh = 2.0
        small_width = crown_width.calculate_open_grown_crown_width_elk(small_dbh, species_code)
        self.assertIsInstance(small_width, float)
        self.assertGreater(small_width, 0)
        self.assertLess(small_width, width)  # Small tree should have smaller crown
        
if __name__ == '__main__':
    unittest.main() 
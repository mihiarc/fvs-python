"""
Tests for crown ratio calculations.
"""

import unittest
import numpy as np
from pathlib import Path
from fvs_core import data_handling
from fvs_core import crown_ratio

class TestCrownRatio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Get test species from the database
        cls.test_species = list(data_handling.species_crown_ratio_data.keys())[:4]  # Use first 4 species
        
        # Map species codes to common names for better test output
        cls.species_names = {code: f"Species {code}" for code in cls.test_species}

    def test_dubbed_crown_ratio(self):
        """Test dubbed crown ratio calculation for dead trees."""
        # Test small DBH (< 24 inches)
        np.random.seed(42)  # For reproducibility
        cr_small = crown_ratio.calculate_dubbed_crown_ratio(12.0, 0.1)
        self.assertGreaterEqual(cr_small, 0.05)
        self.assertLessEqual(cr_small, 0.95)
        
        # Test large DBH (>= 24 inches)
        cr_large = crown_ratio.calculate_dubbed_crown_ratio(30.0, 0.1)
        self.assertGreaterEqual(cr_large, 0.05)
        self.assertLessEqual(cr_large, 0.95)
        
        # Test boundary case
        cr_boundary = crown_ratio.calculate_dubbed_crown_ratio(24.0, 0.1)
        self.assertGreaterEqual(cr_boundary, 0.05)
        self.assertLessEqual(cr_boundary, 0.95)
            
    def test_acr_calculation(self):
        """Test average crown ratio calculation."""
        # Test each species with different relative SDI values
        relsdi_values = [2.0, 4.0, 6.0, 8.0, 10.0]
        
        for species_code in self.test_species:
            for relsdi in relsdi_values:
                acr = crown_ratio.calculate_acr(relsdi, species_code)
                self.assertIsNotNone(acr)
                self.assertGreaterEqual(acr, 0.05)
                self.assertLessEqual(acr, 0.95)
    
    def test_weibull_parameters(self):
        """Test Weibull parameter calculations."""
        for species_code in self.test_species:
            coeffs = data_handling.species_crown_ratio_data[species_code]
            
            # Test with different ACR values
            acr_values = [0.3, 0.5, 0.7]
            for acr in acr_values:
                a, b, c = crown_ratio.calculate_weibull_parameters(
                    acr, coeffs['a'], coeffs['b0'], coeffs['b1'], coeffs['c']
                )
                
                # Check parameter bounds
                self.assertGreaterEqual(b, 0.03)  # b should be bounded by 0.03
                self.assertGreaterEqual(c, 2.0)   # c should be bounded by 2.0
                self.assertIsInstance(a, float)
                self.assertIsInstance(b, float)
                self.assertIsInstance(c, float)
    
    def test_crown_ratio_weibull(self):
        """Test crown ratio calculation using Weibull distribution."""
        x_values = [0.1, 0.3, 0.5, 0.7, 0.9]  # Test different ranks
        scale = 0.8  # Example scale factor
        acr = 0.5   # Example average crown ratio
        
        for species_code in self.test_species:
            for x in x_values:
                cr = crown_ratio.calculate_crown_ratio_weibull(x, species_code, acr, scale)
                self.assertGreaterEqual(cr, 0.05)
                self.assertLessEqual(cr, 0.95)
                self.assertIsInstance(cr, float)
    
    def test_scale_factor(self):
        """Test density-dependent scale factor calculation."""
        # Test various CCF values
        ccf_values = [50, 100, 150, 200, 250]
        
        for ccf in ccf_values:
            scale = crown_ratio.calculate_scale(ccf)
            self.assertGreaterEqual(scale, 0.3)
            self.assertLessEqual(scale, 1.0)
            
        # Test boundary cases
        self.assertAlmostEqual(crown_ratio.calculate_scale(0), 1.0)
        self.assertAlmostEqual(crown_ratio.calculate_scale(1000), 0.3)
    
    def test_crown_ratio_change(self):
        """Test crown ratio change calculation."""
        test_cases = [
            (0.5, 0.6),  # Increase
            (0.6, 0.5),  # Decrease
            (0.5, 0.5)   # No change
        ]
        
        for current_cr, new_cr in test_cases:
            change = crown_ratio.calculate_crown_ratio_change(current_cr, new_cr)
            self.assertEqual(change, new_cr - current_cr)
            self.assertIsInstance(change, float)
    
    def test_invalid_species(self):
        """Test error handling for invalid species codes."""
        invalid_species = "INVALID"
        
        # Test ACR calculation
        with self.assertRaises(KeyError):
            crown_ratio.calculate_acr(5.0, invalid_species)
        
        # Test crown ratio calculation
        with self.assertRaises(KeyError):
            crown_ratio.calculate_crown_ratio_weibull(0.5, invalid_species, 0.5, 0.8)

if __name__ == '__main__':
    unittest.main() 
"""
Tests for crown ratio calculations.
"""

import unittest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import importlib.util
from tabulate import tabulate

# Import the crown_ratio module directly
spec = importlib.util.spec_from_file_location(
    "crown_ratio", 
    Path(__file__).parent.parent / "fvs_core" / "crown_ratio.py"
)
crown_ratio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crown_ratio)

class TestCrownRatio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Test data for southern yellow pines
        cls.test_species = [
            # species_code, acr_equation, d0, d1, d2, a0, b0, b1, c0
            ('SP', 1, -0.0821, -0.1701, -0.0196, 5.0, -3.0, 1.2, 2.5),  # Shortleaf Pine
            ('SA', 1, -0.0789, -0.1654, -0.0189, 5.5, -2.8, 1.1, 2.4),  # Slash Pine
            ('LL', 1, -0.0856, -0.1748, -0.0203, 4.5, -3.2, 1.3, 2.6),  # Longleaf Pine
            ('LP', 1, -0.0734, -0.1607, -0.0182, 5.2, -2.9, 1.15, 2.45)  # Loblolly Pine
        ]
        
        # Map species codes to common names for better plot labels
        cls.species_names = {
            'SP': 'Shortleaf Pine',
            'SA': 'Slash Pine',
            'LL': 'Longleaf Pine',
            'LP': 'Loblolly Pine'
        }
        
        # Create coefficients dictionary for each species
        cls.species_coeffs = {
            code: {
                'acr_equation_number': eq,
                'd0': d0,
                'd1': d1,
                'd2': d2,
                'a0': a0,
                'b0': b0,
                'b1': b1,
                'c0': c0
            }
            for code, eq, d0, d1, d2, a0, b0, b1, c0 in cls.test_species
        }

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
        
        for species_data in self.test_species:
            species_code = species_data[0]
            for relsdi in relsdi_values:
                acr = crown_ratio.calculate_acr(relsdi, species_code)
                self.assertIsNotNone(acr)
                self.assertGreaterEqual(acr, 0.05)
                self.assertLessEqual(acr, 0.95)
    
    def test_weibull_parameters(self):
        """Test Weibull parameter calculations."""
        for species_data in self.test_species:
            species_code = species_data[0]
            coeffs = self.species_coeffs[species_code]
            
            # Test with different ACR values
            acr_values = [0.3, 0.5, 0.7]
            for acr in acr_values:
                a, b, c = crown_ratio.calculate_weibull_parameters(
                    acr, coeffs['a0'], coeffs['b0'], coeffs['b1'], coeffs['c0']
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
        
        for species_data in self.test_species:
            species_code = species_data[0]
            coeffs = self.species_coeffs[species_code]
            
            # Calculate parameters
            a, b, c = crown_ratio.calculate_weibull_parameters(
                0.5,  # Example ACR
                coeffs['a0'],
                coeffs['b0'],
                coeffs['b1'],
                coeffs['c0']
            )
            
            for x in x_values:
                cr = crown_ratio.calculate_crown_ratio_weibull(x, a, b, c, scale)
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
    
    def test_visualize_acr_curves(self):
        """Create visualization of average crown ratio curves for different species."""
        relsdi_range = np.linspace(1.0, 12.0, 100)
        plt.figure(figsize=(12, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Distinct colors for each species
        for i, species_data in enumerate(self.test_species):
            species_code = species_data[0]
            acr_values = [crown_ratio.calculate_acr(relsdi, species_code) 
                         for relsdi in relsdi_range]
            plt.plot(relsdi_range, acr_values, label=self.species_names[species_code], 
                    color=colors[i], linewidth=2)
        
        plt.xlabel('Relative SDI', fontsize=12)
        plt.ylabel('Average Crown Ratio', fontsize=12)
        plt.title('Average Crown Ratio vs Relative SDI\nSouthern Yellow Pines', 
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.tight_layout()
        
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / 'acr_curves.png', dpi=300, bbox_inches='tight')
        plt.close()

    def test_visualize_weibull_curves(self):
        """Create visualization of Weibull-based crown ratio curves for different species."""
        x_range = np.linspace(0.05, 0.95, 100)  # Tree rank values
        scale = 0.8  # Example scale factor
        acr = 0.5   # Example average crown ratio
        plt.figure(figsize=(12, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Distinct colors for each species
        for i, species_data in enumerate(self.test_species):
            species_code = species_data[0]
            coeffs = self.species_coeffs[species_code]
            
            # Calculate Weibull parameters
            a, b, c = crown_ratio.calculate_weibull_parameters(
                acr,
                coeffs['a0'],
                coeffs['b0'],
                coeffs['b1'],
                coeffs['c0']
            )
            
            # Calculate crown ratios
            cr_values = [crown_ratio.calculate_crown_ratio_weibull(x, a, b, c, scale) 
                        for x in x_range]
            plt.plot(x_range, cr_values, label=self.species_names[species_code], 
                    color=colors[i], linewidth=2)
        
        plt.xlabel('Tree Rank (percentile)', fontsize=12)
        plt.ylabel('Crown Ratio', fontsize=12)
        plt.title('Crown Ratio vs Tree Rank\nSouthern Yellow Pines (ACR=0.5, Scale=0.8)', 
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.tight_layout()
        
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / 'weibull_curves.png', dpi=300, bbox_inches='tight')
        plt.close()

    def test_acr_table(self):
        """Create a table of average crown ratios at different relative SDI levels."""
        # Define relative SDI levels to test
        relsdi_levels = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
        
        # Calculate ACR for each species at each relative SDI
        headers = ['RelSDI'] + [self.species_names[code] for code, *_ in self.test_species]
        rows = []
        
        for relsdi in relsdi_levels:
            row = [f"{relsdi:.1f}"]
            for species_data in self.test_species:
                species_code = species_data[0]
                acr = crown_ratio.calculate_acr(relsdi, species_code)
                row.append(f"{acr:.3f}")
            rows.append(row)
        
        # Create and print the table
        table = tabulate(rows, headers=headers, tablefmt='pipe', floatfmt='.3f')
        print("\nAverage Crown Ratio Table:")
        print(table)
        
        # Also save to a file
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / 'acr_table.txt', 'w') as f:
            f.write("Average Crown Ratio Table:\n")
            f.write(table)

if __name__ == '__main__':
    unittest.main() 
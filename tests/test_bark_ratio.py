"""
Tests for bark ratio calculations in the growth module.
"""

import unittest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import importlib.util
from tabulate import tabulate

# Import just the growth_models module directly
spec = importlib.util.spec_from_file_location(
    "growth_models", 
    Path(__file__).parent.parent / "fvs_core" / "growth_models.py"
)
growth_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(growth_models)
calculate_inside_bark_dbh_ratio = growth_models.calculate_inside_bark_dbh_ratio

class TestBarkRatio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Test data for southern yellow pines
        cls.test_species = [
            # species_code, b0, b1
            ('SP', -0.44121, 0.93045),  # Shortleaf Pine
            ('SA', -0.55073, 0.91887),  # Slash Pine
            ('LL', -0.45903, 0.92746),  # Longleaf Pine
            ('LP', -0.48140, 0.91413)   # Loblolly Pine
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
                'Bark_b0': b0,
                'Bark_b1': b1
            }
            for code, b0, b1 in cls.test_species
        }

    def test_basic_functionality(self):
        """Test basic functionality with valid inputs."""
        for species_data in self.test_species:
            species_code = species_data[0]
            dbh = 10.0  # Test with a common DBH value
            
            ratio = calculate_inside_bark_dbh_ratio(dbh, species_code, self.species_coeffs[species_code])
            
            self.assertIsInstance(ratio, float)
            self.assertGreaterEqual(ratio, 0.80)  # Lower bound
            self.assertLessEqual(ratio, 0.99)     # Upper bound
            
    def test_invalid_species(self):
        """Test that function raises ValueError for invalid species code."""
        with self.assertRaises(ValueError):
            calculate_inside_bark_dbh_ratio(10.0, "INVALID_SPECIES")
            
    def test_coefficient_override(self):
        """Test that coefficient override works correctly."""
        test_coeffs = {
            'Bark_b0': -0.5,
            'Bark_b1': 0.92
        }
        
        ratio = calculate_inside_bark_dbh_ratio(10.0, "TEST", test_coeffs)
        self.assertIsInstance(ratio, float)
        self.assertGreaterEqual(ratio, 0.80)
        self.assertLessEqual(ratio, 0.99)
        
    def test_visualize_ratio_curves(self):
        """Create visualization of bark ratio curves for different species."""
        dbh_range = np.linspace(0.5, 30, 100)
        plt.figure(figsize=(12, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Distinct colors for each species
        for i, species_data in enumerate(self.test_species):
            species_code = species_data[0]
            ratios = [calculate_inside_bark_dbh_ratio(dbh, species_code, self.species_coeffs[species_code]) 
                     for dbh in dbh_range]
            plt.plot(dbh_range, ratios, label=self.species_names[species_code], 
                    color=colors[i], linewidth=2)
        
        # Add horizontal lines for bounds
        plt.axhline(y=0.80, color='gray', linestyle='--', alpha=0.5, label='Lower Bound (0.80)')
        plt.axhline(y=0.99, color='gray', linestyle='--', alpha=0.5, label='Upper Bound (0.99)')
        
        plt.xlabel('DBH (inches)', fontsize=12)
        plt.ylabel('Inside-Bark to Outside-Bark DBH Ratio', fontsize=12)
        plt.title('Bark Ratio Relationships\nSouthern Yellow Pines', 
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Customize the plot appearance
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.tight_layout()
        
        # Save the plot
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / 'bark_ratio_curves.png', dpi=300, bbox_inches='tight')
        plt.close()

    def test_ratio_table(self):
        """Create a table of bark ratios at different DBH levels for inspection."""
        # Define DBH levels to test
        dbh_levels = [0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 24.0]
        
        # Calculate ratios for each species at each DBH
        headers = ['DBH'] + [self.species_names[code] for code, *_ in self.test_species]
        rows = []
        
        for dbh in dbh_levels:
            row = [f"{dbh:.2f}"]
            for species_data in self.test_species:
                species_code = species_data[0]
                ratio = calculate_inside_bark_dbh_ratio(dbh, species_code, self.species_coeffs[species_code])
                row.append(f"{ratio:.3f}")
            rows.append(row)
        
        # Create and print the table
        table = tabulate(rows, headers=headers, tablefmt='pipe', floatfmt='.3f')
        print("\nBark Ratio Table (inside-bark to outside-bark DBH ratio):")
        print(table)
        
        # Also save to a file
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / 'bark_ratio_table.txt', 'w') as f:
            f.write("Bark Ratio Table (inside-bark to outside-bark DBH ratio):\n")
            f.write(table)

    def test_bounds(self):
        """Test that ratios are properly bounded between 0.80 and 0.99."""
        # Test with extreme values that should trigger bounds
        test_dbh_values = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]
        
        for species_data in self.test_species:
            species_code = species_data[0]
            for dbh in test_dbh_values:
                ratio = calculate_inside_bark_dbh_ratio(dbh, species_code, self.species_coeffs[species_code])
                self.assertGreaterEqual(ratio, 0.80, 
                                      f"Ratio {ratio} below minimum bound for {species_code} at DBH={dbh}")
                self.assertLessEqual(ratio, 0.99, 
                                   f"Ratio {ratio} above maximum bound for {species_code} at DBH={dbh}")

if __name__ == '__main__':
    unittest.main()
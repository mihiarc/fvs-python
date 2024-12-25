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
curtis_arney_height = growth_models.curtis_arney_height

class TestCurtisArneyHeight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Test data for southern yellow pines
        cls.test_species = [
            # species_code, b0, b1, b2, dbw
            ('SP', 444.0921666, 4.11876312, -0.30617043, 0.5),  # Shortleaf Pine (fixed b2 typo)
            ('SA', 1087.101439, 5.10450596, -0.24284896, 0.5),  # Slash Pine
            ('LL', 98.56082813, 3.89930709, -0.86730393, 0.5),  # Longleaf Pine
            ('LP', 243.860648, 4.28460566, -0.47130185, 0.5)    # Loblolly Pine
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
                'CurtisArney_b0': b0,
                'CurtisArney_b1': b1,
                'CurtisArney_b2': b2,
                'Dbw': dbw
            }
            for code, b0, b1, b2, dbw in cls.test_species
        }

    def test_basic_functionality(self):
        """Test basic functionality with valid inputs."""
        for species_data in self.test_species:
            species_code = species_data[0]
            dbh = 10.0  # Test with a common DBH value
            
            height = curtis_arney_height(dbh, species_code, self.species_coeffs[species_code])
            
            self.assertIsInstance(height, float)
            self.assertGreater(height, 4.51)  # Height should be greater than minimum
            
    def test_small_tree_calculation(self):
        """Test calculation for trees with DBH < 3.0 inches."""
        for species_data in self.test_species:
            species_code = species_data[0]
            dbh = 2.0  # Test with small DBH
            
            height = curtis_arney_height(dbh, species_code, self.species_coeffs[species_code])
            
            self.assertIsInstance(height, float)
            self.assertGreater(height, 4.51)
            
    def test_invalid_species(self):
        """Test that function raises ValueError for invalid species code."""
        with self.assertRaises(ValueError):
            curtis_arney_height(10.0, "INVALID_SPECIES")
            
    def test_coefficient_override(self):
        """Test that coefficient override works correctly."""
        test_coeffs = {
            'CurtisArney_b0': 100.0,
            'CurtisArney_b1': 0.1,
            'CurtisArney_b2': 1.0,
            'Dbw': 0.2
        }
        
        height = curtis_arney_height(10.0, "TEST", test_coeffs)
        self.assertIsInstance(height, float)
        
    def test_visualize_height_curves(self):
        """Create visualization of height-diameter curves for different species."""
        dbh_range = np.linspace(0.5, 30, 100)
        plt.figure(figsize=(12, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Distinct colors for each species
        for i, species_data in enumerate(self.test_species):
            species_code = species_data[0]
            heights = [curtis_arney_height(dbh, species_code, self.species_coeffs[species_code]) 
                      for dbh in dbh_range]
            plt.plot(dbh_range, heights, label=self.species_names[species_code], 
                    color=colors[i], linewidth=2)
        
        plt.axvline(x=3.0, color='gray', linestyle='--', alpha=0.5, 
                   label='Small/Large Tree Threshold')
        plt.xlabel('DBH (inches)', fontsize=12)
        plt.ylabel('Height (feet)', fontsize=12)
        plt.title('Curtis-Arney Height-Diameter Relationships\nSouthern Yellow Pines', 
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Customize the plot appearance
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.tight_layout()
        
        # Save the plot
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / 'curtis_arney_height_curves.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def test_height_continuity(self):
        """Test that height predictions are continuous around DBH=3.0."""
        for species_data in self.test_species:
            species_code = species_data[0]
            
            # Test points just below and above the threshold
            h1 = curtis_arney_height(2.99, species_code, self.species_coeffs[species_code])
            h2 = curtis_arney_height(3.01, species_code, self.species_coeffs[species_code])
            
            # Heights should be reasonably close at the transition point
            # A difference of up to 0.5 feet (6 inches) is acceptable
            self.assertLess(abs(h1 - h2), 0.5, 
                          f"Height discontinuity of {abs(h1 - h2):.2f} feet at DBH=3.0 for {species_code}")

    def test_height_table(self):
        """Create a table of heights at different DBH levels for inspection."""
        # Define DBH levels to test
        dbh_levels = [0.5, 1.0, 2.0, 2.99, 3.01, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 24.0]
        
        # Calculate heights for each species at each DBH
        headers = ['DBH'] + [self.species_names[code] for code, *_ in self.test_species]
        rows = []
        
        for dbh in dbh_levels:
            row = [f"{dbh:.2f}"]
            for species_data in self.test_species:
                species_code = species_data[0]
                height = curtis_arney_height(dbh, species_code, self.species_coeffs[species_code])
                row.append(f"{height:.1f}")
            rows.append(row)
        
        # Create and print the table
        table = tabulate(rows, headers=headers, tablefmt='pipe', floatfmt='.1f')
        print("\nHeight-Diameter Table (heights in feet):")
        print(table)
        
        # Also save to a file
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / 'height_table.txt', 'w') as f:
            f.write("Height-Diameter Table (heights in feet):\n")
            f.write(table)

if __name__ == '__main__':
    unittest.main() 
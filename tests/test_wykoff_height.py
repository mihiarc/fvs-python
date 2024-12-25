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
wykoff_height = growth_models.wykoff_height

class TestWykoffHeight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Test data for southern yellow pines
        cls.test_species = [
            # species_code, b0, b1
            ('SP', 4.6271, -6.4095),    # Shortleaf Pine (fixed b1 typo)
            ('SA', 4.6561, -6.2258),    # Slash Pine
            ('LL', 4.5991, -5.9111),    # Longleaf Pine
            ('LP', 4.6897, -6.8801)     # Loblolly Pine
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
                'Wykoff_b0': b0,
                'Wykoff_b1': b1
            }
            for code, b0, b1 in cls.test_species
        }

    def test_basic_functionality(self):
        """Test basic functionality with valid inputs."""
        for species_data in self.test_species:
            species_code = species_data[0]
            dbh = 10.0  # Test with a common DBH value
            
            height = wykoff_height(dbh, species_code, self.species_coeffs[species_code])
            
            self.assertIsInstance(height, float)
            self.assertGreater(height, 4.51)  # Height should be greater than minimum
            
    def test_invalid_species(self):
        """Test that function raises ValueError for invalid species code."""
        with self.assertRaises(ValueError):
            wykoff_height(10.0, "INVALID_SPECIES")
            
    def test_coefficient_override(self):
        """Test that coefficient override works correctly."""
        test_coeffs = {
            'Wykoff_b0': 4.5,
            'Wykoff_b1': -6.0
        }
        
        height = wykoff_height(10.0, "TEST", test_coeffs)
        self.assertIsInstance(height, float)
        
    def test_visualize_height_curves(self):
        """Create visualization of height-diameter curves for different species."""
        dbh_range = np.linspace(0.5, 30, 100)
        plt.figure(figsize=(12, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Distinct colors for each species
        for i, species_data in enumerate(self.test_species):
            species_code = species_data[0]
            heights = [wykoff_height(dbh, species_code, self.species_coeffs[species_code]) 
                      for dbh in dbh_range]
            plt.plot(dbh_range, heights, label=self.species_names[species_code], 
                    color=colors[i], linewidth=2)
        
        plt.xlabel('DBH (inches)', fontsize=12)
        plt.ylabel('Height (feet)', fontsize=12)
        plt.title('Wykoff Height-Diameter Relationships\nSouthern Yellow Pines', 
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Customize the plot appearance
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.tight_layout()
        
        # Save the plot
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / 'wykoff_height_curves.png', dpi=300, bbox_inches='tight')
        plt.close()

    def test_height_table(self):
        """Create a table of heights at different DBH levels for inspection."""
        # Define DBH levels to test
        dbh_levels = [0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 24.0]
        
        # Calculate heights for each species at each DBH
        headers = ['DBH'] + [self.species_names[code] for code, *_ in self.test_species]
        rows = []
        
        for dbh in dbh_levels:
            row = [f"{dbh:.2f}"]
            for species_data in self.test_species:
                species_code = species_data[0]
                height = wykoff_height(dbh, species_code, self.species_coeffs[species_code])
                row.append(f"{height:.1f}")
            rows.append(row)
        
        # Create and print the table
        table = tabulate(rows, headers=headers, tablefmt='pipe', floatfmt='.1f')
        print("\nHeight-Diameter Table (heights in feet):")
        print(table)
        
        # Also save to a file
        output_dir = Path(__file__).parent / 'test_output'
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / 'wykoff_height_table.txt', 'w') as f:
            f.write("Height-Diameter Table (heights in feet):\n")
            f.write(table)

if __name__ == '__main__':
    unittest.main() 
"""Unit tests for height-diameter relationships."""

import pytest
import math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from src.core.growth.height_diameter import curtis_arney_height

class TestCurtisArneyHeight:
    """Test cases for Curtis-Arney height-diameter relationship."""
    
    @pytest.fixture
    def output_dir(self):
        """Fixture providing the output directory for plots."""
        output_dir = Path(__file__).parent / "plots"
        output_dir.mkdir(exist_ok=True)
        return output_dir

    @pytest.fixture
    def species_coeffs(self):
        """Fixture providing test coefficients for each species."""
        return {
            'LP': {  # Loblolly Pine
                'CurtisArney_b0': 243.860648,
                'CurtisArney_b1': 4.28460566,
                'CurtisArney_b2': -0.47130185,
                'Dbw': 0.2
            },
            'SP': {  # Shortleaf Pine
                'CurtisArney_b0': 444.0921666,
                'CurtisArney_b1': 4.11876312,
                'CurtisArney_b2': -0.30617043,
                'Dbw': 0.2
            },
            'LL': {  # Longleaf Pine
                'CurtisArney_b0': 98.56082813,
                'CurtisArney_b1': 3.89930709,
                'CurtisArney_b2': -0.86730393,
                'Dbw': 0.2
            },
            'SA': {  # Slash Pine
                'CurtisArney_b0': 1087.101439,
                'CurtisArney_b1': 5.10450596,
                'CurtisArney_b2': -0.24284896,
                'Dbw': 0.2
            }
        }
    
    @pytest.fixture
    def species_names(self):
        """Fixture providing full species names for plotting."""
        return {
            'LP': 'Loblolly Pine',
            'SP': 'Shortleaf Pine',
            'LL': 'Longleaf Pine',
            'SA': 'Slash Pine'
        }
    
    def test_breakpoint_height(self, species_coeffs):
        """Test that height at diameter breakpoint equals breast height."""
        for species, coeffs in species_coeffs.items():
            dbh = coeffs['Dbw']
            height = curtis_arney_height(dbh, coeffs)
            assert height == 4.51  # At breakpoint, height should be breast height
    
    def test_small_tree_interpolation(self, species_coeffs):
        """Test linear interpolation for small trees (DBH < 3.0)."""
        # Test with Loblolly Pine
        coeffs = species_coeffs['LP']
        dbw = coeffs['Dbw']
        
        # Calculate height at DBH = 3.0 for reference
        h3 = curtis_arney_height(3.0, coeffs)
        
        # Test points between dbw and 3.0
        test_dbhs = [0.5, 1.0, 2.0, 2.5]
        for dbh in test_dbhs:
            height = curtis_arney_height(dbh, coeffs)
            # Calculate expected height using linear interpolation
            expected = 4.51 + (h3 - 4.51) * (dbh - dbw) / (3.0 - dbw)
            assert math.isclose(height, expected, rel_tol=1e-10)
    
    def test_large_tree_equation(self, species_coeffs):
        """Test full Curtis-Arney equation for large trees (DBH ≥ 3.0)."""
        # Test with Loblolly Pine
        coeffs = species_coeffs['LP']
        b0 = coeffs['CurtisArney_b0']
        b1 = coeffs['CurtisArney_b1']
        b2 = coeffs['CurtisArney_b2']
        
        dbh = 10.0
        height = curtis_arney_height(dbh, coeffs)
        expected = 4.51 + b0 * math.exp(-b1 * dbh**b2)
        assert math.isclose(height, expected, rel_tol=1e-10)
    
    def test_monotonic_increasing(self, species_coeffs):
        """Test that height increases monotonically with DBH."""
        dbh_values = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 20.0]
        
        for species, coeffs in species_coeffs.items():
            prev_height = 0
            for dbh in dbh_values:
                height = curtis_arney_height(dbh, coeffs)
                assert height > prev_height
                prev_height = height
    
    def test_asymptotic_behavior(self, species_coeffs):
        """Test that height approaches but never exceeds asymptotic maximum."""
        large_dbhs = [30.0, 40.0, 50.0]
        
        for species, coeffs in species_coeffs.items():
            asymptotic_max = 4.51 + coeffs['CurtisArney_b0']
            heights = [curtis_arney_height(dbh, coeffs) for dbh in large_dbhs]
            
            # Heights should be less than asymptotic maximum
            for height in heights:
                assert height < asymptotic_max
            
            # Height increases should be diminishing
            increases = [heights[i+1] - heights[i] for i in range(len(heights)-1)]
            for i in range(len(increases)-1):
                assert increases[i] > increases[i+1]  # Each increase should be smaller than the previous
    
    def test_continuity_at_transition(self, species_coeffs):
        """Test continuity of height function at DBH = 3.0."""
        epsilon = 0.0001  # Small value for testing limit
        
        for species, coeffs in species_coeffs.items():
            # Heights just below and above transition point
            h_below = curtis_arney_height(3.0 - epsilon, coeffs)
            h_above = curtis_arney_height(3.0 + epsilon, coeffs)
            
            # Difference should be very small
            assert abs(h_above - h_below) < 0.01
    
    def test_invalid_inputs(self, species_coeffs):
        """Test handling of invalid inputs."""
        # Test negative DBH
        with pytest.raises(ValueError, match="DBH must be positive"):
            curtis_arney_height(-1.0, species_coeffs['LP'])
        
        # Test zero DBH
        with pytest.raises(ValueError, match="DBH must be positive"):
            curtis_arney_height(0.0, species_coeffs['LP'])
        
        # Test missing coefficients
        incomplete_coeffs = {
            'CurtisArney_b0': 243.860648,
            'CurtisArney_b1': 4.28460566
            # Missing CurtisArney_b2
        }
        with pytest.raises(ValueError, match="Missing required coefficients"):
            curtis_arney_height(10.0, incomplete_coeffs) 
    
    def test_visualize_relationships(self, species_coeffs, species_names, output_dir):
        """Create visualizations of height-diameter relationships."""
        # Generate DBH ranges
        small_dbh = np.linspace(0.2, 3.0, 100)  # Small tree range
        large_dbh = np.linspace(3.0, 50.0, 200)  # Large tree range
        full_dbh = np.concatenate([small_dbh, large_dbh])

        # Plot 1: Height vs DBH curves for all species
        plt.figure(figsize=(12, 8))
        for species, coeffs in species_coeffs.items():
            heights = [curtis_arney_height(d, coeffs) for d in full_dbh]
            plt.plot(full_dbh, heights, label=species_names[species], linewidth=2)

        plt.axvline(x=3.0, color='gray', linestyle='--', alpha=0.5, 
                   label='Small/Large Tree Transition')
        plt.xlabel('DBH (inches)', fontsize=12)
        plt.ylabel('Height (feet)', fontsize=12)
        plt.title('Curtis-Arney Height-Diameter Relationships\nSouthern Yellow Pines', 
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'height_curves.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 2: Height growth rate
        plt.figure(figsize=(12, 8))
        for species, coeffs in species_coeffs.items():
            heights = np.array([curtis_arney_height(d, coeffs) for d in large_dbh])
            # Calculate height growth rate (derivative approximation)
            growth_rate = np.diff(heights) / np.diff(large_dbh)
            plt.plot(large_dbh[1:], growth_rate, label=species_names[species], linewidth=2)

        plt.xlabel('DBH (inches)', fontsize=12)
        plt.ylabel('Height Growth Rate (feet/inch)', fontsize=12)
        plt.title('Height Growth Rate vs DBH\nSouthern Yellow Pines', 
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'growth_rate.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 3: Small tree interpolation detail
        plt.figure(figsize=(12, 8))
        small_dbh_detailed = np.linspace(0.2, 4.0, 200)
        for species, coeffs in species_coeffs.items():
            heights = [curtis_arney_height(d, coeffs) for d in small_dbh_detailed]
            plt.plot(small_dbh_detailed, heights, label=species_names[species], linewidth=2)

        plt.axvline(x=3.0, color='gray', linestyle='--', alpha=0.5,
                   label='Small/Large Tree Transition')
        plt.xlabel('DBH (inches)', fontsize=12)
        plt.ylabel('Height (feet)', fontsize=12)
        plt.title('Small Tree Height Interpolation Detail\nSouthern Yellow Pines',
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'small_tree_detail.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 4: Transition point behavior
        plt.figure(figsize=(12, 8))
        transition_dbh = np.linspace(2.5, 3.5, 500)
        for species, coeffs in species_coeffs.items():
            heights = [curtis_arney_height(d, coeffs) for d in transition_dbh]
            plt.plot(transition_dbh, heights, label=species_names[species], linewidth=2)

        plt.axvline(x=3.0, color='gray', linestyle='--', alpha=0.5,
                   label='Small/Large Tree Transition')
        plt.xlabel('DBH (inches)', fontsize=12)
        plt.ylabel('Height (feet)', fontsize=12)
        plt.title('Height-Diameter Relationship at Transition Point\nSouthern Yellow Pines',
                 fontsize=14, pad=20)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'transition_detail.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Verify files were created
        expected_files = ['height_curves.png', 'growth_rate.png', 
                         'small_tree_detail.png', 'transition_detail.png']
        for file in expected_files:
            assert (output_dir / file).exists() 
"""Test utilities for growth model tests."""

from dataclasses import dataclass

@dataclass
class TestTree:
    """Test data structure to simulate Tree class."""
    species: str
    dbh: float
    height: float
    crown_ratio: float
    age: int = 5

# Sample coefficients for testing (using LP coefficients from README)
TEST_COEFFICIENTS = {
    'p2': 243.860648,  # Curtis-Arney height equation
    'p3': 4.28460566,
    'p4': -0.47130185,
    'Dbw': 0.5,
    'Xmin': 1.0,
    'Xmax': 3.0,
    'forest_type_factor': 0.0,
    'ecounit_factor': 0.0,
    'planting_factor': 0.245669,
    'c1': 1.1421,  # Chapman-Richards growth
    'c2': 1.0042,
    'c3': -0.0374,
    'c4': 0.7632,
    'c5': 0.0358,
    'b1': 0.222214,  # Large tree diameter growth
    'b2': 1.163040,
    'b3': -0.000863,
    'b4': 0.028483,
    'b5': 0.006935,
    'b6': 0.005018,
    'b7': -0.000035,
    'b8': -0.000045,
    'b9': 0.0,
    'b10': 0.0,
    'b11': 0.0
}

# Sample stand conditions for testing
SAMPLE_STAND_CONDITIONS = {
    'basal_area': 100.0,
    'plot_basal_area_larger': 50.0,
    'crown_competition_factor': 150.0,
    'relative_height': 0.8,
    'slope': 0.1,
    'aspect': 0.0
} 
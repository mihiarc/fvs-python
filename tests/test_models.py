"""Unit tests for core data structures."""

import pytest
from src.models import Tree, SpeciesConfig

class TestTree:
    """Test cases for the Tree class."""
    
    def test_valid_tree_creation(self):
        """Test creating a valid tree."""
        tree = Tree(species_code='LP', dbh=1.0, height=5.0)
        assert tree.species_code == 'LP'
        assert tree.dbh == 1.0
        assert tree.height == 5.0
        assert tree.crown_ratio == 0.0  # default value
    
    def test_invalid_species_code(self):
        """Test that invalid species codes raise ValueError."""
        with pytest.raises(ValueError, match="Invalid species code"):
            Tree(species_code='XX', dbh=1.0, height=5.0)
    
    def test_invalid_dbh(self):
        """Test that invalid DBH values raise ValueError."""
        with pytest.raises(ValueError, match="DBH must be positive"):
            Tree(species_code='LP', dbh=-1.0, height=5.0)
    
    def test_invalid_height(self):
        """Test that invalid height values raise ValueError."""
        with pytest.raises(ValueError, match="Height must be positive"):
            Tree(species_code='LP', dbh=1.0, height=0.0)
    
    def test_invalid_crown_ratio(self):
        """Test that invalid crown ratio values raise ValueError."""
        with pytest.raises(ValueError, match="Crown ratio must be between 0 and 1"):
            Tree(species_code='LP', dbh=1.0, height=5.0, crown_ratio=1.5)
    
    def test_basal_area_calculation(self):
        """Test basal area calculations."""
        tree = Tree(species_code='LP', dbh=10.0, height=50.0)
        expected_ba = 0.005454 * 10.0 * 10.0
        assert abs(tree.basal_area - expected_ba) < 1e-6
    
    def test_basal_area_per_acre(self):
        """Test basal area per acre calculations with expansion factor."""
        tree = Tree(species_code='LP', dbh=10.0, height=50.0, expansion_factor=10.0)
        expected_ba = 0.005454 * 10.0 * 10.0 * 10.0
        assert abs(tree.basal_area_per_acre - expected_ba) < 1e-6
    
    def test_growth_update(self):
        """Test updating tree growth measurements."""
        tree = Tree(species_code='LP', dbh=1.0, height=5.0)
        tree.update_growth(new_dbh=2.0, new_height=10.0)
        assert tree.previous_dbh == 1.0
        assert tree.previous_height == 5.0
        assert tree.dbh == 2.0
        assert tree.height == 10.0
        assert tree.growth_increment == 1.0
    
    def test_competition_update(self):
        """Test updating competition metrics."""
        tree = Tree(species_code='LP', dbh=1.0, height=5.0)
        tree.update_competition(pccf=100.0, ccf=150.0)
        assert tree.pccf == 100.0
        assert tree.ccf == 150.0
    
    def test_string_representation(self):
        """Test string representation of tree."""
        tree = Tree(species_code='LP', dbh=10.5, height=55.7)
        expected = "LP tree: 10.5\" DBH, 55.7' tall"
        assert str(tree) == expected


class TestSpeciesConfig:
    """Test cases for the SpeciesConfig class."""
    
    @pytest.fixture
    def valid_config(self):
        """Create a valid species configuration for testing."""
        return SpeciesConfig(
            code='LP',
            site_index_range=(50.0, 70.0),
            dbw=5.0,
            small_tree_coeffs={'b0': 1.0, 'b1': 2.0},
            large_tree_coeffs={'b0': 3.0, 'b1': 4.0},
            curtis_arney_coeffs={'b0': 5.0, 'b1': 6.0},
            crown_coeffs_forest={'a1': 7.0, 'a2': 8.0}
        )
    
    def test_valid_config_creation(self, valid_config):
        """Test creating a valid species configuration."""
        assert valid_config.code == 'LP'
        assert valid_config.site_index_range == (50.0, 70.0)
        assert valid_config.dbw == 5.0
    
    def test_invalid_species_code(self):
        """Test that invalid species codes raise ValueError."""
        with pytest.raises(ValueError, match="Invalid species code"):
            SpeciesConfig(code='XX', site_index_range=(50.0, 70.0), dbw=5.0)
    
    def test_invalid_site_index_range(self):
        """Test that invalid site index ranges raise ValueError."""
        with pytest.raises(ValueError, match="Invalid site index range"):
            SpeciesConfig(code='LP', site_index_range=(70.0, 50.0), dbw=5.0)
    
    def test_invalid_dbw(self):
        """Test that invalid diameter breakpoint values raise ValueError."""
        with pytest.raises(ValueError, match="Diameter breakpoint must be positive"):
            SpeciesConfig(code='LP', site_index_range=(50.0, 70.0), dbw=0.0)
    
    def test_validate_tree_measurements(self, valid_config):
        """Test validation of tree measurements."""
        # Valid measurements should not raise
        valid_config.validate_tree(dbh=10.0, height=50.0, site_index=60.0)
        
        # Invalid DBH should raise
        with pytest.raises(ValueError, match="DBH .* outside valid range"):
            valid_config.validate_tree(dbh=150.0, height=50.0, site_index=60.0)
        
        # Invalid site index should raise
        with pytest.raises(ValueError, match="Site index .* outside valid range"):
            valid_config.validate_tree(dbh=10.0, height=50.0, site_index=80.0)
    
    def test_typical_rotation(self, valid_config):
        """Test getting typical rotation ranges."""
        min_age, max_age = valid_config.get_typical_rotation()
        assert min_age == 20  # Loblolly Pine
        assert max_age == 30
    
    def test_from_database(self):
        """Test loading species configuration from database."""
        config = SpeciesConfig.from_database('LP')
        
        # Basic info
        assert config.code == 'LP'
        assert isinstance(config.site_index_range, tuple)
        assert len(config.site_index_range) == 2
        assert config.dbw > 0
        
        # Coefficients
        assert config.small_tree_coeffs
        assert config.large_tree_coeffs
        assert config.curtis_arney_coeffs
        assert config.crown_coeffs_forest
        assert config.crown_coeffs_open
        assert config.bark_coeffs
        
        # Environmental
        assert config.shade_tolerance
        # Ecological coefficients are optional until we implement ecological unit functionality
        assert isinstance(config.ecological_coeffs, dict)
        
        # Validation limits
        assert isinstance(config.dbh_limits, tuple)
        assert len(config.dbh_limits) == 2
        assert config.planted_coefficient > 0
    
    def test_from_database_invalid_species(self):
        """Test that loading invalid species code raises ValueError."""
        with pytest.raises(ValueError, match="Species code .* not found in database"):
            SpeciesConfig.from_database('XX') 
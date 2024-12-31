"""Unit tests for core data structures."""

import pytest
from src.models import Tree, SpeciesConfig

def test_tree_creation():
    """Test basic tree creation."""
    tree = Tree(species_code='LP', dbh=1.0, height=5.0)
    assert tree.species_code == 'LP'
    assert tree.dbh == 1.0
    assert tree.height == 5.0

def test_species_config_creation():
    """Test basic species config creation."""
    config = SpeciesConfig(
        code='LP',
        site_index_range=(50.0, 70.0),
        dbw=5.0
    )
    assert config.code == 'LP'
    assert config.site_index_range == (50.0, 70.0)
    assert config.dbw == 5.0 
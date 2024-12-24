"""Tests for database utilities."""

import pytest
from pathlib import Path
from fvs_core.db_utils import FVSDatabase

@pytest.fixture
def db():
    """Database fixture."""
    with FVSDatabase() as database:
        yield database

def test_get_species_info(db):
    """Test getting species information."""
    # Test with known species
    info = db.get_species_info('FR')
    assert info is not None
    assert info['species_code'] == 'FR'
    assert 'si_min' in info
    assert 'si_max' in info
    
    # Test with unknown species
    info = db.get_species_info('UNKNOWN')
    assert info is None

def test_get_ecological_coefficients(db):
    """Test getting ecological coefficients."""
    # Test with known combination
    coeffs = db.get_ecological_coefficients('FR', 'M221')
    assert coeffs is not None
    assert coeffs['species_code'] == 'FR'
    assert coeffs['fvs_ecounit'] == 'M221'
    
    # Test with unknown combination
    coeffs = db.get_ecological_coefficients('FR', 'UNKNOWN')
    assert coeffs is None

def test_get_forest_type_coefficients(db):
    """Test getting forest type coefficients."""
    # Test with known combination
    coeffs = db.get_forest_type_coefficients('FR', 'FTUPOK')
    assert coeffs is not None
    assert coeffs['species_code'] == 'FR'
    assert coeffs['fvs_fortypcd'] == 'FTUPOK'
    
    # Test with unknown combination
    coeffs = db.get_forest_type_coefficients('FR', 'UNKNOWN')
    assert coeffs is None

def test_get_all_species(db):
    """Test getting all species."""
    species = db.get_all_species()
    assert isinstance(species, list)
    assert len(species) > 0
    assert 'FR' in species

def test_get_all_forest_types(db):
    """Test getting all forest types."""
    types = db.get_all_forest_types()
    assert isinstance(types, list)
    assert len(types) > 0
    assert 'FTUPOK' in types

def test_get_all_ecological_units(db):
    """Test getting all ecological units."""
    units = db.get_all_ecological_units()
    assert isinstance(units, list)
    assert len(units) > 0
    assert 'M221' in units

def test_get_growth_parameters(db):
    """Test getting growth parameters."""
    # Test with known species
    params = db.get_growth_parameters('FR')
    assert params is not None
    assert params['species_code'] == 'FR'
    assert 'CurtisArney_b0' in params
    
    # Test with unknown species
    params = db.get_growth_parameters('UNKNOWN')
    assert params is None

def test_get_scaling_factors(db):
    """Test getting scaling factors."""
    # Test with known species
    factors = db.get_scaling_factors('FR')
    assert factors is not None
    assert factors['species_code'] == 'FR'
    assert 'si_min' in factors
    assert 'si_max' in factors
    
    # Test with unknown species
    factors = db.get_scaling_factors('UNKNOWN')
    assert factors is None 
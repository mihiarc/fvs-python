"""Tests for database utilities."""

import pytest
import sqlite3
from pathlib import Path
from fvs_core.db_utils import FVSDatabase

# Test data constants
TEST_SPECIES = 'FR'
TEST_ECOUNIT = 'M221'
TEST_FOREST_TYPE = 'FTUPOK'
UNKNOWN_CODE = 'UNKNOWN'

# Realistic test data
REALISTIC_SPECIES_DATA = {
    'species_code': TEST_SPECIES,
    'FIA_code': 531,  # Actual FIA code for Fraser Fir
    'si_min': 30,
    'si_max': 120,
    'dbh_min': 1.0,
    'dbh_max': 40.0,
    'growth_transition_dbh_min': 3.0,
    'growth_transition_dbh_max': 6.0,
    'Dbw': 0.9,
    'Bark_b0': 0.1,
    'Bark_b1': 0.2
}

@pytest.fixture
def db_path(tmp_path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_fvspy.db"

@pytest.fixture
def schema_path() -> Path:
    """Get the path to the schema file."""
    return Path("create_tables_v2.sql")

@pytest.fixture
def db(db_path: Path, schema_path: Path):
    """Database fixture that creates a fresh test database."""
    with FVSDatabase(db_path) as database:
        database.create_database(schema_path)
        yield database

def test_database_connection(db_path):
    """Test database connection and context manager."""
    # Test successful connection
    with FVSDatabase(db_path) as db:
        assert db._conn is not None
        assert isinstance(db._conn, sqlite3.Connection)
    assert db._conn is None  # Connection should be closed

    # Test connection error
    with pytest.raises(sqlite3.Error):
        with FVSDatabase("/nonexistent/path/db.sqlite"):
            pass

def test_database_context_manager_with_exception(db_path):
    """Test context manager handles exceptions properly."""
    with pytest.raises(sqlite3.Error):
        with FVSDatabase(db_path) as db:
            assert db._conn is not None
            raise sqlite3.Error("Simulated error")
    assert db._conn is None  # Connection should be closed even after error

def test_create_database(db_path, schema_path):
    """Test database creation and schema validation."""
    with FVSDatabase(db_path) as db:
        db.create_database(schema_path)
        
        # Verify tables exist with correct schema
        cursor = db._conn.cursor()
        
        # Check tables exist
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {table[0] for table in tables}
        
        expected_tables = {
            'species', 'height_diameter_coefficients', 'small_tree_coefficients',
            'large_tree_coefficients', 'species_parameters', 'crown_ratio_coefficients',
            'forest_types', 'ecological_units', 'ecological_coefficients',
            'ecological_species_adjustments', 'forest_type_coefficients',
            'forest_type_species_adjustments'
        }
        
        assert expected_tables.issubset(table_names)
        
        # Check schema for key tables
        species_info = cursor.execute("PRAGMA table_info(species)").fetchall()
        assert any(col[1] == 'species_code' and col[2] == 'TEXT(2)' for col in species_info)
        assert any(col[1] == 'FIA_code' and col[2] == 'INTEGER' for col in species_info)

def test_get_species_info(db):
    """Test getting species information."""
    # Insert test data
    db._conn.execute(
        "INSERT INTO species (species_code, FIA_code) VALUES (?, ?)",
        (REALISTIC_SPECIES_DATA['species_code'], REALISTIC_SPECIES_DATA['FIA_code'])
    )
    db._conn.execute(
        "INSERT INTO species_parameters (species_code, si_min, si_max, dbh_min, dbh_max, "
        "growth_transition_dbh_min, growth_transition_dbh_max, Dbw, Bark_b0, Bark_b1) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (REALISTIC_SPECIES_DATA['species_code'], REALISTIC_SPECIES_DATA['si_min'],
         REALISTIC_SPECIES_DATA['si_max'], REALISTIC_SPECIES_DATA['dbh_min'],
         REALISTIC_SPECIES_DATA['dbh_max'], REALISTIC_SPECIES_DATA['growth_transition_dbh_min'],
         REALISTIC_SPECIES_DATA['growth_transition_dbh_max'], REALISTIC_SPECIES_DATA['Dbw'],
         REALISTIC_SPECIES_DATA['Bark_b0'], REALISTIC_SPECIES_DATA['Bark_b1'])
    )
    db._conn.commit()

    # Test with known species
    info = db.get_species_info(TEST_SPECIES)
    assert isinstance(info, dict)
    assert isinstance(info['species_code'], str)
    assert isinstance(info['FIA_code'], int)
    assert info['species_code'] == TEST_SPECIES
    assert info['FIA_code'] == REALISTIC_SPECIES_DATA['FIA_code']
    assert info['si_min'] == REALISTIC_SPECIES_DATA['si_min']
    assert info['si_max'] == REALISTIC_SPECIES_DATA['si_max']
    
    # Test with unknown species
    info = db.get_species_info(UNKNOWN_CODE)
    assert info is None

def test_get_ecological_coefficients_with_adjustments(db):
    """Test getting ecological coefficients with adjustments."""
    # Insert test data
    db._conn.execute(
        "INSERT INTO ecological_units (fvs_ecounit, fvspy_ecounit) VALUES (?, ?)",
        (TEST_ECOUNIT, 1)
    )
    db._conn.execute(
        "INSERT INTO ecological_coefficients (fvs_ecounit, base_b0, base_b1) VALUES (?, ?, ?)",
        (TEST_ECOUNIT, 1.0, 2.0)
    )
    db._conn.execute(
        "INSERT INTO ecological_species_adjustments (species_code, fvs_ecounit, adjustment_b0, adjustment_b1) "
        "VALUES (?, ?, ?, ?)",
        (TEST_SPECIES, TEST_ECOUNIT, 0.5, 0.5)
    )
    db._conn.commit()

    coeffs = db.get_ecological_coefficients(TEST_SPECIES, TEST_ECOUNIT)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['base_b0'], float)
    assert isinstance(coeffs['adjustment_b0'], float)
    assert isinstance(coeffs['total_b0'], float)
    assert coeffs['base_b0'] == 1.0
    assert coeffs['adjustment_b0'] == 0.5
    assert coeffs['total_b0'] == 1.5

def test_get_ecological_coefficients_no_adjustments(db):
    """Test getting ecological coefficients with no adjustments."""
    # Insert test data without adjustments
    db._conn.execute(
        "INSERT INTO ecological_units (fvs_ecounit, fvspy_ecounit) VALUES (?, ?)",
        (TEST_ECOUNIT, 1)
    )
    db._conn.execute(
        "INSERT INTO ecological_coefficients (fvs_ecounit, base_b0, base_b1) VALUES (?, ?, ?)",
        (TEST_ECOUNIT, 1.0, 2.0)
    )
    db._conn.commit()

    coeffs = db.get_ecological_coefficients(TEST_SPECIES, TEST_ECOUNIT)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['base_b0'], float)
    assert coeffs['adjustment_b0'] is None
    assert isinstance(coeffs['total_b0'], float)
    assert coeffs['base_b0'] == 1.0
    assert coeffs['total_b0'] == 1.0  # Total should equal base when no adjustment

def test_get_forest_type_coefficients_with_adjustments(db):
    """Test getting forest type coefficients with adjustments."""
    # Insert test data
    db._conn.execute(
        "INSERT INTO forest_types (fvs_fortypcd, fvs_fortypcd_name, fia_fortypcd) VALUES (?, ?, ?)",
        (TEST_FOREST_TYPE, "Test Forest Type", 100)
    )
    db._conn.execute(
        "INSERT INTO forest_type_coefficients (fvs_fortypcd, base_lohd, base_nohd) VALUES (?, ?, ?)",
        (TEST_FOREST_TYPE, 1.0, 2.0)
    )
    db._conn.execute(
        "INSERT INTO forest_type_species_adjustments (species_code, fvs_fortypcd, adjustment_lohd, adjustment_nohd) "
        "VALUES (?, ?, ?, ?)",
        (TEST_SPECIES, TEST_FOREST_TYPE, 0.5, 0.5)
    )
    db._conn.commit()

    coeffs = db.get_forest_type_coefficients(TEST_SPECIES, TEST_FOREST_TYPE)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['base_lohd'], float)
    assert isinstance(coeffs['adjustment_lohd'], float)
    assert isinstance(coeffs['total_lohd'], float)
    assert coeffs['base_lohd'] == 1.0
    assert coeffs['adjustment_lohd'] == 0.5
    assert coeffs['total_lohd'] == 1.5

def test_get_forest_type_coefficients_no_adjustments(db):
    """Test getting forest type coefficients with no adjustments."""
    # Insert test data without adjustments
    db._conn.execute(
        "INSERT INTO forest_types (fvs_fortypcd, fvs_fortypcd_name, fia_fortypcd) VALUES (?, ?, ?)",
        (TEST_FOREST_TYPE, "Test Forest Type", 100)
    )
    db._conn.execute(
        "INSERT INTO forest_type_coefficients (fvs_fortypcd, base_lohd, base_nohd) VALUES (?, ?, ?)",
        (TEST_FOREST_TYPE, 1.0, 2.0)
    )
    db._conn.commit()

    coeffs = db.get_forest_type_coefficients(TEST_SPECIES, TEST_FOREST_TYPE)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['base_lohd'], float)
    assert coeffs['adjustment_lohd'] is None
    assert isinstance(coeffs['total_lohd'], float)
    assert coeffs['base_lohd'] == 1.0
    assert coeffs['total_lohd'] == 1.0  # Total should equal base when no adjustment

def test_get_all_species(db):
    """Test getting all species."""
    # Insert test data
    db._conn.execute(
        "INSERT INTO species (species_code, FIA_code) VALUES (?, ?), (?, ?)",
        (TEST_SPECIES, 531, 'SP', 110)  # Using real FIA codes
    )
    db._conn.commit()

    species = db.get_all_species()
    assert isinstance(species, list)
    assert len(species) == 2
    assert all(isinstance(code, str) for code in species)
    assert all(len(code) == 2 for code in species)  # Check length constraint
    assert TEST_SPECIES in species
    assert 'SP' in species

def test_get_all_forest_types(db):
    """Test getting all forest types."""
    # Insert test data
    db._conn.execute(
        "INSERT INTO forest_types (fvs_fortypcd, fvs_fortypcd_name, fia_fortypcd) VALUES (?, ?, ?)",
        (TEST_FOREST_TYPE, "Test Forest Type", 100)
    )
    db._conn.commit()

    types = db.get_all_forest_types()
    assert isinstance(types, list)
    assert len(types) == 1
    assert all(isinstance(code, str) for code in types)
    assert TEST_FOREST_TYPE in types

def test_get_all_ecological_units(db):
    """Test getting all ecological units."""
    # Insert test data
    db._conn.execute(
        "INSERT INTO ecological_units (fvs_ecounit, fvspy_ecounit) VALUES (?, ?)",
        (TEST_ECOUNIT, 1)
    )
    db._conn.commit()

    units = db.get_all_ecological_units()
    assert isinstance(units, list)
    assert len(units) == 1
    assert all(isinstance(code, str) for code in units)
    assert TEST_ECOUNIT in units

def test_get_height_diameter_coefficients(db):
    """Test getting height-diameter coefficients."""
    # Insert test data with realistic coefficients
    db._conn.execute(
        "INSERT INTO height_diameter_coefficients (species_code, CurtisArney_b0, CurtisArney_b1, "
        "CurtisArney_b2, Wykoff_b0, Wykoff_b1) VALUES (?, ?, ?, ?, ?, ?)",
        (TEST_SPECIES, 4.5, -6.2, 1.8, 4.7, -0.015)  # Realistic coefficient values
    )
    db._conn.commit()

    coeffs = db.get_height_diameter_coefficients(TEST_SPECIES)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['species_code'], str)
    assert all(isinstance(coeffs[key], float) for key in ['CurtisArney_b0', 'CurtisArney_b1',
                                                        'CurtisArney_b2', 'Wykoff_b0', 'Wykoff_b1'])
    assert coeffs['CurtisArney_b0'] == 4.5
    assert coeffs['Wykoff_b0'] == 4.7

def test_get_small_tree_coefficients(db):
    """Test getting small tree coefficients."""
    # Insert test data with realistic coefficients
    db._conn.execute(
        "INSERT INTO small_tree_coefficients (species_code, b0, b1, b2, b3, b4) VALUES (?, ?, ?, ?, ?, ?)",
        (TEST_SPECIES, 0.5, -0.2, 0.8, 0.3, -0.1)  # Realistic coefficient values
    )
    db._conn.commit()

    coeffs = db.get_small_tree_coefficients(TEST_SPECIES)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['species_code'], str)
    assert all(isinstance(coeffs[key], float) for key in ['b0', 'b1', 'b2', 'b3', 'b4'])
    assert coeffs['b0'] == 0.5
    assert coeffs['b4'] == -0.1

def test_get_large_tree_coefficients(db):
    """Test getting large tree coefficients."""
    # Insert test data with realistic coefficients
    db._conn.execute(
        "INSERT INTO large_tree_coefficients (species_code, b0, b1, b2, b3, b4, b5) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (TEST_SPECIES, 1.2, -0.4, 0.6, 0.2, -0.3, 0.1)  # Realistic coefficient values
    )
    db._conn.commit()

    coeffs = db.get_large_tree_coefficients(TEST_SPECIES)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['species_code'], str)
    assert all(isinstance(coeffs[key], float) for key in ['b0', 'b1', 'b2', 'b3', 'b4', 'b5'])
    assert coeffs['b0'] == 1.2
    assert coeffs['b5'] == 0.1

def test_get_species_parameters(db):
    """Test getting species parameters."""
    # Insert test data with realistic parameters
    db._conn.execute(
        "INSERT INTO species_parameters (species_code, si_min, si_max, dbh_min, dbh_max, "
        "growth_transition_dbh_min, growth_transition_dbh_max, Dbw, Bark_b0, Bark_b1) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (TEST_SPECIES, 30, 120, 1.0, 40.0, 3.0, 6.0, 0.9, 0.1, 0.2)
    )
    db._conn.commit()

    params = db.get_species_parameters(TEST_SPECIES)
    assert isinstance(params, dict)
    assert isinstance(params['species_code'], str)
    assert isinstance(params['si_min'], int)
    assert isinstance(params['si_max'], int)
    assert all(isinstance(params[key], float) for key in ['dbh_min', 'dbh_max',
                                                        'growth_transition_dbh_min',
                                                        'growth_transition_dbh_max',
                                                        'Dbw', 'Bark_b0', 'Bark_b1'])
    assert params['si_min'] == 30
    assert params['si_max'] == 120
    assert params['dbh_min'] == 1.0
    assert params['dbh_max'] == 40.0

def test_get_crown_ratio_coefficients(db):
    """Test getting crown ratio coefficients."""
    # Insert test data with realistic coefficients
    db._conn.execute(
        "INSERT INTO crown_ratio_coefficients (species_code, acr_equation_type, a, b0, b1, c, "
        "d0, d1, d2, sd, Xmin, Xmax) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (TEST_SPECIES, 1, 0.8, 2.5, -0.3, 1.2, 0.4, -0.2, 0.1, 0.15, 0.0, 1.0)  # Realistic values
    )
    db._conn.commit()

    coeffs = db.get_crown_ratio_coefficients(TEST_SPECIES)
    assert isinstance(coeffs, dict)
    assert isinstance(coeffs['species_code'], str)
    assert isinstance(coeffs['acr_equation_type'], int)
    assert all(isinstance(coeffs[key], float) for key in ['a', 'b0', 'b1', 'c', 'd0',
                                                        'd1', 'd2', 'sd', 'Xmin', 'Xmax'])
    assert coeffs['acr_equation_type'] == 1
    assert coeffs['a'] == 0.8
    assert coeffs['sd'] == 0.15
    assert 0.0 <= coeffs['Xmin'] <= coeffs['Xmax'] <= 1.0  # Check range constraints 
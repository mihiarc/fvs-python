"""
Data handling module for FVS Southern Variant.
Provides access to species data and coefficients from the SQLite database.
"""

import sqlite3
from pathlib import Path
import ast
from .site_index import calculate_rsisp, calculate_mgspix, calculate_mgrsi, calculate_sisp
import os

# Database connection
db_path = Path(__file__).parent.parent / 'data/sqlite_databases/fvspy.db'

def dict_factory(cursor, row):
    """Convert SQLite row to dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_connection():
    """Get a connection to the SQLite database with dictionary row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    return conn

def get_db_connection():
    """Get a connection to the SQLite database."""
    db_path = Path(__file__).parent.parent / 'data' / 'sqlite_databases' / 'fvspy.db'
    return sqlite3.connect(db_path)

def get_species_data():
    """
    Gets species data from the SQLite database.
    
    Returns:
        Dictionary mapping species codes to their coefficients.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Configure cursor to return rows as dictionaries
    cursor.row_factory = sqlite3.Row
    
    # Get all species data in one query
    cursor.execute("""
        SELECT 
            s.species_code,
            s.acr_equation_number as equation_number,
            s.a,
            s.b0,
            s.b1,
            s.c,
            s.d0,
            s.d1,
            s.d2,
            ca.dbw,
            ca.curtis_arney_b0,
            ca.curtis_arney_b1,
            ca.curtis_arney_b2
        FROM species_crown_ratio s
        LEFT JOIN curtis_arney_functions ca ON s.species_code = ca.species_code
    """)
    
    # Convert to dictionary
    species_data = {}
    for row in cursor.fetchall():
        row_dict = dict(row)
        species_code = row_dict['species_code']
        print(f"Debug: Row dict for {species_code}:", row_dict)
        species_data[species_code] = row_dict
    
    conn.close()
    return species_data

def get_site_index_groups():
    """Get site index groups from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT site_index_species, mapped_species, site_type, a, b, c, d
            FROM site_index_groups
        """)
        groups = {}
        for row in cursor.fetchall():
            # Parse mapped_species from string representation to set of species
            try:
                row['mapped_species'] = ast.literal_eval(row['mapped_species'])
            except (ValueError, SyntaxError):
                # If parsing fails, treat it as a single species
                row['mapped_species'] = {row['mapped_species']}
            groups[row['site_index_species']] = row
        return groups

def get_species_crown_ratio_data():
    """Get crown ratio coefficients from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT species_code, a, b0, b1, c, d0, d1, d2
            FROM species_crown_ratio
        """)
        return {row['species_code']: row for row in cursor.fetchall()}

# Initialize data from database
species_data = get_species_data()
site_index_groups = get_site_index_groups()
species_crown_ratio_data = get_species_crown_ratio_data()

def calculate_site_index(site_species, site_index_value, target_species):
    """
    Calculate the site index for a target species based on the site index of another species.
    
    Args:
        site_species (str): The species code for which we have a site index
        site_index_value (float): The known site index value
        target_species (str): The species code for which we want to calculate the site index
    
    Returns:
        float: The calculated site index for the target species, or None if calculation is not possible
    """
    # Default to WO if site_species is invalid
    if site_species not in species_data:
        site_species = "WO"
    
    # Return None if target_species is invalid
    if target_species not in species_data:
        return None
        
    # Get site index ranges for both species
    site_sp_data = species_data[site_species]
    target_sp_data = species_data[target_species]
    
    # Find the site index group that contains both species
    matching_group = None
    for group_id, group_data in site_index_groups.items():
        if (site_species == group_data["site_index_species"] or 
            site_species in group_data["mapped_species"]) and \
           (target_species == group_data["site_index_species"] or 
            target_species in group_data["mapped_species"]):
            matching_group = group_data
            break
    
    if not matching_group:
        return None
        
    # Calculate relative site index for site species
    rsisp = calculate_rsisp(
        site_index_value,
        site_sp_data["si_min"],
        site_sp_data["si_max"]
    )
    
    # Calculate modified growth site productivity index
    mgspix = calculate_mgspix(
        rsisp,
        site_sp_data["si_min"],
        site_sp_data["si_max"],
        matching_group["a"],
        matching_group["b"]
    )
    
    # Calculate modified growth relative site index
    mgrsi = calculate_mgrsi(
        mgspix,
        target_sp_data["si_min"],
        target_sp_data["si_max"],
        matching_group["c"],
        matching_group["d"]
    )
    
    # Calculate final site index for target species
    return calculate_sisp(
        mgrsi,
        target_sp_data["si_min"],
        target_sp_data["si_max"]
    )

"""Crown width calculator module.

This module provides the interface between the database and the crown width equations.
It loads the appropriate coefficients and calls the correct equations based on the
species code and equation assignments in the database.
"""

import numpy as np
import pandas as pd
import sqlite3
from pathlib import Path

def calculate_hopkins_index(elevation: float, latitude: float, longitude: float) -> float:
    """Calculate Hopkins index for a tree.
    
    Args:
        elevation: Elevation (feet)
        latitude: Latitude (degrees)
        longitude: Longitude (degrees)
        
    Returns:
        Hopkins index
    """
    return ((elevation - 887) / 100) * 1.0 + (latitude - 39.54) * 4.0 + (-82.52 - longitude) * 1.25

def load_species_coefficients(species_code: str) -> tuple:
    """Load crown width coefficients for a species from fvspy.db.
    
    Args:
        species_code: The species code to look up
        
    Returns:
        Tuple of (forest_grown_eq, forest_coeffs, open_grown_eq, open_coeffs)
    """
    db_path = Path(__file__).parent.parent / "data" / "sqlite_databases" / "fvspy.db"
    
    with sqlite3.connect(db_path) as conn:
        # Load forest-grown coefficients
        query = "SELECT * FROM crown_width_forest_grown WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=[species_code])
        if df.empty:
            raise ValueError(f"No forest-grown crown coefficients found for species {species_code}")
        forest = df.iloc[0]
        forest_eq = int(forest['equation_number'])  # Convert numpy.int64 to Python int
        forest_coeffs = (float(forest['a1']), float(forest['a2']), 
                        None if pd.isna(forest['a3']) else float(forest['a3']),
                        None if pd.isna(forest['a4']) else float(forest['a4']),
                        None if pd.isna(forest['a5']) else float(forest['a5']))
        
        # Load open-grown coefficients
        query = "SELECT * FROM crown_width_open_grown WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=[species_code])
        if df.empty:
            raise ValueError(f"No open-grown crown coefficients found for species {species_code}")
        open_grown = df.iloc[0]
        open_eq = int(open_grown['equation_number'])  # Convert numpy.int64 to Python int
        open_coeffs = (float(open_grown['a1']), float(open_grown['a2']),
                      None if pd.isna(open_grown['a3']) else float(open_grown['a3']))
        
        return (forest_eq, forest_coeffs, open_eq, open_coeffs)

def calculate_forest_grown_crown_width(dbh: float, crown_ratio: float, hopkins_index: float, species_code: str) -> float:
    """Calculate forest-grown crown width for a species.
    
    Args:
        dbh: Tree diameter at breast height (inches)
        crown_ratio: Crown ratio (proportion)
        hopkins_index: Hopkins index
        species_code: Species code for crown equations
        
    Returns:
        Crown width in feet (used in PCC calculations)
    """
    forest_eq, forest_coeffs, _, _ = load_species_coefficients(species_code)
    
    if forest_eq == 1:  # Bechtold equation
        a1, a2, a3, a4, a5 = forest_coeffs
        if dbh >= 5:
            width = a1 + (a2 * dbh)
            if a4 is not None:
                width += (a4 * crown_ratio)
            if a5 is not None:
                width += (a5 * hopkins_index)
            return max(0.0, width)  # Ensure non-negative width
        else:
            width = a1 + (a2 * 5.0)
            if a4 is not None:
                width += (a4 * crown_ratio)
            if a5 is not None:
                width += (a5 * hopkins_index)
            return max(0.0, width * (dbh / 5.0))  # Ensure non-negative width
            
    elif forest_eq == 2:  # Bragg equation
        a1, a2, a3, _, _ = forest_coeffs
        if dbh >= 5:
            width = a1 + (a2 * dbh**a3) if a3 is not None else a1 + (a2 * dbh)
            return max(0.0, width)  # Ensure non-negative width
        else:
            width = (a1 + (a2 * 5.0**a3) if a3 is not None else a1 + (a2 * 5.0)) * (dbh / 5.0)
            return max(0.0, width)  # Ensure non-negative width
    else:
        raise ValueError(f"Unknown forest-grown equation number {forest_eq} for species {species_code}")

def calculate_open_grown_crown_width(dbh: float, species_code: str) -> float:
    """Calculate open-grown crown width for a species.
    
    Args:
        dbh: Tree diameter at breast height (inches)
        species_code: Species code for crown equations
        
    Returns:
        Crown width in feet (used in CCF calculations)
    """
    _, _, open_eq, open_coeffs = load_species_coefficients(species_code)
    
    if open_eq == 1:  # Bechtold equation (open-grown version)
        a1, a2, a3 = open_coeffs
        if dbh >= 3:
            width = a1 + (a2 * dbh)
            if a3 is not None:
                width += (a3 * dbh**2)
            return max(0.0, width)  # Ensure non-negative width
        else:
            width = a1 + (a2 * 3.0)
            if a3 is not None:
                width += (a3 * 3.0**2)
            return max(0.0, width * (dbh / 3.0))  # Ensure non-negative width
            
    elif open_eq == 3:  # Elk equation
        a1, a2, a3 = open_coeffs
        if dbh >= 3:
            width = a1 + (a2 * dbh**a3) if a3 is not None else a1 + (a2 * dbh)
            return max(0.0, width)  # Ensure non-negative width
        else:
            width = (a1 + (a2 * 3.0**a3) if a3 is not None else a1 + (a2 * 3.0)) * (dbh / 3.0)
            return max(0.0, width)  # Ensure non-negative width
            
    elif open_eq == 4:  # Krajicek equation
        a1, a2, _ = open_coeffs
        if dbh >= 3:
            width = a1 + (a2 * dbh)
            return max(0.0, width)  # Ensure non-negative width
        else:
            width = (a1 + (a2 * 3.0)) * (dbh / 3.0)
            return max(0.0, width)  # Ensure non-negative width
            
    elif open_eq == 5:  # Smith equation
        a1, a2, a3 = open_coeffs
        if dbh >= 3:
            width = a1 + (a2 * dbh * 2.54)
            if a3 is not None:
                width += (a3 * (dbh * 2.54)**2) * 3.28084
            return max(0.0, width)  # Ensure non-negative width
        else:
            width = a1 + (a2 * 3.0 * 2.54)
            if a3 is not None:
                width += (a3 * (3.0 * 2.54)**2) * 3.28084
            return max(0.0, width * (dbh / 3.0))  # Ensure non-negative width
    else:
        raise ValueError(f"Unknown open-grown equation number {open_eq} for species {species_code}")

def calculate_crown_area(crown_width: float) -> float:
    """Calculate crown area assuming circular projection.
    
    Args:
        crown_width: Crown width in feet
        
    Returns:
        Crown area in square feet
    """
    return np.pi * (crown_width/2)**2 
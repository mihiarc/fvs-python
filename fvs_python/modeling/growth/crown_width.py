"""Functions for calculating crown width and related metrics.

Crown width is used primarily in calculating Crown Competition Factor (CCF),
which affects crown ratios and tree growth through competition effects.

FVS Southern Variant calculates the maximum crown width for each indiviudal tree
based on individual tree and stand attributes. Crown width for each tree is reported
in the tree list output table and used to calculate percent canopy cover (PCC) and
crown competition factor (CCF) within the model. When available, forest-grown maximum crown
width equations are used to compute PCC and open-grown crown width equations are used to
compute CCF.

The SN variant computes tree crown width using equations {4.4.1} through {4.4.5} in the FVS
user manual. Species equatino assignment and coefficients are shown in 4.4.1 and 4.4.2. for
forest- and open-grown crown width equations, respectively. Equations are numbered
via the FIA species code and the equation number, i.e. the forest grown equation
from Bechtold (2003) assigned to fir as the number: 01201.
"""

import numpy as np
import pandas as pd
import sqlite3
from pathlib import Path

def load_forest_grown_coefficients(species_code: str) -> tuple:
    """Load forest-grown crown width coefficients for a species from fvspy.db.
    
    Args:
        species_code: The species code to look up
        
    Returns:
        Tuple of coefficients (a1, a2, a3, a4, a5)
    """
    db_path = Path(__file__).parent.parent / "data" / "sqlite_databases" / "fvspy.db"
    with sqlite3.connect(db_path) as conn:
        query = "SELECT * FROM crown_width_forest_grown WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=(species_code,))
        if df.empty:
            raise ValueError(f"No forest-grown crown coefficients found for species {species_code}")
        row = df.iloc[0]
        return (row['a1'], row['a2'], row['a3'], row['a4'], row['a5'])

def load_open_grown_coefficients(species_code: str) -> tuple:
    """Load open-grown crown width coefficients for a species from fvspy.db.
    
    Args:
        species_code: The species code to look up
        
    Returns:
        Tuple of coefficients (a1, a2, a3)
    """
    db_path = Path(__file__).parent.parent / "data" / "sqlite_databases" / "fvspy.db"
    with sqlite3.connect(db_path) as conn:
        query = "SELECT * FROM crown_width_open_grown WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=(species_code,))
        if df.empty:
            raise ValueError(f"No open-grown crown coefficients found for species {species_code}")
        row = df.iloc[0]
        return (row['a1'], row['a2'], row['a3'])

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

def calculate_forest_grown_crown_width_bechtold(dbh: float, crown_ratio: float, hopkins_index: float, species_code: str) -> float:
    """Calculate forest-grown crown width using equation 4.4.1 from the 
    FVS SN variant user manual (Bechtold 2003).
    
    Args:
        dbh: Tree diameter at breast height (inches)
        crown_ratio: Crown ratio (proportion)
        hopkins_index: Hopkins index
        species_code: Species code for crown equations

    Returns:
        Crown width in feet (used in PCC calculations)
    """

    # get species-specific coefficients
    a1, a2, a3, a4, a5 = load_forest_grown_coefficients(species_code)

    # for dbh >= 5
    if dbh >= 5:
        return a1 + (a2 * dbh) + (a3 * dbh**2) + (a4 * crown_ratio) + (a5 * hopkins_index)
    # for dbh < 5
    else:
        return (a1 + (a2 * 5.0) + (a3 * 5.0**2) + (a4 * crown_ratio) + (a5 * hopkins_index)) * (dbh / 5.0)

def calculate_forest_grown_crown_width_bragg(dbh: float, species_code: str) -> float:
    """Calculate forest-grown crown width using equation 4.4.2 from the 
    FVS SN variant user manual (Bragg 2001).
    
    Args:
        dbh: Tree diameter at breast height (inches)
        species_code: Species code for crown equations

    Returns:
        Crown width in feet (used in PCC calculations)
    """

    # get species-specific coefficients
    a1, a2, a3 = load_forest_grown_coefficients(species_code)[:3]

    # for dbh >= 5
    if dbh >= 5:
        return a1 + (a2 * dbh**a3)
    # for dbh < 5
    else:
        return (a1 + (a2 * 5.0**a3)) * (dbh / 5.0)
    
def calculate_open_grown_crown_width_elk(dbh: float, species_code: str) -> float:
    """Calculate open-grown crown width using equation 4.4.3 from the 
    FVS SN variant user manual (Elk 2003).
    
    Args:
        dbh: Tree diameter at breast height (inches)
        species_code: Species code for crown equations

    Returns:
        Crown width in feet (used in CCF calculations)
    """

    # get species-specific coefficients
    a1, a2, a3 = load_open_grown_coefficients(species_code)

    # for dbh >= 3
    if dbh >= 3:
        return a1 + (a2 * dbh**a3)
    # for dbh < 3
    else:
        return (a1 + (a2 * 3.0**a3)) * (dbh / 3.0)
    
def calculate_open_grown_crown_width_krajicek(dbh: float, species_code: str) -> float:
    """Calculate open-grown crown width using equation 4.4.4 from the 
    FVS SN variant user manual (Krajicek et al. 1961).
    
    Args:
        dbh: Tree diameter at breast height (inches)
        species_code: Species code for crown equations

    Returns:
        Crown width in feet (used in CCF calculations)
    """

    # get species-specific coefficients
    a1, a2 = load_open_grown_coefficients(species_code)[:2]

    # for dbh >= 3
    if dbh >= 3:
        return a1 + (a2 * dbh)
    # for dbh < 3
    else:
        return (a1 + (a2 * 3.0)) * (dbh / 3.0)

def calculate_open_grown_crown_width_smith(dbh: float, species_code: str) -> float:
    """Calculate open-grown crown width using equation 4.4.5 from the 
    FVS SN variant user manual (Smith et al. 1992).
    
    Args:
        dbh: Tree diameter at breast height (inches)
        species_code: Species code for crown equations

    Returns:
        Crown width in feet (used in CCF calculations)
    """

    # get species-specific coefficients
    a1, a2, a3 = load_open_grown_coefficients(species_code)

    # for dbh >= 3
    if dbh >= 3:
        return a1 + (a2 * dbh * 2.54) + (a3 * (dbh * 2.54)**2) * 3.28084
    # for dbh < 3
    else:
        return (a1 + (a2 * 3.0 * 2.54) + (a3 * (3.0 * 2.54)**2) * 3.28084) * (dbh / 3.0)


def calculate_crown_area(crown_width: float) -> float:
    """Calculate crown area assuming circular projection.
    
    Args:
        crown_width: Crown width in feet
        
    Returns:
        Crown area in square feet
    """
    return np.pi * (crown_width/2)**2

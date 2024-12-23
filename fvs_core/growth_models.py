"""
Growth module for FVS Southern Variant.
Implements height-diameter relationships and other growth-related functions.
"""

import math
from pathlib import Path
import pandas as pd

# Read species coefficients from CSV
data_dir = Path(__file__).parent.parent / 'data'
df = pd.read_csv(data_dir / 'species_data.csv')
species_data = df.set_index('species_code').to_dict('index')

def curtis_arney_height(dbh, species, coefficients=None):
    """
    Calculate tree height using the Curtis-Arney equation (4.1.1).
    
    Args:
        dbh (float): Diameter at breast height in inches
        species (str): Species code
        coefficients (dict, optional): Override default coefficients
    
    Returns:
        float: Estimated tree height in feet
    """
    if coefficients is None:
        if species not in species_data:
            raise ValueError(f"Unknown species code: {species}")
        coefficients = species_data[species]
    
    b0 = coefficients['CurtisArney_b0']
    b1 = coefficients['CurtisArney_b1']
    b2 = coefficients['CurtisArney_b2']
    
    if dbh < 3.0:
        # Special calculation for small trees
        dbw = coefficients.get('Dbw', 0.2)  # Default to 0.2 if not specified
        return ((4.51 + b0 * math.exp(-b1 * 3**b2) - 4.51) * (dbh - dbw) / (3 - dbw)) + 4.51
    else:
        # Standard calculation for larger trees dbh >= 3 inches
        return 4.51 + b0 * math.exp(-b1 * dbh**b2)

def wykoff_height(dbh, species, coefficients=None):
    """
    Calculate tree height using the Wykoff equation (4.1.2).
    This is an optional alternative to Curtis-Arney that can be calibrated to local data.
    
    Args:
        dbh (float): Diameter at breast height in inches
        species (str): Species code
        coefficients (dict, optional): Override default coefficients
    
    Returns:
        float: Estimated tree height in feet
    """
    if coefficients is None:
        if species not in species_data:
            raise ValueError(f"Unknown species code: {species}")
        coefficients = species_data[species]
    
    b0 = coefficients['Wykoff_b0']
    b1 = coefficients['Wykoff_b1']
    
    # Logistic equation form; used only for larger trees
    return 4.51 + math.exp(b0 + b1 / (dbh + 1))

def calculate_inside_bark_dbh_ratio(dob, species, coefficients=None):
    """Calculates inside-bark diameter using a bark ratio.

    Bark ratio estimates are used to convert between diameter
    outside bark and diameter inside bark in various parts of
    the model. The coefficients are based on the species and
    derived in Clark (1991).

    Args:
        dob: tree diameter outside bark at breast height
        species: species code
        coefficients: species-specific coefficients

    Returns:
        bratio: species-specific bark ratio 
        (bounded to 0.80 <= bratio <= 0.99)
    """
    if coefficients is None:
        if species not in species_data:
            raise ValueError(f"Unknown species code: {species}")
        coefficients = species_data[species]
    
    b0 = coefficients['Bark_b0']
    b1 = coefficients['Bark_b1']
    bratio = (b0 + b1 * (dob)) / dob
    return max(0.80, min(bratio, 0.99))

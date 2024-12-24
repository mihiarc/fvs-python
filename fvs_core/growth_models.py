"""
Growth module for FVS Southern Variant.
Implements height-diameter relationships and other growth-related functions.
"""

import math
from pathlib import Path
import pandas as pd
import numpy as np

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

import numpy as np
import random

def calculate_small_tree_height_growth(si, aget, c1, c2, c3, c4, c5, ht=None, random_error_sd=0.1, user_adjustment=0, calibration_adjustment=0): #Added parameters for adjustments and random error
    """Calculates small tree height growth using the Chapman-Richards function.
    Equation 4.6.1.1 in the FVS Southern Variant User's Guide.

    Args:
        si: species-specific site index.
        aget: Tree age.
        c1-c5: Species-specific coefficients.
        ht: tree height in feet.
        random_error_sd: Standard deviation of the random error.
        user_adjustment: User-defined height growth adjustment.
        calibration_adjustment: Adjustment due to calibration.

    Returns:
        Predicted tree height. Used for current and future height growth.
    """
    if ht is None:
        potht = c1 * si**c2 * (1.0 - np.exp(c3 * aget))**(c4 * (si**c5))
    else:
        aget = (1/c3)*np.log(1-(ht/c1/si**c2)**(1/c4/si**c5))
        potht = c1 * si**c2 * (1.0 - np.exp(c3 * (aget+5)))**(c4 * (si**c5))
    
    #Add random error
    potht += random.gauss(0, random_error_sd)
    
    potht += user_adjustment + calibration_adjustment
    return potht

def calculate_growth_weight(dbh, xmin, xmax):
    """Calculates the weight for blending small and large tree growth estimates.
    Equation 4.6.1.2 in the FVS Southern Variant User's Guide.

    Args:
        dbh: Diameter at breast height (in inches).
        xmin: Minimum diameter for small tree growth. set to 3.0 inches.
        xmax: Maximum diameter for large tree growth. set to 1.0 inches.

    Returns:
        The weight for blending small and large tree growth estimates.
    """
    
    if dbh < xmin:
        xwt = 0
    elif dbh > xmax:
        xwt = 1
    else:
        xwt = (dbh - xmin) / (xmax - xmin)
    return xwt

def blend_growth_estimates(xwt, stge, ltge):
    """Blends small and large tree growth estimates using the calculated weight.
    Equation 4.6.1.3 in the FVS Southern Variant User's Guide.

    Args:
        xwt: Weight for blending small and large tree growth estimates.
        stge: Small tree growth estimate obtained from calculate_small_tree_height_growth.
        ltge: Large tree growth estimate obtained from calculate_large_tree_diameter_growth.

    Returns:
        The blended growth estimate.
    """
    return (1 - xwt) * stge + xwt * ltge

def calculate_large_tree_diameter_growth(dbh, cr, relht, si, ba, pbal, slope, aspect, fortype, ecounit, plant, b_coeffs):
    """Calculates large tree diameter growth (ln(DDS)).
    Equation 4.7.1.1 in the FVS Southern Variant User's Guide.
    Args:
        dbh: Diameter at breast height (in inches).
        cr: Crown ratio (as a percentage, 0.0-100.0).
        relht: Relative height of the subject tree to the top height of the stand.
        si: species-specific site index.
        ba: Stand basal area per acre (square feet per acre).
        pbal: Plot basal area in larger trees.
        slope: Stand slope (scaled 0-1).
        aspect: Stand aspect in radians.
        fortype: Forest type group coefficient. tables 4.7.1.3 and 4.7.1.4
        ecounit: Ecological unit group dependent coefficient. tables 4.7.1.5 and 4.7.1.6
        plant: Managed pine stand coefficient. table 4.7.1.7
        b_coeffs: Species-specific coefficients. tables 4.7.1.1 and 4.7.1.2

    Returns:
        The natural log of the 5-year periodic change in squared inside-bark diameter (ln(DDS)).
    """

    ln_dds = (b_coeffs["b1"] + (b_coeffs["b2"] * np.log(dbh)) + (b_coeffs["b3"] * dbh**2) +
              (b_coeffs["b4"] * np.log(cr)) + (b_coeffs["b5"] * relht) + (b_coeffs["b6"] * si) +
              (b_coeffs["b7"] * ba) + (b_coeffs["b8"] * pbal) + (b_coeffs["b9"] * slope) +
              (b_coeffs["b10"] * np.cos(aspect) * slope) + (b_coeffs["b11"] * np.sin(aspect) * slope) +
              fortype + ecounit + plant)

    return ln_dds

def apply_diameter_growth_bounding(dbh, diameter_growth, lower_limit, upper_limit):
    """Applies the diameter growth bounding function.
    Equation 4.7.1.3 in the FVS Southern Variant User's Guide.
    
    Args:
        dbh: Diameter at breast height (in inches).
        diameter_growth: Original calculated diameter growth (in inches).
        lower_limit: Lower diameter bounding limit (in inches).
        upper_limit: Upper diameter bounding limit (in inches).

    Returns:
        Adjusted diameter growth (in inches).
    """
    if lower_limit == 998: #Bounding turned off
        return diameter_growth
    elif dbh > lower_limit and dbh <= upper_limit:
        dgbmod = max(1.0 + 0.9 * ((dbh - lower_limit) / (lower_limit - upper_limit)), 0.048)
        adjusted_growth = diameter_growth * dgbmod
        return adjusted_growth
    elif dbh > upper_limit:
        return 0.048
    else:
        return diameter_growth  # No bounding needed
    
def calculate_diameter_growth_from_dds(dbh_ib, ln_dds):
    """Calculates diameter growth from ln(DDS).
    Args:
        dbh_ib: Inside-bark diameter (in inches).
        ln_dds: The natural log of the periodic change in squared inside-bark diameter (ln(DDS)).
    Returns:
        Diameter growth (in inches) over the period
    """
    dds = np.exp(ln_dds)
    dbh_ib_new_squared = dbh_ib**2 + dds
    dbh_ib_new = np.sqrt(dbh_ib_new_squared)
    diameter_growth = dbh_ib_new - dbh_ib
    return diameter_growth
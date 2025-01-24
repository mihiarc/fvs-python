"""
Growth module for FVS Southern Variant.
Implements height-diameter relationships and other growth-related functions.
"""

import math
import numpy as np

# Test data for southern yellow pines
species_data = {
    'SP': {  # Shortleaf Pine
        'CurtisArney_b0': 444.0921666,
        'CurtisArney_b1': 4.11876312,
        'CurtisArney_b2': -0.30617043,
        'Dbw': 0.5,
        'Wykoff_b0': 4.6271,
        'Wykoff_b1': -6.4095
    },
    'SA': {  # Slash Pine
        'CurtisArney_b0': 1087.101439,
        'CurtisArney_b1': 5.10450596,
        'CurtisArney_b2': -0.24284896,
        'Dbw': 0.5,
        'Wykoff_b0': 4.6561,
        'Wykoff_b1': -6.2258
    },
    'LL': {  # Longleaf Pine
        'CurtisArney_b0': 98.56082813,
        'CurtisArney_b1': 3.89930709,
        'CurtisArney_b2': -0.86730393,
        'Dbw': 0.5,
        'Wykoff_b0': 4.5991,
        'Wykoff_b1': -5.9111
    },
    'LP': {  # Loblolly Pine
        'CurtisArney_b0': 243.860648,
        'CurtisArney_b1': 4.28460566,
        'CurtisArney_b2': -0.47130185,
        'Dbw': 0.5,
        'Wykoff_b0': 4.6897,
        'Wykoff_b1': -6.8801
    }
}

def curtis_arney_height(dbh, species, coefficients=None):
    """
    Calculate tree height using the Curtis-Arney equation.
    
    Args:
        dbh (float): Diameter at breast height in inches
        species (str): Species code
        coefficients (dict, optional): Override default coefficients
    
    Returns:
        float: Estimated tree height in feet
    """
    if coefficients is None:
        raise ValueError("Coefficients are required")
    
    p2 = coefficients['p2']
    p3 = coefficients['p3']
    p4 = coefficients['p4']
    
    if dbh < 3.0:
        # Special calculation for small trees
        dbw = coefficients.get('Dbw', 0.2)  # Default to 0.2 if not specified
        # Calculate height at dbh=3.0 for interpolation
        h3 = 4.51 + p2 * math.exp(-p3 * 3**p4)
        # Linear interpolation between breast height and h3
        return 4.51 + (h3 - 4.51) * (dbh - dbw) / (3 - dbw)
    else:
        # Standard calculation for larger trees dbh >= 3 inches
        return 4.51 + p2 * math.exp(-p3 * dbh**p4)

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

def calculate_small_tree_height_growth(si, aget, ht, c1, c2, c3, c4, c5):
    """
    Calculate small tree height growth using the Chapman-Richards function.
    
    Args:
        si: Site index (base age 25)
        aget: Tree age
        ht: Current height (feet)
        c1-c5: Species-specific coefficients
    
    Returns:
        float: Predicted height growth (feet)
    """
    if ht is None:
        potht = c1 * si**c2 * (1.0 - np.exp(c3 * aget))**(c4 * (si**c5))
    else:
        # Calculate age from current height
        aget = (1/c3) * np.log(1-(ht/c1/si**c2)**(1/c4/si**c5))
        # Project height 5 years forward
        potht = c1 * si**c2 * (1.0 - np.exp(c3 * (aget+5)))**(c4 * (si**c5))
    
    return potht - (ht if ht is not None else 0)

def calculate_growth_weight(dbh, xmin, xmax):
    """
    Calculate weight for blending small and large tree growth estimates.
    
    Args:
        dbh: Diameter at breast height (inches)
        xmin: Minimum diameter for transition (typically 2.0)
        xmax: Maximum diameter for transition (typically 3.0)
    
    Returns:
        float: Weight between 0 (small tree) and 1 (large tree)
    """
    if dbh < xmin:
        return 0
    elif dbh > xmax:
        return 1
    else:
        return (dbh - xmin) / (xmax - xmin)

def blend_growth_estimates(weight, small_growth, large_growth):
    """
    Blend small and large tree growth estimates.
    
    Args:
        weight: Weight from calculate_growth_weight
        small_growth: Growth estimate from small tree model
        large_growth: Growth estimate from large tree model
    
    Returns:
        float: Blended growth estimate
    """
    return (1 - weight) * small_growth + weight * large_growth

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

def calculate_bark_thickness(dbh: float, a: float, b: float) -> float:
    """Calculate bark thickness using species-specific coefficients.
    
    Args:
        dbh: Diameter at breast height (inches)
        a: Species-specific coefficient a
        b: Species-specific coefficient b
        
    Returns:
        Bark thickness in inches
    """
    return a + b * dbh

def calculate_inside_bark_dbh(dbh: float, bark_thickness: float) -> float:
    """Calculate inside bark diameter from outside bark diameter and bark thickness.
    
    Args:
        dbh: Outside bark diameter at breast height (inches)
        bark_thickness: Bark thickness (inches)
        
    Returns:
        Inside bark diameter (inches)
    """
    return dbh - 2 * bark_thickness

def curtis_arney(dbh: float, b0: float, b1: float, b2: float) -> float:
    """Calculate tree height using the Curtis-Arney equation.
    
    Args:
        dbh: Diameter at breast height (inches)
        b0: Species-specific coefficient b0
        b1: Species-specific coefficient b1
        b2: Species-specific coefficient b2
        
    Returns:
        Tree height in feet
    """
    if dbh < 3.0:
        # Special calculation for small trees
        return 4.51 + (b0 * np.exp(-b1 * 3**b2) - 4.51) * (dbh - 0.2) / (3 - 0.2)
    else:
        # Standard calculation for larger trees
        return 4.51 + b0 * np.exp(-b1 * dbh**b2)
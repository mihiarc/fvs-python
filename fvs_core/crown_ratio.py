import numpy as np
from scipy.stats import weibull_min
import random
from fvs_core import data_handling

# Crown ratio equations are used for the three purposes in FVS: (1) to estimate tree crown 
# ratios missing from the input data for for both live and dead trees, (2) to estimate
# change in crown ratio from cycle to cycle for live trees; and (3) to estimate initial crown 
# ratios for regernerating trees established during a simulation.

# A Weibull-based crown model developed by Dixon (1985) as described in Dixon (2002) is used
# to predict crown ratio for all live trees. To estimate crown ratio using this methodology,
# the average crown ratio (acr) is estimated from stand density index using one of the five
# equations in this module. 

def calculate_dubbed_crown_ratio(dbh, sd):
    """
    In the SN variant, crown ratio missing on dead trees in the input data is dubbed
    using this equation. Piecewise equations are used based on dbh > 24in or <= 24in.

    Args:
        dbh: diameter at breast height
        sd: standard deviation of the normal distribution

    Returns:
        crown ratio
    """
    if dbh < 24:
        x = 0.70 - (0.40 / 24.0) * dbh
    else:
        x = 0.30
    cr = 1 / (1 + np.exp(x + random.gauss(0, sd)))  # N(0, SD) is implemented with random.gauss
    return max(0.05, min(0.95, cr))

def calculate_acr(relsdi, species):
    """
    Calculates the average crown ratio (ACR) using one of five equation types.
    The equation type is determined by acr_equation_number in the database.
    
    The five equation types are:
    1. acr = exp(d0 + d1*ln(relsdi) + d2*relsdi)
    2. acr = exp(d0 + d1*ln(relsdi))
    3. acr = (d0 + d2*relsdi)/100
    4. acr = d0 + d1*log10(relsdi)
    5. acr = relsdi/(d0*relsdi + d1)
    
    Args:
        relsdi: relative stand density index ((Stand SDI / Maximum SDI) *10) and is between 1.0 and 12.0
        species: species code
        
    Returns:
        average crown ratio between 0 and 1
        
    Raises:
        KeyError: if species code is not found in the database
        ValueError: if equation type is invalid or required coefficients are missing
    """
    if species not in data_handling.species_data:
        raise KeyError(f"Species code '{species}' not found in crown ratio data")
        
    coeffs = data_handling.species_data[species]
    print(f"Debug: coeffs for {species}:", coeffs)
    
    # Get equation number and coefficients
    equation_number = coeffs.get('equation_number')
    if equation_number is None:
        raise ValueError(f"Missing equation number for species {species}")
    
    d0 = coeffs.get('d0')
    d1 = coeffs.get('d1')
    d2 = coeffs.get('d2')
    
    # Calculate ACR based on equation type
    if equation_number == 1:
        if any(x is None for x in [d0, d1, d2]):
            raise ValueError(f"Missing coefficients for equation 1 (species {species})")
        raw_acr = np.exp(d0 + (d1 * np.log(relsdi)) + (d2 * relsdi)) / 100.0
        print(f"Debug: Species {species} eq1 - raw_acr before bounds: {raw_acr:.3f}")
        acr = raw_acr
    elif equation_number == 2:
        if any(x is None for x in [d0, d1]):
            raise ValueError(f"Missing coefficients for equation 2 (species {species})")
        raw_acr = np.exp(d0 + (d1 * np.log(relsdi))) / 100.0
        print(f"Debug: Species {species} eq2 - raw_acr before bounds: {raw_acr:.3f}")
        acr = raw_acr
    elif equation_number == 3:
        if any(x is None for x in [d0, d2]):
            raise ValueError(f"Missing coefficients for equation 3 (species {species})")
        raw_acr = (d0 + (d2 * relsdi)) / 100.0
        print(f"Debug: Species {species} eq3 - raw_acr before bounds: {raw_acr:.3f}")
        acr = raw_acr
    elif equation_number == 4:
        if any(x is None for x in [d0, d1]):
            raise ValueError(f"Missing coefficients for equation 4 (species {species})")
        raw_acr = (d0 + (d1 * np.log10(relsdi))) / 100.0
        print(f"Debug: Species {species} eq4 - raw_acr before bounds: {raw_acr:.3f}")
        acr = raw_acr
    elif equation_number == 5:
        if any(x is None for x in [d0, d1]):
            raise ValueError(f"Missing coefficients for equation 5 (species {species})")
        raw_acr = relsdi / ((d0 * relsdi) + d1)  # Already a proportion
        print(f"Debug: Species {species} eq5 - raw_acr before bounds: {raw_acr:.3f}")
        acr = raw_acr
    else:
        raise ValueError(f"Invalid equation number {equation_number} for species {species}")
        
    # Ensure ACR is between 0 and 1
    return max(0.05, min(0.95, acr))

def calculate_crown_ratio_weibull(x, species, acr, scale):
    """
    Calculates crown ratio using the Weibull distribution. The crown ratio is expressed
    as a percentage of total height. The Weibull parameters are derived from species-specific
    coefficients (a, b0, b1, c) and the average crown ratio (acr).
    
    The Weibull parameters are:
    - location (a) = a0/100
    - scale (b) = max(0.03, (b0 + b1*acr)/100)
    - shape (c) = max(2.0, c0)
    
    These parameters are then scaled by the density-dependent factor before calculating
    the final crown ratio using the Weibull percent point function.

    Args:
        x: is a tree's rank in the diameter distribution (1 = smallest; ITRN = largest)
            divided by the total number of trees (ITRN) multiplied by scale; bounded between 0.05 and 0.95
        species: species code for getting Weibull parameters
        acr: average crown ratio calculated from calculate_acr
        scale: density-dependent scaling factor between 0.3 and 1.0

    Returns:
        y: a tree's crown ratio expressed as a percent of total height
        
    Raises:
        KeyError: if species code is not found in the database
    """
    if species not in data_handling.species_data:
        raise KeyError(f"Species code '{species}' not found in crown ratio data")
        
    coeffs = data_handling.species_data[species]
    
    # Get Weibull parameters from coefficients
    a, b, c = calculate_weibull_parameters(
        acr,
        coeffs['a'],
        coeffs['b0'],
        coeffs['b1'],
        coeffs['c']
    )
    
    # Scale the input crown ratio and ensure it's between 0 and 1
    x = max(0.0001, min(0.9999, x))  # Avoid 0 and 1 which can cause numerical issues
    
    try:
        # Calculate the Weibull-based crown ratio
        # First apply the scale factor to the parameters
        a_scaled = a * scale
        b_scaled = b * scale
        
        # Then use the percent point function (inverse CDF) of the Weibull distribution
        cr = weibull_min.ppf(x, c, loc=a_scaled, scale=b_scaled)
    except ValueError as e:
        # If there's an error with the Weibull calculation, return the input x
        print(f"Warning: Weibull calculation failed for species {species}: {e}")
        cr = x
    
    # Apply bounds
    return max(0.05, min(0.95, cr))

def calculate_weibull_parameters(acr, a0, b0, b1, c0):
    """
    Calculates Weibull distribution parameters for crown ratio calculation.
    
    The parameters are:
    - location (a) = a0/100                          (converts to proportion)
    - scale (b) = max(0.03, (b0 + b1*acr))          (minimum bound)
    - shape (c) = max(2.0, c0)                       (ensures minimum shape parameter)
    
    Args:
        acr: average crown ratio between 0 and 1
        a0: location parameter coefficient
        b0: scale parameter intercept coefficient
        b1: scale parameter slope coefficient
        c0: shape parameter coefficient
        
    Returns:
        tuple of (a, b, c) parameters for the Weibull distribution
    """
    a = a0 / 100.0  # Convert to proportion
    b = max(0.03, b0 + b1 * acr)  # Apply minimum bound
    c = max(2.0, c0)  # Bound only
    return a, b, c

def calculate_scale(ccf):
    """
    Calculates the density-dependent scaling factor.
    
    Args:
        ccf: crown competition factor
        
    Returns:
        scaling factor between 0.3 and 1.0
    """
    scale = 1 - 0.00167 * (ccf - 100)
    return max(0.3, min(1.0, scale))

def calculate_crown_ratio_change(current_cr, new_cr):
    """
    Calculates the change in crown ratio.
    
    Args:
        current_cr: current crown ratio
        new_cr: new crown ratio
        
    Returns:
        change in crown ratio
    """
    return new_cr - current_cr
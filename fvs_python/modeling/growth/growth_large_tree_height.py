# In the SN variant, the large tree heigh growth model follows the approach of Wensel
# et al. (1987) where the potential height growth is calculated for every tree and modified
# based on indifivudal tree crown ration and rlative height in the stand using equation {4.7.2.1}.
# POtential height growth is calculated using the methodology described in the small-tree height 
# increment model.

# The crown ration modifying function uses Hoerl's Special Function (HSF) form (Cuthbert and
# Wood 1971, p. 23) identified in euqation {4.7.2.2} with a range of 0.0 to 1.0. The a-c 
# parameters are chosen so that height growth is maximized for crown ratios between 45 and 75%.

# The relative height modifying function (HGMDRH) is based on the height of the tree record 
# compared to the top height of the stand, adjusted for shade tolerance. The modifying function 
# is based on the Generalized Chapman-Richards function (Donnelly and Betters 1991, Donnelly 
# and others 1992, and Pienaar and Turnbull 1973), whose parameters are set to attenuate 
# height growth based on relative height and shade tolerance, see equation {4.7.2.3} – {4.7.2.7}. 
# Coefficients for these equations are shown in tables 4.7.2.1 and 4.7.2.2. The modifier value 
# (HGMDRH) decreases with decreasing relative height and species intolerance with a range 
# between 0.0 and 1.0. Height growth reaches an upper asymptote of 1.0 at a relative height of 
# 1.0 for intolerant species and 0.7 for tolerant species. 

import numpy as np

def large_tree_periodic_height_growth(pothtg, hgmdcr, hgmdrh):
    """
    Calculates the periodic height growth for large trees using the Wensel et al. (1987) model.
    Equation {4.7.2.1} from the SN variant.

    Args:
        pothtg (float): The potential height growth for the tree. (sec. 4.6.1)
        hgmdcr (float): The crown ratio modifier (bounded to hgmdcr < 1.0)
        hgmdrh (float): The relative height modifier

    Returns:
        float: The periodic height growth for the tree.
    """
    return pothtg * (0.25 * hgmdcr + 0.75 * hgmdrh)

def large_tree_crown_ratio_modifier(cr):
    """
    Calculates the crown ratio modifier using Hoerl's Special Function (HSF) form.
    Equation {4.7.2.2} from the SN variant.

    Args:
        cr (float): The crown ratio of the tree as a proportion of the total height.

    Returns:
        hgmdcr (float): The crown ratio modifier (bounded to hgmdcr < 1.0)
    """
    return 100 * cr**3 * np.exp(-5*cr)

def large_tree_relative_height_modifier(relht, rhk, rhyxs, rhxs, rhr, rhb, rhm):
    """
    Calculates the relative height modifier using the Generalized Chapman-Richards function.
    Equation {4.7.2.3} from the SN variant.

    Args:
        relht (float): The height of the tree record relative to the top height of the stand.
        rhk (float): shade tolerance coefficient
        rhyxs (float): shade tolerance coefficient
        rhxs (float): shade tolerance coefficient
        rhr (float): shade tolerance coefficient
        rhb (float): shade tolerance coefficient
        rhm (float): shade tolerance coefficient

    Returns:
        float: The relative height modifier.
    """

    fctrkx = ((rhk / rhyxs)**(rhm - 1)) - 1
    fctrrb = (-1.0 * rhr) / (1 - rhb)
    fctrxb = relht**(1 - rhb) - rhxs**(1 - rhb)
    fctrm = 1 / (1 - rhm)
    
    return rhk * (1 + fctrkx * np.exp(fctrrb*fctrxb))**fctrm
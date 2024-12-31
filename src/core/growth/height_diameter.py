"""Height-diameter relationship equations.

This module implements various height-diameter relationships used in the forest growth
simulator, including the Curtis-Arney equation which is the primary method for
southern yellow pines.
"""

import math
from typing import Dict, Union, Optional

def curtis_arney_height(dbh: float, coeffs: Dict[str, float]) -> float:
    """Calculate total tree height using the Curtis-Arney equation.
    
    The Curtis-Arney equation is the primary height-diameter relationship for southern
    yellow pines. The equation form is:
        H = 4.51 + b0 * exp(-b1 * D^b2)
    where:
        H = total tree height in feet
        D = diameter at breast height (DBH) in inches
        b0, b1, b2 = species-specific coefficients
    
    For small trees (DBH < 3.0 inches), a linear interpolation is used between
    breast height (4.51 feet) and the height predicted at DBH = 3.0 inches.
    
    Args:
        dbh: Diameter at breast height in inches
        coeffs: Dictionary containing Curtis-Arney coefficients:
            - 'CurtisArney_b0': Asymptotic maximum height minus 4.51
            - 'CurtisArney_b1': Rate parameter
            - 'CurtisArney_b2': Shape parameter (typically negative)
            - 'Dbw': Diameter breakpoint (optional, defaults to 0.2)
    
    Returns:
        Total tree height in feet
    
    Raises:
        ValueError: If dbh is not positive or if required coefficients are missing
        
    Example:
        >>> coeffs = {
        ...     'CurtisArney_b0': 243.860648,
        ...     'CurtisArney_b1': 4.28460566,
        ...     'CurtisArney_b2': -0.47130185
        ... }
        >>> curtis_arney_height(10.0, coeffs)
        52.3  # Example output
    """
    # Validate inputs
    if dbh <= 0:
        raise ValueError(f"DBH must be positive, got {dbh}")
    
    required_coeffs = ['CurtisArney_b0', 'CurtisArney_b1', 'CurtisArney_b2']
    missing_coeffs = [c for c in required_coeffs if c not in coeffs]
    if missing_coeffs:
        raise ValueError(f"Missing required coefficients: {missing_coeffs}")
    
    # Extract coefficients
    b0 = coeffs['CurtisArney_b0']
    b1 = coeffs['CurtisArney_b1']
    b2 = coeffs['CurtisArney_b2']
    dbw = coeffs.get('Dbw', 0.2)  # Default to 0.2 if not specified
    
    def calculate_height(d: float) -> float:
        """Helper function to calculate height for a given diameter."""
        return 4.51 + b0 * math.exp(-b1 * d**b2)
    
    if dbh < 3.0:
        # Special calculation for small trees
        if dbh <= dbw:
            return 4.51  # At or below the diameter breakpoint, height is breast height
        
        # Calculate height at dbh=3.0 for interpolation
        h3 = calculate_height(3.0)
        # Linear interpolation between breast height and h3
        return 4.51 + (h3 - 4.51) * (dbh - dbw) / (3.0 - dbw)
    else:
        # Standard calculation for larger trees
        return calculate_height(dbh) 
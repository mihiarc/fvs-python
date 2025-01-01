"""Functions for calculating tree and stand volumes."""

def calculate_tree_volume(species: str, dbh: float, height: float, b0: float, b1: float, b2: float) -> float:
    """Calculate the volume of a tree using a generalized volume equation.
    
    This is a simplified version of the volume equation used in FVS.
    Volume = b0 * (DBH^b1) * (Height^b2)
    
    Args:
        species: Species code
        dbh: Diameter at breast height (inches)
        height: Total tree height (feet)
        b0: Species-specific volume equation coefficient
        b1: Species-specific DBH exponent
        b2: Species-specific height exponent
        
    Returns:
        Tree volume in cubic feet
    """
    if dbh <= 0 or height <= 0:
        return 0.0
        
    volume = b0 * (dbh ** b1) * (height ** b2)
    return max(0.0, volume)  # Ensure non-negative volume 
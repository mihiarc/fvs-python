import numpy as np

def calculate_stand_metrics(stand):
    """Calculate stand-level metrics.
    
    Args:
        stand: List of tree objects
        
    Returns:
        Dictionary containing stand metrics
    """
    # Calculate basic metrics
    dbhs = [tree.dbh for tree in stand]
    heights = [tree.height for tree in stand]
    tpa = sum(tree.trees_per_acre for tree in stand)
    
    # Calculate basal area (sq ft/acre)
    basal_area = sum((np.pi * (tree.dbh/2)**2 * tree.trees_per_acre) / 144 for tree in stand)
    
    # Return metrics dictionary
    return {
        'avg_dbh': np.mean(dbhs),
        'avg_height': np.mean(heights),
        'basal_area': basal_area,
        'trees_per_acre': tpa
    } 
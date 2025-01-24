import pandas as pd
import numpy as np
import random
import sqlite3
from pathlib import Path
from .fia_utils import FIADatabase
from ..src import crown_ratio
from ..src import growth_models

def load_growth_coefficients(species_code: str) -> dict:
    """Load growth coefficients for a species from fvspy.db.
    
    Args:
        species_code: The species code to look up
        
    Returns:
        Dictionary of growth coefficients for the species
    """
    coeffs = {}
    with sqlite3.connect('fvspy.db') as conn:
        # Get small tree coefficients
        query = "SELECT * FROM small_tree_coefficients WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=(species_code,))
        if df.empty:
            raise ValueError(f"No small tree coefficients found for species {species_code}")
        small_tree = df.iloc[0]
        coeffs.update({
            'SmallTreeGrowth_c1': small_tree['b0'],
            'SmallTreeGrowth_c2': small_tree['b1'],
            'SmallTreeGrowth_c3': small_tree['b2'],
            'SmallTreeGrowth_c4': small_tree['b3'],
            'SmallTreeGrowth_c5': small_tree['b4']
        })
        
        # Get height-diameter coefficients
        query = "SELECT * FROM height_diameter_coefficients WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=(species_code,))
        if df.empty:
            raise ValueError(f"No height-diameter coefficients found for species {species_code}")
        hd = df.iloc[0]
        coeffs.update({
            'CurtisArney_b0': hd['CurtisArney_b0'],
            'CurtisArney_b1': hd['CurtisArney_b1'],
            'CurtisArney_b2': hd['CurtisArney_b2']
        })
        
        # Get large tree coefficients
        query = "SELECT * FROM large_tree_coefficients WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=(species_code,))
        if df.empty:
            raise ValueError(f"No large tree coefficients found for species {species_code}")
        large_tree = df.iloc[0]
        coeffs.update({
            'LargeTreeGrowth_b1': large_tree['b0'],
            'LargeTreeGrowth_b2': large_tree['b1'],
            'LargeTreeGrowth_b3': large_tree['b2'],
            'LargeTreeGrowth_b4': large_tree['b3'],
            'LargeTreeGrowth_b5': large_tree['b4'],
            'LargeTreeGrowth_b6': large_tree['b5'],
            'LargeTreeGrowth_b7': 0.0000001,  # Additional coefficients not in database
            'LargeTreeGrowth_b8': 0.0000001,
            'LargeTreeGrowth_b9': 0.0000001,
            'LargeTreeGrowth_b10': 0.0000001,
            'LargeTreeGrowth_b11': 0.0000001
        })
        
        # Add volume coefficients (placeholder values)
        coeffs.update({
            'Volume_b0': 0.002,
            'Volume_b1': 1.8,
            'Volume_b2': 1.1
        })
        
        # Add diameter limits
        coeffs.update({
            'Lower_Diameter_Limit': 12,
            'Upper_Diameter_Limit': 24
        })
        
        return coeffs

def estimate_age_from_height_diameter(species_code: str, height: float, dbh: float) -> int:
    """Estimate tree age based on height-diameter relationship.
    
    Uses Curtis-Arney or Wykoff equations from growth_models to estimate age
    based on the relationship between actual and predicted height.
    
    Args:
        species_code: The species code
        height: Tree height in feet
        dbh: Tree diameter at breast height in inches
        
    Returns:
        Estimated age in years
    """
    try:
        coeffs = load_growth_coefficients(species_code)
        
        # Get predicted height using Curtis-Arney equation
        predicted_height = growth_models.curtis_arney_height(dbh, species_code)
        
        # Calculate relative development (actual/predicted height)
        height_ratio = height / predicted_height if predicted_height > 0 else 1.0
        
        # Base age estimate on size and relative development
        if dbh < 3.0:
            # For small trees, use small tree height growth equation
            # Solve for age that gives observed height
            si = coeffs.get('SmallTreeGrowth_si', 80)  # Default SI if not available
            c1 = coeffs['SmallTreeGrowth_c1']
            c2 = coeffs['SmallTreeGrowth_c2']
            c3 = coeffs['SmallTreeGrowth_c3']
            c4 = coeffs['SmallTreeGrowth_c4']
            c5 = coeffs['SmallTreeGrowth_c5']
            
            # Start with rough estimate
            est_age = max(5, int(height))
            
            # Refine estimate using small tree height growth equation
            for _ in range(5):  # Few iterations to converge
                pred_ht = growth_models.calculate_small_tree_height_growth(
                    si, est_age, c1, c2, c3, c4, c5, height)
                if abs(pred_ht - height) < 0.1:
                    break
                est_age = int(est_age * (height / pred_ht))
            
            return max(5, est_age)
        else:
            # For larger trees, use diameter-based estimate adjusted by height ratio
            base_age = dbh * 2.5  # Rough estimate: 2.5 years per inch of diameter
            estimated_age = int(base_age * height_ratio)
            return max(5, estimated_age)
            
    except (ValueError, KeyError):
        # Fallback to simple DBH-based estimate if coefficients not found
        return max(5, int(dbh * 2.5))

def initialize_from_fia(db_path: str, stand_cn: str):
    """Initialize a stand from FIA database.
    
    Args:
        db_path: Path to the FIA database file
        stand_cn: The stand control number to initialize from
        
    Returns:
        A list of tree objects representing the stand
    """
    # Map FIA species codes to FVS species codes
    species_map = {
        131: "LP"  # Loblolly Pine
    }
    
    with FIADatabase(db_path) as db:
        # Get stand information including site characteristics
        stand_info = db.get_plot_info(stand_cn)
        if not stand_info:
            raise ValueError(f"Stand {stand_cn} not found in database")
            
        # Get trees for the stand
        trees_df = db.get_plot_trees(stand_cn)
        if trees_df.empty:
            raise ValueError(f"No trees found for stand {stand_cn}")
        
        # Calculate stand-level metrics
        total_ba = sum((np.pi * (trees_df['DIAMETER']/2)**2) * trees_df['TREE_COUNT'] / 144)
        max_height = trees_df['HEIGHT'].max()
        
        # Convert crown class codes to relative SDI contribution
        crown_class_sdi = {
            0: 0.5,  # Unknown
            1: 1.0,  # Open grown
            2: 1.0,  # Dominant
            3: 0.8,  # Co-dominant
            4: 0.6,  # Intermediate
            5: 0.4   # Overtopped
        }
        
        # Calculate initial CCF for the stand
        initial_ccf = calculate_ccf(trees_df)
        
        # Convert trees to objects with calculated variables
        stand = []
        for _, tree_data in trees_df.iterrows():
            # Convert FIA species code to FVS species code
            species_code = species_map.get(int(tree_data['SPECIES']))
            if species_code is None:
                print(f"Warning: No species mapping found for FIA code {tree_data['SPECIES']}")
                continue
            
            # Get species coefficients for growth calculations
            try:
                species_coeffs = load_growth_coefficients(species_code)
            except ValueError:
                print(f"Warning: No growth coefficients found for species {species_code}")
                continue
            
            # Estimate age using height-diameter relationship
            estimated_age = estimate_age_from_height_diameter(
                species_code,
                tree_data['HEIGHT'],
                tree_data['DIAMETER']
            )
            
            # Calculate relative SDI based on crown class
            crown_class = int(tree_data['CROWN_CLASS']) if pd.notnull(tree_data['CROWN_CLASS']) else 0
            rel_sdi = crown_class_sdi.get(crown_class, 0.5)
            
            # Calculate crown ratio using Weibull model
            acr = crown_ratio.calculate_acr(rel_sdi, species_code)
            if acr is not None:
                # Get crown parameters for the species
                with sqlite3.connect('fvspy.db') as conn:
                    query = "SELECT * FROM crown_ratio_coefficients WHERE species_code = ?"
                    df = pd.read_sql_query(query, conn, params=(species_code,))
                    if not df.empty:
                        coeffs = df.iloc[0]
                        a, b, c = crown_ratio.calculate_weibull_parameters(
                            acr, 
                            coeffs['a'],
                            coeffs['b0'],
                            coeffs['b1'],
                            coeffs['c']
                        )
                        scale = crown_ratio.calculate_scale(initial_ccf)
                        # Use tree's relative position in diameter distribution for x
                        x = len(trees_df[trees_df['DIAMETER'] <= tree_data['DIAMETER']]) / len(trees_df)
                        calculated_cr = crown_ratio.calculate_crown_ratio_weibull(x, a, b, c, scale)
                    else:
                        calculated_cr = 0.4  # Default if no coefficients found
            else:
                calculated_cr = 0.4  # Default if ACR calculation fails
            
            # Use measured crown ratio if available, otherwise use calculated
            crown_ratio_value = (tree_data['CROWN_RATIO'] / 100 
                               if pd.notnull(tree_data['CROWN_RATIO']) 
                               else calculated_cr)
            
            # Initialize basic tree attributes
            tree_dict = {
                'species': species_code,
                'dbh': tree_data['DIAMETER'],
                'height': tree_data['HEIGHT'],
                'crown_ratio': crown_ratio_value,
                'trees_per_acre': tree_data['TREE_COUNT'],
                'age': estimated_age,
                
                # Site characteristics from stand info
                'si': stand_info.get('SITE_INDEX', 80),
                'Slope': stand_info.get('SLOPE', 0.1),
                'Aspect': stand_info.get('ASPECT', 0),
                'Fortype': stand_info.get('FOREST_TYPE', 0.5),
                
                # Stand-level metrics
                'BA': total_ba,
                'PBAL': sum((np.pi * (trees_df[trees_df['DIAMETER'] > tree_data['DIAMETER']]['DIAMETER']/2)**2) * 
                           trees_df[trees_df['DIAMETER'] > tree_data['DIAMETER']]['TREE_COUNT'] / 144),
                
                # Competition metrics based on crown class and position
                'RELSDI': rel_sdi,
                'CCF': initial_ccf,
                'PCCF': calculate_pccf(trees_df, tree_data),
                
                # Additional calculated metrics
                'RELHT': tree_data['HEIGHT'] / max_height if max_height > 0 else 1.0,
                'Ecounit': 0.2,  # Could be derived from location if needed
                'Plant': 0.1     # Could be derived from forest type if needed
            }
            
            # Add growth-specific variables
            tree_dict = initialize_tree_growth_variables(tree_dict, species_coeffs)
            
            tree = type('obj', (object,), tree_dict)
            stand.append(tree)
            
        return stand

def calculate_ccf(trees_df):
    """Calculate Crown Competition Factor for the stand.
    
    CCF is calculated using the crown ratio module's functions to determine
    crown width and competition. The calculation follows Dixon's (1985) methodology
    using Weibull-based crown model.
    
    Args:
        trees_df: DataFrame containing tree data
        
    Returns:
        CCF value for the stand (percentage)
    """
    # Standard acre in square feet
    ACRE_SQFT = 43560
    
    # Calculate stand-level metrics needed for crown ratio estimation
    total_ba = sum((np.pi * (trees_df['DIAMETER']/2)**2) * trees_df['TREE_COUNT'] / 144)
    max_sdi = 400  # Default maximum SDI, should be species-specific
    current_sdi = total_ba * (trees_df['DIAMETER'].mean() / 10) ** 1.605
    relsdi = (current_sdi / max_sdi) * 10  # Convert to scale expected by calculate_acr
    
    total_crown_area = 0
    n_trees = len(trees_df)
    
    # Calculate crown area for each tree
    for i, tree in trees_df.iterrows():
        # Use measured crown ratio if available
        if pd.notnull(tree['CROWN_RATIO']):
            cr = tree['CROWN_RATIO'] / 100
        else:
            # Calculate crown ratio using Weibull model
            # 1. Get average crown ratio for the species
            acr = crown_ratio.calculate_acr(relsdi, tree['SPECIES'])
            if acr is None:
                cr = 0.4  # Default if calculation fails
            else:
                try:
                    # 2. Get crown parameters for the species
                    with sqlite3.connect('fvspy.db') as conn:
                        query = "SELECT * FROM crown_ratio_coefficients WHERE species_code = ?"
                        df = pd.read_sql_query(query, conn, params=(tree['SPECIES'],))
                        if not df.empty:
                            coeffs = df.iloc[0]
                            # 3. Calculate Weibull parameters
                            a, b, c = crown_ratio.calculate_weibull_parameters(
                                acr, 
                                coeffs['a'],
                                coeffs['b0'],
                                coeffs['b1'],
                                coeffs['c']
                            )
                            # 4. Calculate tree's position in diameter distribution
                            x = len(trees_df[trees_df['DIAMETER'] <= tree['DIAMETER']]) / n_trees
                            # 5. Use initial scale of 1.0 (will be adjusted in subsequent iterations)
                            cr = crown_ratio.calculate_crown_ratio_weibull(x, a, b, c, 1.0)
                        else:
                            cr = 0.4  # Default if no coefficients found
                except (sqlite3.Error, KeyError):
                    cr = 0.4  # Default if database access fails
        
        # Calculate crown area based on crown ratio and tree size
        # Using a simplified crown width model: crown width = k * DBH * sqrt(crown_ratio)
        # where k is a species-specific constant (typically around 1.0)
        k = 1.0  # Could be made species-specific
        crown_width = k * tree['DIAMETER'] * np.sqrt(cr)
        crown_area = np.pi * (crown_width/2)**2
        total_crown_area += crown_area * tree['TREE_COUNT']
    
    # Calculate initial CCF
    initial_ccf = (total_crown_area / ACRE_SQFT) * 100
    
    # Iterate to adjust crown ratios based on competition
    # This could be done in a loop to converge on final CCF
    scale = crown_ratio.calculate_scale(initial_ccf)
    
    # For now, we'll just do one adjustment
    total_crown_area = 0
    for i, tree in trees_df.iterrows():
        if pd.notnull(tree['CROWN_RATIO']):
            cr = tree['CROWN_RATIO'] / 100
        else:
            cr = cr * scale  # Adjust crown ratio by scale factor
        
        crown_width = k * tree['DIAMETER'] * np.sqrt(cr)
        crown_area = np.pi * (crown_width/2)**2
        total_crown_area += crown_area * tree['TREE_COUNT']
    
    # Calculate final CCF
    final_ccf = (total_crown_area / ACRE_SQFT) * 100
    
    return min(final_ccf, 200)  # Cap at 200% to account for crown overlap

def calculate_pccf(trees_df, tree_data):
    """Calculate Point Crown Competition Factor for a specific tree.
    
    Args:
        trees_df: DataFrame containing tree data
        tree_data: Series containing data for the target tree
        
    Returns:
        PCCF value for the tree
    """
    # Calculate competition from larger and similar sized trees
    larger_trees = trees_df[trees_df['DIAMETER'] >= tree_data['DIAMETER']]
    if larger_trees.empty:
        return 0
    
    # Use crown class to weight the competition
    crown_weights = {
        1: 1.2,  # Open grown trees contribute more
        2: 1.0,  # Dominant trees normal contribution
        3: 0.8,  # Co-dominant trees less
        4: 0.6,  # Intermediate trees much less
        5: 0.4   # Overtopped trees minimal contribution
    }
    
    pccf = 0
    for _, comp_tree in larger_trees.iterrows():
        crown_class = int(comp_tree['CROWN_CLASS']) if pd.notnull(comp_tree['CROWN_CLASS']) else 3
        weight = crown_weights.get(crown_class, 0.8)
        distance_factor = 1.0  # Could be adjusted based on spatial data if available
        pccf += weight * distance_factor * comp_tree['TREE_COUNT']
    
    return min(pccf, 100)  # Cap at 100%

def load_crown_coefficients(species_code: str) -> dict:
    """Load crown width coefficients for a species from fvspy.db.
    
    Args:
        species_code: The species code to look up
        
    Returns:
        Dictionary of crown coefficients for the species
    """
    with sqlite3.connect('fvspy.db') as conn:
        query = "SELECT * FROM species_scaling_factors WHERE species_code = ?"
        df = pd.read_sql_query(query, conn, params=(species_code,))
        if df.empty:
            raise ValueError(f"No crown coefficients found for species {species_code}")
        return df.iloc[0].to_dict()

def calculate_crown_width(dbh: float, height: float, crown_ratio: float, species_code: str) -> float:
    """Calculate maximum crown width for a tree.
    
    Args:
        dbh: Tree diameter at breast height (inches)
        height: Tree height (feet)
        crown_ratio: Crown ratio (proportion)
        species_code: Species code for crown equations
        
    Returns:
        Crown width in feet
    """
    try:
        coeffs = load_crown_coefficients(species_code)
        
        # Calculate crown width using species-specific equation
        # Crown width = a + b * DBH + c * Height + d * Crown Ratio
        crown_width = (coeffs['crown_width_a'] + 
                      coeffs['crown_width_b'] * dbh + 
                      coeffs['crown_width_c'] * height + 
                      coeffs['crown_width_d'] * crown_ratio)
        
        # Ensure reasonable bounds
        return max(min(crown_width, height), dbh/2)
    except (ValueError, KeyError):
        # Fallback to a simple DBH-based estimate if coefficients not found
        return dbh * 0.75  # Simple approximation: crown width is about 75% of DBH

def calculate_crown_area(crown_width: float) -> float:
    """Calculate crown area assuming circular projection.
    
    Args:
        crown_width: Crown width in feet
        
    Returns:
        Crown area in square feet
    """
    return np.pi * (crown_width/2)**2

def initialize_tree_growth_variables(tree_dict, species_coeffs):
    """Initialize growth-related variables for a tree.
    
    Args:
        tree_dict: Dictionary of tree attributes
        species_coeffs: Species coefficients from growth_models
        
    Returns:
        Updated tree_dict with growth variables
    """
    dbh = tree_dict['dbh']
    
    # Initialize bark ratio
    bark_ratio = growth_models.calculate_inside_bark_dbh_ratio(dbh, tree_dict['species'])
    tree_dict['dbh_ib'] = dbh * bark_ratio
    
    # Initialize growth weights for blending if in transition zone
    if 1.0 <= dbh <= 3.0:
        tree_dict['growth_weight'] = growth_models.calculate_growth_weight(dbh, 1.0, 3.0)
    else:
        tree_dict['growth_weight'] = 1.0 if dbh > 3.0 else 0.0
    
    # Initialize diameter growth bounds
    tree_dict['lower_diameter_limit'] = species_coeffs.get('Lower_Diameter_Limit', 998)
    tree_dict['upper_diameter_limit'] = species_coeffs.get('Upper_Diameter_Limit', 999)
    
    return tree_dict

def initialize_stand(input_data, trees_per_acre=None, species_mix=None, initial_dbh_distribution=None):
    """Initializes a stand of trees.

    Args:
        input_data: Either a path to a CSV file, a dictionary containing stand initialization parameters,
                   or a tuple of (db_path, plot_id) for FIA database initialization.
        trees_per_acre: Initial number of trees per acre (used if initializing from conditions).
        species_mix: A dictionary specifying the proportion of each species (used if initializing from conditions).
        initial_dbh_distribution: A function that generates initial DBH values. For realistic distributions,
                                use get_empirical_dbh_distribution(species_code).

    Example:
        # Initialize from empirical distributions
        species_mix = {"FR1": 0.6, "JU1": 0.4}
        dbh_distributions = {
            species: get_empirical_dbh_distribution(species)
            for species in species_mix
        }
        stand = initialize_stand(
            {"use_empirical": True},
            trees_per_acre=1000,
            species_mix=species_mix,
            initial_dbh_distribution=dbh_distributions
        )

    Returns:
        A list of tree objects representing the stand.
    """
    if isinstance(input_data, tuple) and len(input_data) == 2:  # Initialize from FIA database
        db_path, plot_id = input_data
        return initialize_from_fia(db_path, plot_id)
    elif isinstance(input_data, (str, Path)):  # Initialize from CSV
        stand_df = pd.read_csv(input_data)
        stand = stand_df.to_dict(orient="records")
        for tree_data in stand:
            tree = type('obj', (object,), tree_data)
            stand[stand.index(tree_data)] = tree
        return stand
    elif isinstance(input_data, dict):  # Initialize from conditions
        if not all([trees_per_acre, species_mix, initial_dbh_distribution]):
            raise ValueError("Must provide trees_per_acre, species_mix, and initial_dbh_distribution when initializing from conditions.")

        stand = []
        for species, proportion in species_mix.items():
            num_trees = int(trees_per_acre * proportion)
            # Handle both single distribution function and species-specific distributions
            dbh_dist = initial_dbh_distribution.get(species, initial_dbh_distribution) if isinstance(initial_dbh_distribution, dict) else initial_dbh_distribution
            for _ in range(num_trees):
                dbh = dbh_dist()
                stand.append(type('obj', (object,), {
                    "species": species, 
                    "dbh": dbh, 
                    "height": None, 
                    "age": 0, 
                    "trees_per_acre": 1, 
                    "si": 80, 
                    "RELSDI": 0.5, 
                    "CCF": 100, 
                    "PCCF": 100, 
                    "PBAL": 100, 
                    "Slope": 0.1, 
                    "Aspect": 0, 
                    "Fortype": 0.5, 
                    "Ecounit": 0.2, 
                    "Plant": 0.1
                }))
        return stand
    else:
        raise TypeError("input_data must be a path, dictionary, or (db_path, plot_id) tuple.")

def get_empirical_dbh_distribution(species_code, db_path="data/test_coastal_loblolly.db"):
    """Create a DBH distribution function based on empirical data.
    
    Args:
        species_code: The species code to get distribution for
        db_path: Path to the database containing tree data
        
    Returns:
        A function that generates DBH values following the empirical distribution
    """
    with sqlite3.connect(db_path) as conn:
        # Get DBH values for the species from the database
        query = """
            SELECT DIAMETER 
            FROM trees 
            WHERE SPECIES = ? 
            AND DIAMETER IS NOT NULL
        """
        df = pd.read_sql_query(query, conn, params=(species_code,))
        
        if df.empty:
            raise ValueError(f"No DBH data found for species {species_code}")
            
        dbh_values = df['DIAMETER'].values
        
        # Create a kernel density estimate for smooth sampling
        from scipy import stats
        kde = stats.gaussian_kde(dbh_values)
        
        # Return a function that samples from this distribution
        def sample_dbh():
            while True:
                # Sample until we get a positive DBH value
                dbh = kde.resample(1)[0][0]
                if dbh > 0:
                    return dbh
        
        return sample_dbh

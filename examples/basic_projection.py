import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple
from fvs_core.initialize_stand import initialize_from_fia
from fvs_core.grow_stand import grow_stand
from fvs_core.stand_metrics import calculate_stand_metrics
from fvs_core.visualize_stand_growth import (
    visualize_stand_growth,
    visualize_dbh_distribution,
    visualize_height_distribution,
    visualize_tree_attributes,
    visualize_species_composition,
    create_stand_summary
)
import os

def load_coefficients(db_path: Union[str, Path]) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Loads growth and crown coefficients from the database.
    
    Args:
        db_path: Path to the SQLite database containing coefficients
        
    Returns:
        Tuple of (growth_coefficients, crown_coefficients)
    """
    with sqlite3.connect(db_path) as conn:
        # Load growth coefficients
        growth_coeff_query = """
        SELECT s.species_code,
               stc.b0 as small_tree_b0, stc.b1 as small_tree_b1,
               ltc.b0 as CurtisArney_b0, ltc.b1 as CurtisArney_b1, ltc.b2 as CurtisArney_b2
        FROM species s
        LEFT JOIN small_tree_coefficients stc ON s.species_code = stc.species_code
        LEFT JOIN large_tree_coefficients ltc ON s.species_code = ltc.species_code
        """
        growth_df = pd.read_sql_query(growth_coeff_query, conn)
        
        # Load crown coefficients
        crown_coeff_query = """
        SELECT s.species_code,
               sp.si_min, sp.si_max, sp.Dbw,
               sp.Bark_b0, sp.Bark_b1
        FROM species s
        LEFT JOIN species_parameters sp ON s.species_code = sp.species_code
        """
        crown_df = pd.read_sql_query(crown_coeff_query, conn)
    
    # Convert to dictionaries
    growth_coeffs = {}
    for _, row in growth_df.iterrows():
        growth_coeffs[row['species_code']] = {
            'small_tree': {
                'b0': row['small_tree_b0'],
                'b1': row['small_tree_b1']
            },
            'large_tree': {
                'b0': row['CurtisArney_b0'],
                'b1': row['CurtisArney_b1'],
                'b2': row['CurtisArney_b2']
            }
        }
    
    crown_coeffs = {}
    for _, row in crown_df.iterrows():
        crown_coeffs[row['species_code']] = {
            'si_min': row['si_min'],
            'si_max': row['si_max'],
            'dbw': row['Dbw'],
            'bark': {
                'b0': row['Bark_b0'],
                'b1': row['Bark_b1']
            }
        }
    
    return growth_coeffs, crown_coeffs

def generate_stand_history(stand_db_path, coeff_db_path, stand_cn, projection_period, output_dir):
    """Generate stand history for a given stand.
    
    Args:
        stand_db_path: Path to the database containing stand data
        coeff_db_path: Path to the database containing coefficients
        stand_cn: Stand control number to project
        projection_period: Number of years to project
        output_dir: Directory to save outputs
        
    Returns:
        DataFrame containing stand history
    """
    # Species code mapping
    species_mapping = {
        '131': 'LP'  # Loblolly Pine
    }
    
    # Connect to databases
    with sqlite3.connect(stand_db_path) as stand_conn, sqlite3.connect(coeff_db_path) as coeff_conn:
        # Get trees for the stand
        query = "SELECT * FROM trees WHERE STAND_CN = ?"
        trees_df = pd.read_sql_query(query, stand_conn, params=(stand_cn,))
        
        # Get species data
        species_data = {}
        crown_data = {}
        
        # Get unique species in the stand
        unique_species = trees_df['SPECIES'].unique()
        
        for species_code in unique_species:
            # Map the species code to FVS code
            fvs_code = species_mapping.get(str(species_code))
            if not fvs_code:
                print(f"Warning: No species mapping found for code {species_code}")
                continue
                
            # Get small tree coefficients
            query = """
                SELECT * FROM small_tree_coefficients 
                WHERE species_code = ?
            """
            small_tree_df = pd.read_sql_query(query, coeff_conn, params=(fvs_code,))
            if small_tree_df.empty:
                print(f"Warning: No small tree coefficients found for {fvs_code}")
                continue
            small_tree_coeffs = small_tree_df.iloc[0]
            
            # Get large tree coefficients
            query = """
                SELECT * FROM large_tree_coefficients 
                WHERE species_code = ?
            """
            large_tree_df = pd.read_sql_query(query, coeff_conn, params=(fvs_code,))
            if large_tree_df.empty:
                print(f"Warning: No large tree coefficients found for {fvs_code}")
                continue
            large_tree_coeffs = large_tree_df.iloc[0]
            
            # Get height-diameter coefficients
            query = """
                SELECT * FROM height_diameter_coefficients 
                WHERE species_code = ?
            """
            hd_df = pd.read_sql_query(query, coeff_conn, params=(fvs_code,))
            if hd_df.empty:
                print(f"Warning: No height-diameter coefficients found for {fvs_code}")
                continue
            hd_coeffs = hd_df.iloc[0]
            
            # Get species parameters
            query = """
                SELECT * FROM species_parameters 
                WHERE species_code = ?
            """
            params_df = pd.read_sql_query(query, coeff_conn, params=(fvs_code,))
            if params_df.empty:
                print(f"Warning: No species parameters found for {fvs_code}")
                continue
            params_coeffs = params_df.iloc[0]
            
            # Get crown ratio coefficients
            query = """
                SELECT * FROM crown_ratio_coefficients 
                WHERE species_code = ?
            """
            crown_df = pd.read_sql_query(query, coeff_conn, params=(fvs_code,))
            if crown_df.empty:
                print(f"Warning: No crown ratio coefficients found for {fvs_code}")
                continue
            crown_coeffs = crown_df.iloc[0]
            
            # Add species data
            species_data[fvs_code] = {
                # Small tree height growth coefficients
                "SmallTreeGrowth_c1": small_tree_coeffs['b0'],
                "SmallTreeGrowth_c2": small_tree_coeffs['b1'],
                "SmallTreeGrowth_c3": small_tree_coeffs['b2'],
                "SmallTreeGrowth_c4": small_tree_coeffs['b3'],
                "SmallTreeGrowth_c5": small_tree_coeffs['b4'],
                # Height-diameter coefficients
                "CurtisArney_b0": hd_coeffs['CurtisArney_b0'],
                "CurtisArney_b1": hd_coeffs['CurtisArney_b1'],
                "CurtisArney_b2": hd_coeffs['CurtisArney_b2'],
                # Bark coefficients
                "Bark_b0": params_coeffs['Bark_b0'],
                "Bark_b1": params_coeffs['Bark_b1'],
                # Volume coefficients (placeholder values)
                "Volume_b0": 0.002,
                "Volume_b1": 1.8,
                "Volume_b2": 1.1,
                # Diameter growth coefficients from large tree model
                "b1": large_tree_coeffs['b0'],
                "b2": large_tree_coeffs['b1'],
                "b3": large_tree_coeffs['b2'],
                "b4": large_tree_coeffs['b3'],
                "b5": large_tree_coeffs['b4'],
                "b6": large_tree_coeffs['b5'],
                "b7": 0.0000001,  # Additional coefficients not in database
                "b8": 0.0000001,
                "b9": 0.0000001,
                "b10": 0.0000001,
                "b11": 0.0000001,
                # Diameter limits from species parameters
                "Lower_Diameter_Limit": params_coeffs['dbh_min'],
                "Upper_Diameter_Limit": params_coeffs['dbh_max']
            }
            
            # Add crown data from crown ratio coefficients
            crown_data[fvs_code] = {
                "a": crown_coeffs['a'] / 100.0,  # Convert to proportion
                "b0": crown_coeffs['b0'],
                "b1": crown_coeffs['b1'],
                "c": max(2.0, crown_coeffs['c'])  # Ensure c > 2.0
            }
        
        # Convert trees to objects
        stand = []
        for _, tree_data in trees_df.iterrows():
            species_code = str(tree_data['SPECIES'])
            fvs_code = species_mapping.get(species_code)
            if not fvs_code or fvs_code not in species_data:
                continue
                
            tree = type('obj', (object,), {
                "species": fvs_code,  # Use mapped species code
                "dbh": tree_data['DIAMETER'],
                "height": tree_data['HEIGHT'],
                "age": 20,  # Default age since it's not in the database
                "si": 80,  # Default site index (lowercase for consistency)
                "trees_per_acre": tree_data['TREE_COUNT'],
                "relsdi": 0.5,  # Default relative SDI (lowercase for consistency)
                "ccf": 100,  # Default crown competition factor (lowercase for consistency)
                "pccf": 50,  # Default point crown competition factor (lowercase for consistency)
                "ba": 120,  # Default basal area (lowercase for consistency)
                "pbal": 80,  # Default point basal area in larger trees (lowercase for consistency)
                "relht": 0.6,  # Default relative height (lowercase for consistency)
                "slope": 0.1,  # Default slope (lowercase for consistency)
                "aspect": 0,  # Default aspect (lowercase for consistency)
                "fortype": 0.5,  # Default forest type (lowercase for consistency)
                "ecounit": 0.2,  # Default ecological unit (lowercase for consistency)
                "plant": 0.1,  # Default plant status (lowercase for consistency)
                "crown_ratio": tree_data.get('CROWN_RATIO', 0.6)  # Use crown ratio from data or default
            })
            stand.append(tree)
        
        # Project the stand
        stand_history = []
        for year in range(0, projection_period + 1, 5):
            # Calculate stand metrics
            metrics = calculate_stand_metrics(stand)
            metrics['year'] = year
            stand_history.append(metrics)
            
            # Grow the stand for 5 years
            if year < projection_period:
                grow_stand(stand, 5, species_data, crown_data)  # Added projection period argument
        
        # Convert to DataFrame
        stand_history = pd.DataFrame(stand_history)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save results
        stand_history.to_csv(os.path.join(output_dir, f'stand_history_{stand_cn}.csv'), index=False)
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        visualize_stand_growth(stand_history, output_dir, stand_cn)
        
        return stand_history

if __name__ == "__main__":
    # Example usage
    stand_db_path = "data/test_coastal_loblolly.db"
    coeff_db_path = "data/fvspy.db"  # Updated path
    stand_cn = "635664613126144"  # Example stand control number
    projection_period = 50
    output_dir = "outputs"
    
    print(f"\nStarting stand projection with:")
    print(f"Stand DB: {stand_db_path}")
    print(f"Coefficient DB: {coeff_db_path}")
    print(f"Stand CN: {stand_cn}")
    print(f"Projection period: {projection_period} years")
    
    # Generate stand history
    try:
        stand_history = generate_stand_history(stand_db_path, coeff_db_path, stand_cn, projection_period, output_dir)
        
        # Save results if available
        if isinstance(stand_history, pd.DataFrame) and not stand_history.empty:
            stand_history.to_csv(os.path.join(output_dir, f'stand_history_{stand_cn}.csv'), index=False)
            print(f"\nResults saved to {output_dir}")
        else:
            print("\nNo stand history was generated.")
    except Exception as e:
        print(f"\nError during projection: {str(e)}")
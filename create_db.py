"""Script to create and populate the FVS database."""

import pandas as pd
from fvs_core.db_utils import FVSDatabase

def create_and_populate_db():
    """Create and populate the FVS database."""
    # Create database with schema
    with FVSDatabase('fvspy.db') as db:
        print("Creating database schema...")
        db.create_database('data/create_tables_v2.sql')
        
        # Load data from CSV files into tables
        print("\nLoading data into tables...")
        
        # Load species data
        species_df = pd.read_csv('data/species_data.csv')
        species_df[['species_code', 'FIA_code']].to_sql('species', db._conn, if_exists='append', index=False)
        print("✓ Loaded species data")
        
        # Load ecological units (from base_ecounit_codes.csv)
        eco_df = pd.read_csv('data/base_ecounit_codes.csv')
        eco_df[['fvs_ecounit', 'fvspy_ecounit']].to_sql('ecological_units', db._conn, if_exists='append', index=False)
        print("✓ Loaded ecological units")
        
        # Load ecological coefficients
        eco_coef_df = pd.read_csv('data/ecounit_codes.csv')
        # Fill NaN values with 0.0
        eco_coef_df = eco_coef_df.fillna(0.0)
        eco_coef_df = eco_coef_df.rename(columns={
            'fvs_spcd': 'species_code',
            'ecounit_b0': 'ecounit_b0',
            'ecounit_b1': 'ecounit_b1',
            'ecounit_b2': 'ecounit_b2',
            'ecounit_b3': 'ecounit_b3',
            'ecounit_b4': 'ecounit_b4',
            'ecounit_b5': 'ecounit_b5',
            'ecounit_b6': 'ecounit_b6',
            'ecounit_b7': 'ecounit_b7',
            'ecounit_b8': 'ecounit_b8',
            'ecounit_b9': 'ecounit_b9',
            'ecounit_b10': 'ecounit_b10',
            'ecounit_b11': 'ecounit_b11'
        })
        eco_coef_df[['species_code', 'fvs_ecounit', 'ecounit_b0', 'ecounit_b1', 'ecounit_b2', 'ecounit_b3', 
                     'ecounit_b4', 'ecounit_b5', 'ecounit_b6', 'ecounit_b7', 'ecounit_b8', 'ecounit_b9', 
                     'ecounit_b10', 'ecounit_b11']].to_sql('ecological_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded ecological coefficients")
        
        # Load forest types (taking first occurrence of each forest type code)
        forest_df = pd.read_csv('data/forest_type_group_codes.csv')
        forest_df = forest_df.drop_duplicates(subset=['fvs_fortypcd'], keep='first')
        forest_df[['fvs_fortypcd', 'fvs_fortypcd_name', 'fia_fortypcd']].to_sql('forest_types', db._conn, if_exists='append', index=False)
        print("✓ Loaded forest types")
        
        # Load growth coefficients
        growth_df = pd.read_csv('data/ln_dds_species_growth_parameters.csv')
        growth_df = growth_df.fillna(0.0)  # Fill NaN values with 0.0
        
        # Create a new DataFrame with the required columns
        growth_coef_df = pd.DataFrame({
            'species_code': growth_df['species_code'],
            'CurtisArney_b0': 0.0,  # Default values since they're not in the CSV
            'CurtisArney_b1': 0.0,
            'CurtisArney_b2': 0.0,
            'Wykoff_b0': 0.0,
            'Wykoff_b1': 0.0,
            'small_tree_b0': 0.0,
            'small_tree_b1': 0.0,
            'small_tree_b2': 0.0,
            'small_tree_b3': 0.0,
            'small_tree_b4': 0.0,
            'ln_dds_b0': 0.0,  # We'll fill these from the CSV
            'ln_dds_b1': 0.0,
            'ln_dds_b2': growth_df['ln_dds_b2=8'],  # Note the different column name
            'ln_dds_b3': 0.0,
            'ln_dds_b4': 0.0,
            'ln_dds_b5': 0.0
        })
        
        growth_coef_df.to_sql('growth_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded growth coefficients")
        
        # Load crown ratio data
        crown_df = pd.read_csv('data/species_crown_ratio.csv')
        crown_df = crown_df.fillna(0.0)  # Fill NaN values with 0.0
        
        # Create a new DataFrame with the required columns
        scaling_factors_df = pd.DataFrame({
            'species_code': crown_df['species_code'],
            'si_min': 0.0,  # Default values since they're not in the CSV
            'si_max': 100.0,
            'Dbw': 0.0,
            'Bark_b0': crown_df['b0'],  # Map crown ratio coefficients to bark coefficients
            'Bark_b1': crown_df['b1']
        })
        
        scaling_factors_df.to_sql('species_scaling_factors', db._conn, if_exists='append', index=False)
        print("✓ Loaded crown ratio data")
        
        print("\nDatabase creation and population complete!")

if __name__ == '__main__':
    create_and_populate_db() 
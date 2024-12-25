"""Script to create and populate the FVS parameters database."""

import pandas as pd
from fvs_core.db_utils import FVSDatabase

def create_and_populate_db():
    """Create and populate the FVS parameters database."""
    # Create database with schema
    with FVSDatabase('fvspy.db') as db:
        print("Creating database schema...")
        db.create_database('create_tables_v2.sql')
        
        # Load data from CSV files into tables
        print("\nLoading data into tables...")
        
        # Load species data
        species_df = pd.read_csv('data/species_data.csv')
        species_df[['species_code', 'FIA_code']].to_sql('species', db._conn, if_exists='append', index=False)
        print("✓ Loaded species data")
        
        # Load height-diameter coefficients
        height_diam_cols = ['species_code', 'CurtisArney_b0', 'CurtisArney_b1', 'CurtisArney_b2', 'Wykoff_b0', 'Wykoff_b1']
        species_df[height_diam_cols].to_sql('height_diameter_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded height-diameter coefficients")
        
        # Load small tree coefficients
        small_tree_cols = ['species_code', 'small_tree_b0', 'small_tree_b1', 'small_tree_b2', 'small_tree_b3', 'small_tree_b4']
        small_tree_df = species_df[small_tree_cols].copy()
        small_tree_df.columns = ['species_code', 'b0', 'b1', 'b2', 'b3', 'b4']
        small_tree_df.to_sql('small_tree_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded small tree coefficients")
        
        # Load large tree coefficients
        large_tree_cols = ['species_code', 'ln_dds_b0', 'ln_dds_b1', 'ln_dds_b2', 'ln_dds_b3', 'ln_dds_b4', 'ln_dds_b5']
        large_tree_df = species_df[large_tree_cols].copy()
        large_tree_df.columns = ['species_code', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5']
        large_tree_df.to_sql('large_tree_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded large tree coefficients")
        
        # Load species parameters
        params_cols = ['species_code', 'si_min', 'si_max', 'Dbw', 'Bark_b0', 'Bark_b1']
        species_df[params_cols].to_sql('species_parameters', db._conn, if_exists='append', index=False)
        print("✓ Loaded species parameters")
        
        # Load ecological units (from base_ecounit_codes.csv)
        eco_df = pd.read_csv('data/base_ecounit_codes.csv')
        eco_df[['fvs_ecounit', 'fvspy_ecounit']].to_sql('ecological_units', db._conn, if_exists='append', index=False)
        print("✓ Loaded ecological units")
        
        # Load ecological coefficients and adjustments
        eco_coef_df = pd.read_csv('data/ecounit_codes.csv')
        eco_coef_df = eco_coef_df.fillna(0.0)  # Fill NaN values with 0.0
        eco_coef_df = eco_coef_df.rename(columns={'fvs_spcd': 'species_code'})
        
        # Base ecological coefficients
        eco_coeff_cols = ['fvs_ecounit'] + [f'ecounit_b{i}' for i in range(12)]
        eco_coeffs = eco_coef_df[eco_coeff_cols].copy()
        eco_coeffs.columns = ['fvs_ecounit'] + [f'base_b{i}' for i in range(12)]
        eco_coeffs = eco_coeffs.drop_duplicates(subset=['fvs_ecounit'])
        eco_coeffs.to_sql('ecological_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded ecological coefficients")
        
        # Species-specific ecological adjustments
        eco_adj_cols = ['species_code', 'fvs_ecounit'] + [f'ecounit_b{i}' for i in range(12)]
        eco_adj = eco_coef_df[eco_adj_cols].copy()
        eco_adj.columns = ['species_code', 'fvs_ecounit'] + [f'adjustment_b{i}' for i in range(12)]
        eco_adj.to_sql('ecological_species_adjustments', db._conn, if_exists='append', index=False)
        print("✓ Loaded ecological species adjustments")
        
        # Load forest types (taking first occurrence of each forest type code)
        forest_df = pd.read_csv('data/forest_type_group_codes.csv')
        forest_df = forest_df.drop_duplicates(subset=['fvs_fortypcd'], keep='first')
        forest_df[['fvs_fortypcd', 'fvs_fortypcd_name', 'fia_fortypcd']].to_sql('forest_types', db._conn, if_exists='append', index=False)
        print("✓ Loaded forest types")
        
        # Load forest type coefficients and adjustments
        growth_df = pd.read_csv('data/ln_dds_species_growth_parameters.csv')
        growth_df = growth_df.fillna(0.0)  # Fill NaN values with 0.0
        
        # Base forest type coefficients
        ft_base_cols = ['base_fortype', 'ftlohd', 'ftnohd', 'ftokpn', 'ftsfhp', 'ftuphd', 'ftupok', 'ftylpn']
        ft_base_df = growth_df[ft_base_cols].drop_duplicates(subset=['base_fortype'], keep='first')
        ft_base_df.columns = ['fvs_fortypcd', 'base_lohd', 'base_nohd', 'base_okpn', 'base_sfhp', 'base_uphd', 'base_upok', 'base_ylpn']
        ft_base_df.to_sql('forest_type_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded forest type coefficients")
        
        # Species-specific forest type adjustments
        ft_adj_cols = ['species_code', 'base_fortype', 'ftlohd', 'ftnohd', 'ftokpn', 'ftsfhp', 'ftuphd', 'ftupok', 'ftylpn']
        ft_adj_df = growth_df[ft_adj_cols].copy()
        ft_adj_df.columns = ['species_code', 'fvs_fortypcd', 'adjustment_lohd', 'adjustment_nohd', 'adjustment_okpn', 'adjustment_sfhp', 'adjustment_uphd', 'adjustment_upok', 'adjustment_ylpn']
        ft_adj_df.to_sql('forest_type_species_adjustments', db._conn, if_exists='append', index=False)
        print("✓ Loaded forest type species adjustments")
        
        # Load crown ratio coefficients
        crown_df = pd.read_csv('data/species_crown_ratio.csv')
        crown_df = crown_df.fillna(0.0)  # Fill NaN values with 0.0
        crown_df = crown_df.rename(columns={'acr_equation_number': 'acr_equation_type'})
        # Add missing columns with default values
        crown_df['d0'] = 0.0
        crown_df['d1'] = 0.0
        crown_df['d2'] = 0.0
        crown_df['sd'] = 0.0
        crown_df['Xmin'] = 0.0
        crown_df['Xmax'] = 100.0
        crown_df.to_sql('crown_ratio_coefficients', db._conn, if_exists='append', index=False)
        print("✓ Loaded crown ratio coefficients")
        
        print("\nDatabase creation and population complete!")

if __name__ == '__main__':
    create_and_populate_db() 
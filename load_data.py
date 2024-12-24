import pandas as pd
import sqlite3
from pathlib import Path

def create_tables(conn):
    """Create tables with proper constraints."""
    with open('create_tables_v2.sql', 'r') as f:
        conn.executescript(f.read())

def insert_dataframe(conn, table_name, df):
    """Insert DataFrame into table using INSERT OR REPLACE."""
    placeholders = ','.join(['?' for _ in df.columns])
    columns = ','.join(df.columns)
    query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
    conn.executemany(query, df.values.tolist())
    conn.commit()

def load_species_data(conn, df):
    """Load species data into the database."""
    # Basic species info
    species_data = df[['species_code', 'FIA_code']].copy()
    insert_dataframe(conn, 'species', species_data)
    
    # Growth coefficients
    growth_cols = [
        'species_code',
        'CurtisArney_b0', 'CurtisArney_b1', 'CurtisArney_b2',
        'Wykoff_b0', 'Wykoff_b1',
        'small_tree_b0', 'small_tree_b1', 'small_tree_b2', 'small_tree_b3', 'small_tree_b4',
        'ln_dds_b0', 'ln_dds_b1', 'ln_dds_b2', 'ln_dds_b3', 'ln_dds_b4', 'ln_dds_b5'
    ]
    growth_data = df[growth_cols].copy()
    insert_dataframe(conn, 'growth_coefficients', growth_data)
    
    # Scaling factors
    scaling_cols = ['species_code', 'si_min', 'si_max', 'Dbw', 'Bark_b0', 'Bark_b1']
    scaling_data = df[scaling_cols].copy()
    insert_dataframe(conn, 'species_scaling_factors', scaling_data)

def load_forest_types(conn, df):
    """Load forest type data into the database."""
    forest_types = df[['fvs_fortypcd', 'fvs_fortypcd_name', 'fia_fortypcd']].drop_duplicates()
    insert_dataframe(conn, 'forest_types', forest_types)

def load_ecological_units(conn, df):
    """Load ecological unit data into the database."""
    eco_units = df[['fvs_ecounit', 'fvspy_ecounit']].drop_duplicates()
    # Convert fvspy_ecounit to integer
    eco_units['fvspy_ecounit'] = eco_units['fvspy_ecounit'].astype(int)
    insert_dataframe(conn, 'ecological_units', eco_units)

def load_ecological_coefficients(conn, df, species_codes, eco_units):
    """Load ecological coefficients into the database."""
    # Rename fvs_spcd to species_code for consistency
    df = df.rename(columns={'fvs_spcd': 'species_code'})
    eco_cols = ['species_code', 'fvs_ecounit'] + [f'ecounit_b{i}' for i in range(12)]
    eco_data = df[eco_cols].copy()
    
    # Filter for valid species and ecological units
    eco_data = eco_data[
        eco_data['species_code'].isin(species_codes) &
        eco_data['fvs_ecounit'].isin(eco_units)
    ]
    
    # Fill any NULL values with 0.0
    eco_data = eco_data.fillna(0.0)
    insert_dataframe(conn, 'ecological_coefficients', eco_data)

def load_forest_type_coefficients(conn, df, species_codes, forest_types):
    """Load forest type coefficients into the database."""
    ft_cols = ['species_code', 'base_fortype', 'ftlohd', 'ftnohd', 'ftokpn', 'ftsfhp', 'ftuphd', 'ftupok', 'ftylpn']
    ft_data = df[ft_cols].copy()
    ft_data = ft_data.rename(columns={'base_fortype': 'fvs_fortypcd'})
    
    # Filter for valid species and forest types
    ft_data = ft_data[
        ft_data['species_code'].isin(species_codes) &
        ft_data['fvs_fortypcd'].isin(forest_types)
    ]
    
    # Fill any NULL values with 0.0
    ft_data = ft_data.fillna(0.0)
    insert_dataframe(conn, 'forest_type_coefficients', ft_data)

def main():
    # Connect to database with foreign key support
    conn = sqlite3.connect('fvspy.db')
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create tables with proper constraints
    create_tables(conn)
    
    try:
        # Load species data first (required by foreign keys)
        species_df = pd.read_csv('data/species_data.csv')
        load_species_data(conn, species_df)
        species_codes = species_df['species_code'].unique()
        
        # Load forest types (required by forest_type_coefficients)
        forest_types_df = pd.read_csv('data/forest_type_group_codes.csv')
        load_forest_types(conn, forest_types_df)
        forest_types = forest_types_df['fvs_fortypcd'].unique()
        
        # Load ecological units from base codes
        eco_units_df = pd.read_csv('data/base_ecounit_codes.csv')
        load_ecological_units(conn, eco_units_df)
        eco_units = eco_units_df['fvs_ecounit'].unique()
        
        # Load ecological coefficients from species data
        eco_coeffs_df = pd.read_csv('data/ecounit_codes.csv')
        load_ecological_coefficients(conn, eco_coeffs_df, species_codes, eco_units)
        
        # Load forest type coefficients from species growth parameters
        growth_params_df = pd.read_csv('data/ln_dds_species_growth_parameters.csv')
        load_forest_type_coefficients(conn, growth_params_df, species_codes, forest_types)
        
        conn.commit()
    except Exception as e:
        print(f"Error loading data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main() 
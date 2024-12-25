"""Script to create and populate the FVS parameters database."""

import os
import pandas as pd
import sqlite3
import ast

def create_and_populate_db():
    """Create and populate the FVS parameters database."""
    db_path = os.path.join('data', 'sqlite_databases', 'fvspy.db')
    sql_path = os.path.join('data', 'sqlite_databases', 'create_tables_v2.sql')
    csv_dir = os.path.join('data', 'fvs_sn_tables')
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    try:
        # Create tables
        print("Creating database schema...")
        with open(sql_path, 'r') as sql_file:
            conn.executescript(sql_file.read())
        
        # Load data from CSV files into tables
        print("\nLoading data into tables...")
        
        # Helper function to load CSV data
        def load_csv(filename, table_name, conn, columns=None, transform_func=None, **kwargs):
            print(f"Loading {filename}...")
            df = pd.read_csv(os.path.join(csv_dir, filename))
            df = df.fillna(0.0)  # Fill NaN values with 0.0
            if columns:
                df = df[columns]
            if transform_func:
                df = transform_func(df)
            df.to_sql(table_name, conn, if_exists='append', index=False, **kwargs)
            print(f"✓ Loaded {table_name}")
            return df
        
        # Extract unique species codes from site_index_range.csv
        species_df = pd.read_csv(os.path.join(csv_dir, 'site_index_range.csv'))
        species_df[['species_code']].to_sql('species', conn, if_exists='append', index=False)
        print("✓ Loaded species")
        
        # Load site index groups with mapped_species as string
        def transform_site_index_groups(df):
            df['mapped_species'] = df['mapped_species'].apply(lambda x: str(ast.literal_eval(x)))
            return df
        
        load_csv('site_index_groups.csv', 'site_index_groups', conn, transform_func=transform_site_index_groups)
        
        # Load site index ranges
        load_csv('site_index_range.csv', 'site_index_range', conn)
        
        # Load bark thickness data
        load_csv('bark_thickness.csv', 'bark_thickness', conn)
        
        # Load Wykoff functions
        load_csv('wykoff_functions.csv', 'wykoff_functions', conn)
        
        # Load Curtis-Arney functions
        load_csv('curtis_arney_functions.csv', 'curtis_arney_functions', conn)
        
        # Load large tree growth parameters
        load_csv('large_tree_growth_parameters.csv', 'large_tree_growth', conn)
        
        # Load small tree growth parameters
        load_csv('small_tree_growth_parameters.csv', 'small_tree_growth', conn)
        
        # Load forest type group codes
        load_csv('forest_type_group_codes.csv', 'forest_types', conn)
        
        # Load ecological unit codes
        load_csv('base_ecounit_codes.csv', 'ecological_units', conn)
        
        # Load ecological coefficients
        load_csv('ecounit_codes.csv', 'ecological_coefficients', conn)
        
        # Load species crown ratio data
        load_csv('species_crown_ratio_with_acr.csv', 'species_crown_ratio', conn)
        
        print("\nDatabase creation and population complete!")
        
        # Verify tables were created and populated
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nCreated tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cursor.fetchone()[0]
            print(f"- {table[0]}: {count} rows")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_and_populate_db() 
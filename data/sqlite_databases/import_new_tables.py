import sqlite3
import pandas as pd
import os

def import_tables():
    # Connect to the database
    db_path = 'data/sqlite_databases/fvspy.db'
    conn = sqlite3.connect(db_path)
    
    # Create tables using the SQL file
    with open('data/sqlite_databases/add_crown_width_tables.sql', 'r') as sql_file:
        sql_script = sql_file.read()
        conn.executescript(sql_script)
    
    # Import diameter bounding limits
    df_diameter = pd.read_csv('data/fvs_sn_tables/diameter_bounding_limits.csv')
    df_diameter.to_sql('diameter_bounding_limits', conn, if_exists='append', index=False)
    
    # Import planted coefficients
    df_planted = pd.read_csv('data/fvs_sn_tables/planted_coefficients.csv')
    df_planted.to_sql('planted_coefficients', conn, if_exists='append', index=False)
    
    # Import shade tolerance coefficients first (due to foreign key constraint)
    df_shade_coef = pd.read_csv('data/fvs_sn_tables/shade_tolerance_coefficients.csv')
    df_shade_coef.columns = [col.strip() for col in df_shade_coef.columns]  # Remove any whitespace
    df_shade_coef.to_sql('shade_tolerance_coefficients', conn, if_exists='append', index=False)
    
    # Import shade tolerance by species
    df_shade_species = pd.read_csv('data/fvs_sn_tables/shade_tolerance_by_species.csv')
    df_shade_species.columns = [col.strip() for col in df_shade_species.columns]  # Remove any whitespace
    df_shade_species['species_code'] = df_shade_species['species_code'].str.strip()
    df_shade_species['shade_tolerance'] = df_shade_species['shade_tolerance'].str.strip()
    df_shade_species.to_sql('shade_tolerance_by_species', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    print("Data import completed successfully!")

if __name__ == "__main__":
    import_tables() 
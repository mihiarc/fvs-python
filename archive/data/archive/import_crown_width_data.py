import sqlite3
import pandas as pd
import numpy as np
import os

# Database path
db_path = 'data/sqlite_databases/fvspy.db'

# CSV file paths
forest_grown_path = 'data/fvs_sn_tables/crown_width_forest_grown.csv'
open_grown_path = 'data/fvs_sn_tables/crown_width_open_grown.csv'

# First, execute the SQL schema
with open('data/sqlite_databases/add_crown_width_tables.sql', 'r') as f:
    sql_schema = f.read()

# Connect to database and create tables
conn = sqlite3.connect(db_path)
conn.executescript(sql_schema)

# Read and process forest grown data
forest_grown_df = pd.read_csv(forest_grown_path)
# Replace empty strings with NaN
forest_grown_df = forest_grown_df.replace('', np.nan)
forest_grown_df.to_sql('crown_width_forest_grown', conn, if_exists='append', index=False)

# Read and process open grown data
open_grown_df = pd.read_csv(open_grown_path)
# Replace empty strings with NaN
open_grown_df = open_grown_df.replace('', np.nan)
open_grown_df.to_sql('crown_width_open_grown', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("Crown width tables successfully created and populated.") 
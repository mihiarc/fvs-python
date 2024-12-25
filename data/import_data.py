import pandas as pd
import sqlite3
import os
import sys

def verify_database():
    """Verify that the database exists and has data."""
    db_path = 'fvspy.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found. Cannot proceed.", file=sys.stderr)
        sys.exit(1)
        
    if os.path.getsize(db_path) == 0:
        print(f"Error: Database {db_path} exists but is empty. Cannot proceed.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Database {db_path} exists and is populated.")

if __name__ == "__main__":
    verify_database() 
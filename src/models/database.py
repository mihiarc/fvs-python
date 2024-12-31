"""Database access for species configuration."""

import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

class DatabaseConnection:
    """Helper class for database operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / 'data' / 'sqlite_databases' / 'fvspy.db')
        self.db_path = db_path
    
    def __enter__(self):
        """Context manager entry."""
        self.conn = sqlite3.connect(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.conn:
            self.conn.close()
    
    def _fetch_coefficients(self, table: str, species_code: str) -> Dict[str, float]:
        """Helper method to fetch coefficients from a table.
        
        Args:
            table: Name of the table to query
            species_code: Species code to fetch data for
            
        Returns:
            Dictionary of coefficients, empty if no data found
            
        Raises:
            sqlite3.Error: If there's a database error
        """
        if table == "ecological_coefficients":
            # For ecological coefficients, use species_code directly as fvs_spcd
            df = pd.read_sql_query("""
                SELECT * FROM ecological_coefficients WHERE fvs_spcd = ?
            """, self.conn, params=(species_code,))
        else:
            # For other tables, use species_code directly
            df = pd.read_sql_query(f"""
                SELECT * FROM {table} WHERE species_code = ?
            """, self.conn, params=(species_code,))
        
        if df.empty:
            return {}
        
        return df.iloc[0].to_dict()
    
    def fetch_species_data(self, species_code: str) -> Dict[str, Any]:
        """Fetch all configuration data for a species.
        
        Args:
            species_code: Species code to fetch data for
            
        Returns:
            Dictionary containing all species configuration data
            
        Raises:
            ValueError: If species code not found in database or required data missing
        """
        with self.conn as conn:
            # Verify species exists
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM species WHERE species_code = ?", (species_code,))
            if not cursor.fetchone():
                raise ValueError(f"Species code {species_code} not found in database")
            
            # Get site index range and diameter breakpoint
            cursor.execute("""
                SELECT si_min, si_max, dbw 
                FROM site_index_range 
                WHERE species_code = ?
            """, (species_code,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"No site index range found for species {species_code}")
            si_min, si_max, dbw = result
            
            # Get diameter limits
            cursor.execute("""
                SELECT dbh_low, dbh_high
                FROM diameter_bounding_limits
                WHERE species_code = ?
            """, (species_code,))
            result = cursor.fetchone()
            if not result:
                dbh_low, dbh_high = 0.0, 100.0  # Default limits if not specified
            else:
                dbh_low, dbh_high = result
            
            # Get coefficients
            small_tree = self._fetch_coefficients("small_tree_growth", species_code)
            large_tree = self._fetch_coefficients("large_tree_growth", species_code)
            curtis_arney = self._fetch_coefficients("curtis_arney_functions", species_code)
            wykoff = self._fetch_coefficients("wykoff_functions", species_code)
            crown_forest = self._fetch_coefficients("crown_width_forest_grown", species_code)
            crown_open = self._fetch_coefficients("crown_width_open_grown", species_code)
            bark = self._fetch_coefficients("bark_thickness", species_code)
            
            # Get shade tolerance
            cursor.execute("""
                SELECT shade_tolerance
                FROM shade_tolerance_by_species
                WHERE species_code = ?
            """, (species_code,))
            result = cursor.fetchone()
            shade_tolerance = result[0] if result else ''
            
            # Get planted coefficient
            cursor.execute("""
                SELECT plant_coefficient
                FROM planted_coefficients
                WHERE species_code = ?
            """, (species_code,))
            result = cursor.fetchone()
            planted_coefficient = result[0] if result else 1.0
            
            # Get ecological coefficients
            ecological = self._fetch_coefficients("ecological_coefficients", species_code)
            
            return {
                'code': species_code,
                'site_index_range': (si_min, si_max),
                'dbw': dbw,
                'dbh_limits': (dbh_low, dbh_high),
                'small_tree_coeffs': small_tree,
                'large_tree_coeffs': large_tree,
                'curtis_arney_coeffs': curtis_arney,
                'wykoff_coeffs': wykoff,
                'crown_coeffs_forest': crown_forest,
                'crown_coeffs_open': crown_open,
                'bark_coeffs': bark,
                'shade_tolerance': shade_tolerance,
                'ecological_coeffs': ecological,
                'planted_coefficient': planted_coefficient
            } 
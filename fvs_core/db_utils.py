"""Database utility functions for FVS."""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

class FVSDatabase:
    def __init__(self, db_path: Union[str, Path] = 'fvspy.db'):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self._conn = None
    
    def __enter__(self):
        """Context manager entry."""
        self._conn = sqlite3.connect(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def get_species_info(self, species_code: str) -> Optional[Dict]:
        """Get all information for a species."""
        query = """
        SELECT s.*, g.*, sf.*
        FROM species s
        LEFT JOIN growth_coefficients g ON s.species_code = g.species_code
        LEFT JOIN species_scaling_factors sf ON s.species_code = sf.species_code
        WHERE s.species_code = ?
        """
        df = pd.read_sql_query(query, self._conn, params=(species_code,))
        return df.to_dict('records')[0] if not df.empty else None
    
    def get_ecological_coefficients(self, species_code: str, ecounit: str) -> Optional[Dict]:
        """Get ecological coefficients for a species and ecological unit."""
        query = """
        SELECT *
        FROM ecological_coefficients
        WHERE species_code = ? AND fvs_ecounit = ?
        """
        df = pd.read_sql_query(query, self._conn, params=(species_code, ecounit))
        return df.to_dict('records')[0] if not df.empty else None
    
    def get_forest_type_coefficients(self, species_code: str, forest_type: str) -> Optional[Dict]:
        """Get forest type coefficients for a species and forest type."""
        query = """
        SELECT *
        FROM forest_type_coefficients
        WHERE species_code = ? AND fvs_fortypcd = ?
        """
        df = pd.read_sql_query(query, self._conn, params=(species_code, forest_type))
        return df.to_dict('records')[0] if not df.empty else None
    
    def get_all_species(self) -> List[str]:
        """Get list of all species codes."""
        query = "SELECT species_code FROM species"
        df = pd.read_sql_query(query, self._conn)
        return df['species_code'].tolist()
    
    def get_all_forest_types(self) -> List[str]:
        """Get list of all forest type codes."""
        query = "SELECT fvs_fortypcd FROM forest_types"
        df = pd.read_sql_query(query, self._conn)
        return df['fvs_fortypcd'].tolist()
    
    def get_all_ecological_units(self) -> List[str]:
        """Get list of all ecological unit codes."""
        query = "SELECT fvs_ecounit FROM ecological_units"
        df = pd.read_sql_query(query, self._conn)
        return df['fvs_ecounit'].tolist()
    
    def get_growth_parameters(self, species_code: str) -> Optional[Dict]:
        """Get all growth parameters for a species."""
        query = """
        SELECT *
        FROM growth_coefficients
        WHERE species_code = ?
        """
        df = pd.read_sql_query(query, self._conn, params=(species_code,))
        return df.to_dict('records')[0] if not df.empty else None
    
    def get_scaling_factors(self, species_code: str) -> Optional[Dict]:
        """Get all scaling factors for a species."""
        query = """
        SELECT *
        FROM species_scaling_factors
        WHERE species_code = ?
        """
        df = pd.read_sql_query(query, self._conn, params=(species_code,))
        return df.to_dict('records')[0] if not df.empty else None 
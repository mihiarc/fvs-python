"""FIA database utility functions for FVS."""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd

class FIADatabase:
    def __init__(self, db_path: Union[str, Path]):
        """Initialize FIA database connection.
        
        Args:
            db_path: Path to the FIA SQLite database file.
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"FIA database not found at {self.db_path}")
        self._conn = None

    def __enter__(self):
        """Context manager entry."""
        try:
            self._conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_plot_trees(self, stand_cn: str) -> pd.DataFrame:
        """Get all trees for a given stand.
        
        Args:
            stand_cn: The stand control number to query.
            
        Returns:
            DataFrame containing tree data for the stand.
        """
        query = """
        SELECT * FROM trees 
        WHERE STAND_CN = ?
        """
        return pd.read_sql_query(query, self._conn, params=(stand_cn,))

    def get_plot_info(self, stand_cn: str) -> Optional[Dict[str, Any]]:
        """Get stand information.
        
        Args:
            stand_cn: The stand control number to query.
            
        Returns:
            Dictionary containing stand data or None if not found.
        """
        query = """
        SELECT * FROM stands 
        WHERE STAND_CN = ?
        """
        df = pd.read_sql_query(query, self._conn, params=(stand_cn,))
        return df.to_dict('records')[0] if not df.empty else None

    def get_plots_by_state(self, state_code: int) -> pd.DataFrame:
        """Get all plots for a given state.
        
        Args:
            state_code: The FIA state code to query.
            
        Returns:
            DataFrame containing plot data for the state.
        """
        query = """
        SELECT * FROM plots 
        WHERE StateCode = ?
        """
        return pd.read_sql_query(query, self._conn, params=(state_code,))

    def get_tree_measurements(self, tree_id: int) -> pd.DataFrame:
        """Get measurement history for a specific tree.
        
        Args:
            tree_id: The FIA tree ID to query.
            
        Returns:
            DataFrame containing measurement history for the tree.
        """
        query = """
        SELECT * FROM tree_measurements 
        WHERE TreeID = ?
        ORDER BY MeasurementYear
        """
        return pd.read_sql_query(query, self._conn, params=(tree_id,)) 
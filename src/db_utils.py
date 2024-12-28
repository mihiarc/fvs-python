"""Database utility functions for FVS."""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd

class FVSDatabase:
    def __init__(self, db_path: Union[str, Path] = 'fvspy.db'):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self._conn = None

    def __enter__(self):
        """Context manager entry."""
        try:
            self._conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise  # Re-raise the exception
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def create_database(self, schema_file: Union[str, Path]) -> None:
        """Creates the database and its tables from a schema file.
        
        Args:
            schema_file: Path to the SQL schema file.
            
        Raises:
            sqlite3.Error: If there's an error creating the database.
        """
        try:
            with open(schema_file, 'r') as f:
                schema = f.read()
            self._conn.executescript(schema)
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating database: {e}")
            if self._conn:
                self._conn.rollback()
            raise

    def get_species_info(self, species_code: str) -> Optional[Dict[str, Any]]:
        """Get all information for a species.

        Args:
            species_code: The species code to look up.

        Returns:
            A dictionary containing all information for the given species, or None if not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT *
            FROM species
            NATURAL FULL OUTER JOIN height_diameter_coefficients
            NATURAL FULL OUTER JOIN small_tree_coefficients
            NATURAL FULL OUTER JOIN large_tree_coefficients
            NATURAL FULL OUTER JOIN species_parameters
            NATURAL FULL OUTER JOIN crown_ratio_coefficients
            WHERE species_code = ?;
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code,))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving species info: {e}")
            return None

    def get_ecological_coefficients(self, species_code: str, ecounit: str) -> Optional[Dict[str, Any]]:
        """Get ecological coefficients for a species and ecological unit.

        Args:
            species_code: The species code to look up.
            ecounit: The ecological unit code.

        Returns:
            A dictionary containing base coefficients, adjustments, and total values,
            or None if the combination is not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT 
                e.fvs_ecounit,
                CAST(e.base_b0 AS REAL) as base_b0,
                CAST(e.base_b1 AS REAL) as base_b1,
                CAST(e.base_b2 AS REAL) as base_b2,
                CAST(e.base_b3 AS REAL) as base_b3,
                CAST(e.base_b4 AS REAL) as base_b4,
                CAST(e.base_b5 AS REAL) as base_b5,
                CAST(e.base_b6 AS REAL) as base_b6,
                CAST(e.base_b7 AS REAL) as base_b7,
                CAST(e.base_b8 AS REAL) as base_b8,
                CAST(e.base_b9 AS REAL) as base_b9,
                CAST(e.base_b10 AS REAL) as base_b10,
                CAST(e.base_b11 AS REAL) as base_b11,
                CAST(a.adjustment_b0 AS REAL) as adjustment_b0,
                CAST(a.adjustment_b1 AS REAL) as adjustment_b1,
                CAST(a.adjustment_b2 AS REAL) as adjustment_b2,
                CAST(a.adjustment_b3 AS REAL) as adjustment_b3,
                CAST(a.adjustment_b4 AS REAL) as adjustment_b4,
                CAST(a.adjustment_b5 AS REAL) as adjustment_b5,
                CAST(a.adjustment_b6 AS REAL) as adjustment_b6,
                CAST(a.adjustment_b7 AS REAL) as adjustment_b7,
                CAST(a.adjustment_b8 AS REAL) as adjustment_b8,
                CAST(a.adjustment_b9 AS REAL) as adjustment_b9,
                CAST(a.adjustment_b10 AS REAL) as adjustment_b10,
                CAST(a.adjustment_b11 AS REAL) as adjustment_b11,
                CAST(e.base_b0 + COALESCE(a.adjustment_b0, 0) AS REAL) as total_b0,
                CAST(e.base_b1 + COALESCE(a.adjustment_b1, 0) AS REAL) as total_b1,
                CAST(e.base_b2 + COALESCE(a.adjustment_b2, 0) AS REAL) as total_b2,
                CAST(e.base_b3 + COALESCE(a.adjustment_b3, 0) AS REAL) as total_b3,
                CAST(e.base_b4 + COALESCE(a.adjustment_b4, 0) AS REAL) as total_b4,
                CAST(e.base_b5 + COALESCE(a.adjustment_b5, 0) AS REAL) as total_b5,
                CAST(e.base_b6 + COALESCE(a.adjustment_b6, 0) AS REAL) as total_b6,
                CAST(e.base_b7 + COALESCE(a.adjustment_b7, 0) AS REAL) as total_b7,
                CAST(e.base_b8 + COALESCE(a.adjustment_b8, 0) AS REAL) as total_b8,
                CAST(e.base_b9 + COALESCE(a.adjustment_b9, 0) AS REAL) as total_b9,
                CAST(e.base_b10 + COALESCE(a.adjustment_b10, 0) AS REAL) as total_b10,
                CAST(e.base_b11 + COALESCE(a.adjustment_b11, 0) AS REAL) as total_b11
            FROM ecological_coefficients e
            LEFT JOIN ecological_species_adjustments a 
                ON e.fvs_ecounit = a.fvs_ecounit AND a.species_code = ?
            WHERE e.fvs_ecounit = ?
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code, ecounit))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving ecological coefficients: {e}")
            return None

    def get_forest_type_coefficients(self, species_code: str, forest_type: str) -> Optional[Dict[str, Any]]:
        """Get forest type coefficients for a species and forest type.

        Args:
            species_code: The species code to look up.
            forest_type: The forest type code.

        Returns:
            A dictionary containing base coefficients, adjustments, and total values,
            or None if the combination is not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT 
                f.fvs_fortypcd,
                CAST(f.base_lohd AS REAL) as base_lohd,
                CAST(f.base_nohd AS REAL) as base_nohd,
                CAST(f.base_okpn AS REAL) as base_okpn,
                CAST(f.base_sfhp AS REAL) as base_sfhp,
                CAST(f.base_uphd AS REAL) as base_uphd,
                CAST(f.base_upok AS REAL) as base_upok,
                CAST(f.base_ylpn AS REAL) as base_ylpn,
                CAST(a.adjustment_lohd AS REAL) as adjustment_lohd,
                CAST(a.adjustment_nohd AS REAL) as adjustment_nohd,
                CAST(a.adjustment_okpn AS REAL) as adjustment_okpn,
                CAST(a.adjustment_sfhp AS REAL) as adjustment_sfhp,
                CAST(a.adjustment_uphd AS REAL) as adjustment_uphd,
                CAST(a.adjustment_upok AS REAL) as adjustment_upok,
                CAST(a.adjustment_ylpn AS REAL) as adjustment_ylpn,
                CAST(f.base_lohd + COALESCE(a.adjustment_lohd, 0) AS REAL) as total_lohd,
                CAST(f.base_nohd + COALESCE(a.adjustment_nohd, 0) AS REAL) as total_nohd,
                CAST(f.base_okpn + COALESCE(a.adjustment_okpn, 0) AS REAL) as total_okpn,
                CAST(f.base_sfhp + COALESCE(a.adjustment_sfhp, 0) AS REAL) as total_sfhp,
                CAST(f.base_uphd + COALESCE(a.adjustment_uphd, 0) AS REAL) as total_uphd,
                CAST(f.base_upok + COALESCE(a.adjustment_upok, 0) AS REAL) as total_upok,
                CAST(f.base_ylpn + COALESCE(a.adjustment_ylpn, 0) AS REAL) as total_ylpn
            FROM forest_type_coefficients f
            LEFT JOIN forest_type_species_adjustments a 
                ON f.fvs_fortypcd = a.fvs_fortypcd AND a.species_code = ?
            WHERE f.fvs_fortypcd = ?
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code, forest_type))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving forest type coefficients: {e}")
            return None

    def get_all_species(self) -> List[str]:
        """Get list of all species codes.

        Returns:
            A list of species codes.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = "SELECT species_code FROM species"
            df = pd.read_sql_query(query, self._conn)
            return df['species_code'].tolist()
        except sqlite3.Error as e:
            print(f"Error retrieving species list: {e}")
            return []

    def get_all_forest_types(self) -> List[str]:
        """Get list of all forest type codes.

        Returns:
            A list of forest type codes.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = "SELECT fvs_fortypcd FROM forest_types"
            df = pd.read_sql_query(query, self._conn)
            return df['fvs_fortypcd'].tolist()
        except sqlite3.Error as e:
            print(f"Error retrieving forest types list: {e}")
            return []

    def get_all_ecological_units(self) -> List[str]:
        """Get list of all ecological unit codes.

        Returns:
            A list of ecological unit codes.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = "SELECT fvs_ecounit FROM ecological_units"
            df = pd.read_sql_query(query, self._conn)
            return df['fvs_ecounit'].tolist()
        except sqlite3.Error as e:
            print(f"Error retrieving ecological units list: {e}")
            return []

    def get_height_diameter_coefficients(self, species_code: str) -> Optional[Dict[str, Any]]:
        """Get height-diameter coefficients for a species.

        Args:
            species_code: The species code to look up.

        Returns:
            A dictionary containing height-diameter coefficients, or None if not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT *
            FROM height_diameter_coefficients
            WHERE species_code = ?
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code,))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving height-diameter coefficients: {e}")
            return None

    def get_small_tree_coefficients(self, species_code: str) -> Optional[Dict[str, Any]]:
        """Get small tree growth coefficients for a species.

        Args:
            species_code: The species code to look up.

        Returns:
            A dictionary containing small tree coefficients, or None if not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT *
            FROM small_tree_coefficients
            WHERE species_code = ?
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code,))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving small tree coefficients: {e}")
            return None

    def get_large_tree_coefficients(self, species_code: str) -> Optional[Dict[str, Any]]:
        """Get large tree growth coefficients for a species.

        Args:
            species_code: The species code to look up.

        Returns:
            A dictionary containing large tree coefficients, or None if not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT *
            FROM large_tree_coefficients
            WHERE species_code = ?
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code,))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving large tree coefficients: {e}")
            return None

    def get_species_parameters(self, species_code: str) -> Optional[Dict[str, Any]]:
        """Get species parameters.

        Args:
            species_code: The species code to look up.

        Returns:
            A dictionary containing species parameters, or None if not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT 
                species_code,
                si_min,
                si_max,
                CAST(dbh_min AS REAL) as dbh_min,
                CAST(dbh_max AS REAL) as dbh_max,
                CAST(growth_transition_dbh_min AS REAL) as growth_transition_dbh_min,
                CAST(growth_transition_dbh_max AS REAL) as growth_transition_dbh_max,
                CAST(Dbw AS REAL) as Dbw,
                CAST(Bark_b0 AS REAL) as Bark_b0,
                CAST(Bark_b1 AS REAL) as Bark_b1
            FROM species_parameters
            WHERE species_code = ?
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code,))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving species parameters: {e}")
            return None

    def get_crown_ratio_coefficients(self, species_code: str) -> Optional[Dict[str, Any]]:
        """Get crown ratio coefficients for a species.

        Args:
            species_code: The species code to look up.

        Returns:
            A dictionary containing crown ratio coefficients, or None if not found.

        Raises:
            sqlite3.Error: If there's an error querying the database.
        """
        try:
            query = """
            SELECT 
                species_code,
                acr_equation_type,
                CAST(a AS REAL) as a,
                CAST(b0 AS REAL) as b0,
                CAST(b1 AS REAL) as b1,
                CAST(c AS REAL) as c,
                CAST(d0 AS REAL) as d0,
                CAST(d1 AS REAL) as d1,
                CAST(d2 AS REAL) as d2,
                CAST(sd AS REAL) as sd,
                CAST(Xmin AS REAL) as Xmin,
                CAST(Xmax AS REAL) as Xmax
            FROM crown_ratio_coefficients
            WHERE species_code = ?
            """
            df = pd.read_sql_query(query, self._conn, params=(species_code,))
            return df.to_dict('records')[0] if not df.empty else None
        except sqlite3.Error as e:
            print(f"Error retrieving crown ratio coefficients: {e}")
            return None 
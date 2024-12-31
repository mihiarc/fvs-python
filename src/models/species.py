"""Species configuration and management.

This module contains the SpeciesConfig class which manages species-specific
parameters, growth coefficients, and validation ranges for the forest growth
simulator.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional, Union
from pathlib import Path
from .database import DatabaseConnection

@dataclass
class SpeciesConfig:
    """Configuration for a tree species including all growth parameters.
    
    This class holds all species-specific parameters needed for growth simulation,
    including coefficients for various growth equations, crown calculations, and
    environmental responses.
    
    Attributes:
        code: Species identifier (LP, SP, LL, or SA)
        site_index_range: Valid range for site index (min, max)
        dbw: Diameter breakpoint for switching between small and large tree models
        
        small_tree_coeffs: Coefficients for small tree growth
        large_tree_coeffs: Coefficients for large tree growth
        curtis_arney_coeffs: Coefficients for Curtis-Arney height-diameter relationship
        wykoff_coeffs: Coefficients for Wykoff height-diameter relationship
        
        crown_coeffs_forest: Coefficients for forest-grown crown width
        crown_coeffs_open: Coefficients for open-grown crown width
        bark_coeffs: Coefficients for bark thickness calculation
        
        shade_tolerance: Shade tolerance classification
        ecological_coeffs: Coefficients for ecological unit effects
        
        dbh_limits: Valid range for DBH (min, max)
        planted_coefficient: Coefficient for planted stand effects
    """
    # Basic info
    code: str
    site_index_range: Tuple[float, float]
    dbw: float
    
    # Growth coefficients
    small_tree_coeffs: Dict[str, float] = field(default_factory=dict)
    large_tree_coeffs: Dict[str, float] = field(default_factory=dict)
    curtis_arney_coeffs: Dict[str, float] = field(default_factory=dict)
    wykoff_coeffs: Dict[str, float] = field(default_factory=dict)
    
    # Crown and bark
    crown_coeffs_forest: Dict[str, float] = field(default_factory=dict)
    crown_coeffs_open: Dict[str, float] = field(default_factory=dict)
    bark_coeffs: Dict[str, float] = field(default_factory=dict)
    
    # Environmental
    shade_tolerance: str = field(default='')
    ecological_coeffs: Dict[str, float] = field(default_factory=dict)
    
    # Validation limits
    dbh_limits: Tuple[float, float] = field(default=(0.0, 100.0))
    planted_coefficient: float = field(default=1.0)

    def __post_init__(self):
        """Validate inputs after initialization."""
        if not self.code in ['LP', 'SP', 'LL', 'SA']:
            raise ValueError(f"Invalid species code: {self.code}")
        
        if not self.site_index_range[0] < self.site_index_range[1]:
            raise ValueError(f"Invalid site index range: {self.site_index_range}")
        
        if self.dbw <= 0:
            raise ValueError(f"Diameter breakpoint must be positive, got {self.dbw}")
    
    @classmethod
    def from_database(cls, code: str, db_path: Optional[Union[str, Path]] = None) -> 'SpeciesConfig':
        """Create a SpeciesConfig instance from database data.
        
        Args:
            code: Species code to load
            db_path: Optional path to database file. If None, uses default location.
            
        Returns:
            SpeciesConfig instance with data loaded from database
            
        Raises:
            ValueError: If species code not found in database
        """
        with DatabaseConnection(str(db_path) if db_path else None) as db:
            data = db.fetch_species_data(code)
            return cls(**data)
    
    def validate_tree(self, dbh: float, height: float, site_index: float) -> None:
        """Validate tree measurements against species constraints.
        
        Args:
            dbh: Diameter at breast height to validate
            height: Total height to validate
            site_index: Site index to validate
            
        Raises:
            ValueError: If any measurements are outside valid ranges
        """
        if not self.dbh_limits[0] <= dbh <= self.dbh_limits[1]:
            raise ValueError(
                f"DBH {dbh} outside valid range {self.dbh_limits} for {self.code}")
        
        if not self.site_index_range[0] <= site_index <= self.site_index_range[1]:
            raise ValueError(
                f"Site index {site_index} outside valid range {self.site_index_range} for {self.code}")
    
    def get_typical_rotation(self) -> Tuple[int, int]:
        """Get typical rotation age range for the species.
        
        Returns:
            Tuple of (minimum rotation age, maximum rotation age)
        """
        rotation_ranges = {
            'LP': (20, 30),  # Loblolly Pine
            'SP': (30, 40),  # Shortleaf Pine
            'LL': (35, 45),  # Longleaf Pine
            'SA': (25, 35)   # Slash Pine
        }
        return rotation_ranges[self.code] 
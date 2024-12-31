"""Tree class representing an individual tree in a forest stand.

This module contains the Tree class which is the fundamental unit of the forest growth
simulator. Each Tree instance represents a single tree with its attributes and methods
for growth, competition, and other characteristics.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import math

@dataclass
class Tree:
    """A class representing an individual tree in a forest stand.
    
    Attributes:
        species_code: Species identifier (LP, SP, LL, or SA)
        dbh: Diameter at breast height in inches
        height: Total height in feet
        crown_ratio: Ratio of live crown to total height (0-1)
        forest_crown_width: Crown width in forest conditions (feet)
        open_crown_width: Crown width in open-grown conditions (feet)
        expansion_factor: Number of trees per acre this tree represents
        
    Optional Attributes:
        previous_dbh: DBH from previous growth period
        previous_height: Height from previous growth period
        growth_increment: Last period's diameter growth
        pccf: Point crown competition factor
        ccf: Crown competition factor
        bark_thickness: Thickness of bark in inches
        shade_tolerance: Species shade tolerance classification
        ecological_unit: Ecological unit identifier
    """
    # Required attributes
    species_code: str
    dbh: float
    height: float
    
    # Optional attributes with defaults
    crown_ratio: float = field(default=0.0)
    forest_crown_width: float = field(default=0.0)
    open_crown_width: float = field(default=0.0)
    expansion_factor: float = field(default=1.0)
    
    # Growth tracking
    previous_dbh: Optional[float] = field(default=None)
    previous_height: Optional[float] = field(default=None)
    growth_increment: Optional[float] = field(default=None)
    
    # Competition metrics
    pccf: float = field(default=0.0)
    ccf: float = field(default=0.0)
    
    # Additional characteristics
    bark_thickness: float = field(default=0.0)
    shade_tolerance: str = field(default='')
    ecological_unit: str = field(default='')

    def __post_init__(self):
        """Validate inputs after initialization."""
        if not self.species_code in ['LP', 'SP', 'LL', 'SA']:
            raise ValueError(f"Invalid species code: {self.species_code}")
        if self.dbh <= 0:
            raise ValueError(f"DBH must be positive, got {self.dbh}")
        if self.height <= 0:
            raise ValueError(f"Height must be positive, got {self.height}")
        if not 0 <= self.crown_ratio <= 1:
            raise ValueError(f"Crown ratio must be between 0 and 1, got {self.crown_ratio}")
    
    @property
    def basal_area(self) -> float:
        """Calculate basal area in square feet."""
        return 0.005454 * self.dbh * self.dbh
    
    @property
    def basal_area_per_acre(self) -> float:
        """Calculate basal area per acre in square feet."""
        return self.basal_area * self.expansion_factor
    
    def update_growth(self, new_dbh: float, new_height: float) -> None:
        """Update tree measurements after growth.
        
        Args:
            new_dbh: New diameter at breast height
            new_height: New total height
        """
        self.previous_dbh = self.dbh
        self.previous_height = self.height
        self.dbh = new_dbh
        self.height = new_height
        if self.previous_dbh is not None:
            self.growth_increment = self.dbh - self.previous_dbh
    
    def update_competition(self, pccf: float, ccf: float) -> None:
        """Update competition metrics.
        
        Args:
            pccf: New point crown competition factor
            ccf: New crown competition factor
        """
        self.pccf = pccf
        self.ccf = ccf
    
    def __str__(self) -> str:
        """Return string representation of the tree."""
        return (f"{self.species_code} tree: "
                f"{self.dbh:.1f}\" DBH, {self.height:.1f}' tall") 
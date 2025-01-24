"""
Tree class representing an individual loblolly pine tree.
Implements both small-tree and large-tree growth models.
"""
import math
import yaml
from pathlib import Path

class Tree:
    def __init__(self, dbh, height, age=0, crown_ratio=0.85):
        """Initialize a tree with basic measurements.
        
        Args:
            dbh: Diameter at breast height (inches)
            height: Total height (feet)
            age: Tree age in years
            crown_ratio: Initial crown ratio (proportion of tree height with live crown)
        """
        self.dbh = dbh
        self.height = height
        self.age = age
        self.crown_ratio = crown_ratio
        
        # Load configuration
        config_path = Path(__file__).parent.parent / 'config' / 'loblolly_params.yaml'
        with open(config_path, 'r') as f:
            self.params = yaml.safe_load(f)
    
    def grow(self, site_index: float, competition_factor: float) -> None:
        """Grow the tree for one year.
        
        Args:
            site_index: Site index (base age 25) in feet
            competition_factor: Competition factor (0-1)
            
        Raises:
            ValueError: If site_index is negative or competition_factor is outside [0,1]
        """
        if site_index <= 0:
            raise ValueError(f"Site index must be positive, got {site_index}")
        if not 0 <= competition_factor <= 1:
            raise ValueError(f"Competition factor must be between 0 and 1, got {competition_factor}")
        
        # Increment age
        self.age += 1
        
        # Determine which growth model to use based on size
        # Start transition very early with wider zone
        if self.dbh < 1.0:  # Pure small tree model below 1"
            self._grow_small_tree(site_index, competition_factor)
        elif self.dbh > 3.0:  # Pure large tree model above 3"
            self._grow_large_tree(site_index, competition_factor)
        else:
            # Wide transition zone (1" to 3") with non-linear weighting
            # Use sigmoid function for smoother transition
            relative_pos = (self.dbh - 1.0) / 2.0  # 0 to 1 over 1" to 3"
            weight = 1.0 / (1.0 + math.exp(-6 * (relative_pos - 0.5)))  # Sigmoid centered at 2"
            self._grow_transition(site_index, competition_factor, weight)
        
        # Update crown ratio and age
        self._update_crown_ratio(competition_factor)
    
    def _grow_small_tree(self, site_index, competition_factor):
        """Implement small tree height growth model.
        
        Uses modified Chapman-Richards growth function with:
        1. Moderate early growth rate
        2. Strong site index response
        3. Reduced competition sensitivity
        4. Smoother transition to large tree growth
        """
        p = self.params['small_tree']
        
        # Calculate potential height growth using modified Chapman-Richards
        # Add age-dependent boost to early growth but cap it
        age_factor = min(1.5, 1.8 / (1.0 + 0.3 * self.age))  # Cap early boost
        potential_growth = (
            p['c1'] * 1.0 *  # Neutral base rate
            (site_index ** p['c2']) * 
            (1.0 - math.exp(p['c3'] * self.age)) ** (p['c4'] * (site_index ** p['c5'])) *
            age_factor  # Moderate early boost
        )
        
        # Reduce competition effect for very small trees
        size_factor = min(1.0, self.dbh / 3.0)  # Full effect at DBH = 3.0
        competition_effect = 0.2 + 0.2 * size_factor  # 20-40% reduction
        actual_growth = potential_growth * (1.0 - competition_effect * competition_factor)
        
        # Ensure minimum growth in early years but cap it
        actual_growth = min(1.2, max(0.3, actual_growth))  # Between 0.3 and 1.2 feet
        
        # Update height
        self.height += actual_growth
        
        # Update DBH using height-diameter relationship
        initial_dbh = self.dbh
        self._update_dbh_from_height()
        
        # Ensure positive but capped DBH growth
        min_growth = 0.05 if self.age <= 2 else 0.02  # Higher minimum only in first 2 years
        max_growth = 0.8  # Cap maximum growth
        dbh_growth = max(min_growth, min(max_growth, self.dbh - initial_dbh))
        self.dbh = initial_dbh + dbh_growth
    
    def _grow_large_tree(self, site_index, competition_factor):
        """Implement large tree diameter growth model.
        
        Uses modified diameter growth equation with:
        1. Moderate growth rate for consistency
        2. Strong crown ratio response
        3. Increased competition sensitivity
        4. Moderate size-dependent growth reduction
        """
        p = self.params['large_tree']
        
        # Calculate ln(DDS) with moderate size-dependent reduction
        size_factor = math.exp(-0.015 * self.dbh)  # Slower decline with size
        ln_dds = (
            p['b1'] * (1.0 + 0.4 * size_factor) +  # Moderate size effect
            p['b2'] * math.log(self.dbh) +
            p['b3'] * self.dbh**2 +
            p['b4'] * math.log(self.crown_ratio) +
            p['b5'] * (self.height / site_index) +
            p['b6'] * site_index +
            p['planting_factor']
        )
        
        # Apply moderate competition modifier for larger trees
        competition_effect = 0.4 + 0.2 * (1 - size_factor)  # 40-60% reduction at max competition
        ln_dds *= (1.0 - competition_effect * competition_factor)
        
        # Convert back to diameter growth and update DBH
        dds = math.exp(ln_dds)
        initial_dbh = self.dbh
        new_dbh = math.sqrt(self.dbh**2 + dds)
        
        # Ensure growth is within reasonable bounds
        dbh_growth = new_dbh - initial_dbh
        min_growth = 0.2  # Minimum growth for large trees
        max_growth = 0.6  # Maximum growth for large trees
        dbh_growth = max(min_growth, min(max_growth, dbh_growth))
        self.dbh = initial_dbh + dbh_growth
        
        # Update height using height-diameter relationship
        self._update_height_from_dbh()
    
    def _grow_transition(self, site_index, competition_factor, weight):
        """Blend small and large tree growth models."""
        # Store initial state
        initial_dbh = self.dbh
        initial_height = self.height
        
        # Grow using both models
        self._grow_small_tree(site_index, competition_factor)
        small_dbh = self.dbh
        small_height = self.height
        
        # Reset and grow with large tree model
        self.dbh = initial_dbh
        self.height = initial_height
        self._grow_large_tree(site_index, competition_factor)
        
        # Weighted average of results
        self.dbh = (1 - weight) * small_dbh + weight * self.dbh
        self.height = (1 - weight) * small_height + weight * self.height
    
    def _update_crown_ratio(self, competition_factor):
        """Update crown ratio based on tree size, age and competition.
        
        Crown ratio should:
        1. Decrease with increasing competition
        2. Decrease with age (slower in young trees)
        3. Stay within biological limits
        """
        # Base crown ratio reduction from competition
        competition_effect = 0.1 * competition_factor
        
        # Age effect (sigmoid curve)
        age_effect = 0.05 / (1 + math.exp(-0.1 * (self.age - 15)))
        
        # Update crown ratio
        self.crown_ratio = max(
            0.2,  # Minimum crown ratio
            min(
                0.85,  # Maximum crown ratio
                self.crown_ratio * (1.0 - competition_effect - age_effect)
            )
        )
    
    def _update_dbh_from_height(self):
        """Update DBH based on height using Curtis-Arney equation."""
        p = self.params['height_diameter']
        
        # Solve Curtis-Arney equation for DBH
        if self.height <= 4.5:
            self.dbh = max(self.dbh, 0.1)  # Keep current DBH if larger than minimum
        else:
            # Numerical approximation since equation can't be directly solved for DBH
            target_height = self.height
            dbh = self.dbh  # Start with current DBH as guess
            
            for _ in range(5):  # Simple iteration to converge
                height_calc = 4.5 + p['p2'] * math.exp(-p['p3'] * dbh**p['p4'])
                if abs(height_calc - target_height) < 0.01:
                    break
                dbh *= (target_height / height_calc)**0.5
            
            self.dbh = max(self.dbh, dbh)  # Never decrease DBH
    
    def _update_height_from_dbh(self):
        """Update height based on DBH using Curtis-Arney equation."""
        p = self.params['height_diameter']
        
        if self.dbh < p['dbw']:
            # Linear interpolation for very small trees
            self.height = 4.5 * (self.dbh / p['dbw'])
        else:
            # Curtis-Arney equation
            self.height = 4.5 + p['p2'] * math.exp(-p['p3'] * self.dbh**p['p4'])
    
    def get_volume(self):
        """Calculate tree volume in cubic feet."""
        # Simple volume calculation using form factor
        basal_area = math.pi * (self.dbh / 24)**2  # basal area in square feet
        return basal_area * self.height * self.params['volume']['form_factor'] 
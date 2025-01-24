"""
Tree class representing an individual loblolly pine tree.
Implements both small-tree and large-tree growth models.
"""
import math
import yaml
import numpy as np
from scipy.stats import weibull_min
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
    
    def grow(self, site_index: float, competition_factor: float, rank: float = 0.5, relsdi: float = 5.0) -> None:
        """Grow the tree for five years.
        
        Args:
            site_index: Site index (base age 25) in feet
            competition_factor: Competition factor (0-1)
            rank: Tree's rank in diameter distribution (0-1)
            relsdi: Relative stand density index (0-12)
        """
        # Increment age by 5 years
        self.age += 5
        
        # Get transition parameters
        xmin = self.params['transition']['Xmin']
        xmax = self.params['transition']['Xmax']
        
        # Calculate weight for blending growth models
        if self.dbh < xmin:
            weight = 0.0
        elif self.dbh > xmax:
            weight = 1.0
        else:
            weight = (self.dbh - xmin) / (xmax - xmin)
        
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
        large_dbh = self.dbh
        large_height = self.height
        
        # Linear blending of results
        self.dbh = (1 - weight) * small_dbh + weight * large_dbh
        self.height = (1 - weight) * small_height + weight * large_height
        
        # Update crown ratio using Weibull model
        self._update_crown_ratio_weibull(rank, relsdi, competition_factor)
    
    def _grow_small_tree(self, site_index, competition_factor):
        """Implement small tree height growth model using Chapman-Richards function."""
        p = self.params['small_tree_growth']
        
        # Calculate potential 5-year height growth
        potential_growth = (
            p['c1'] * (site_index ** p['c2']) * 
            (1.0 - math.exp(p['c3'] * self.age)) ** 
            (p['c4'] * (site_index ** p['c5']))
        )
        
        # Apply competition effect
        actual_growth = potential_growth * (1.0 - 0.3 * competition_factor)
        
        # Update height
        self.height += actual_growth
        
        # Update DBH using height-diameter relationship
        self._update_dbh_from_height()
    
    def _grow_large_tree(self, site_index, competition_factor):
        """Implement large tree diameter growth model."""
        p = self.params['large_tree_growth']
        
        # Calculate ln(DDS) - 5-year growth
        ln_dds = (
            p['b1'] +
            p['b2'] * math.log(self.dbh) +
            p['b3'] * self.dbh**2 +
            p['b4'] * math.log(self.crown_ratio) +
            p['b5'] * (self.height / site_index) +
            p['b6'] * site_index +
            p['planting_factor']
        )
        
        # Apply competition effect
        ln_dds *= (1.0 - 0.5 * competition_factor)
        
        # Convert to diameter growth and update DBH
        dds = math.exp(ln_dds)
        self.dbh = math.sqrt(self.dbh**2 + dds)
        
        # Update height using height-diameter relationship
        self._update_height_from_dbh()
    
    def _update_crown_ratio_weibull(self, rank, relsdi, competition_factor):
        """Update crown ratio using Weibull-based model.
        
        Args:
            rank: Tree's rank in diameter distribution (0-1)
            relsdi: Relative stand density index (0-12)
            competition_factor: Competition factor (0-1)
        """
        # Calculate average crown ratio based on stand density
        p = self.params['crown']
        acr = p['acr_b0'] + p['acr_b1'] * math.log(max(1.0, relsdi))
        acr = max(0.2, min(0.85, acr))
        
        # Calculate Weibull parameters
        location = p['weibull_a'] / 100.0
        scale = max(0.03, (p['weibull_b0'] + p['weibull_b1'] * acr) / 100.0)
        shape = max(2.0, p['weibull_c'])
        
        # Calculate density-dependent scaling factor (more sensitive to competition)
        scale_factor = 1.0 - 0.7 * competition_factor
        
        try:
            # Calculate new crown ratio using Weibull distribution
            x = max(0.001, min(0.999, rank))  # Bound rank to avoid numerical issues
            new_cr = weibull_min.ppf(x, shape, loc=location * scale_factor, scale=scale * scale_factor)
            
            # Apply age-related reduction
            age_factor = 1.0 - 0.003 * self.age  # 0.3% reduction per year
            new_cr *= max(0.5, age_factor)  # Cap age reduction at 50%
            
            # Ensure reasonable bounds
            self.crown_ratio = max(0.2, min(0.85, new_cr))
        except:
            # Fallback to simpler update if Weibull calculation fails
            reduction = (
                0.15 * competition_factor +  # Competition effect
                0.003 * self.age +          # Age effect
                0.1 * (1.0 - rank)          # Size effect
            )
            self.crown_ratio = max(0.2, min(0.85, 
                self.crown_ratio * (1.0 - min(0.3, reduction))))
    
    def _update_dbh_from_height(self):
        """Update DBH based on height using Curtis-Arney equation."""
        p = self.params['height_diameter']
        
        if self.height <= 4.5:
            self.dbh = p['Dbw']  # Set to minimum DBH
        else:
            # Solve Curtis-Arney equation for DBH numerically
            target_height = self.height
            dbh = self.dbh  # Start with current DBH
            
            for _ in range(5):
                height_calc = self._curtis_arney_height(dbh)
                if abs(height_calc - target_height) < 0.01:
                    break
                dbh *= (target_height / height_calc)**0.5
            
            self.dbh = dbh
    
    def _update_height_from_dbh(self):
        """Update height based on DBH using Curtis-Arney equation."""
        self.height = self._curtis_arney_height(self.dbh)
    
    def _curtis_arney_height(self, dbh):
        """Calculate height using Curtis-Arney equation."""
        p = self.params['height_diameter']
        
        if dbh < 3.0:
            # Linear interpolation for small trees
            h3 = 4.5 + p['p2'] * math.exp(-p['p3'] * 3.0**p['p4'])
            return 4.5 + (h3 - 4.5) * (dbh - p['Dbw']) / (3.0 - p['Dbw'])
        else:
            # Standard Curtis-Arney equation
            return 4.5 + p['p2'] * math.exp(-p['p3'] * dbh**p['p4'])
    
    def get_volume(self):
        """Calculate tree volume in cubic feet."""
        basal_area = math.pi * (self.dbh / 24)**2
        return basal_area * self.height * self.params['volume']['form_factor'] 
"""
Tree class representing an individual tree.
Implements both small-tree and large-tree growth models.
"""
import math
import yaml
import numpy as np
from scipy.stats import weibull_min
from pathlib import Path

class Tree:
    def __init__(self, dbh, height, species="LP", age=0, crown_ratio=0.85):
        """Initialize a tree with basic measurements.
        
        Args:
            dbh: Diameter at breast height (inches)
            height: Total height (feet)
            species: Species code (e.g., "LP" for loblolly pine)
            age: Tree age in years
            crown_ratio: Initial crown ratio (proportion of tree height with live crown)
        """
        self.dbh = dbh
        self.height = height
        self.species = species
        self.age = age
        self.crown_ratio = crown_ratio
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration using the new config loader."""
        from .config_loader import get_config_loader
        
        loader = get_config_loader()
        
        # Load species-specific parameters
        self.species_params = loader.load_species_config(self.species)
        
        # Load functional forms and site index parameters
        self.functional_forms = loader.functional_forms
        self.site_index_params = loader.site_index_params
    
    def grow(self, site_index: float, competition_factor: float, rank: float = 0.5, relsdi: float = 5.0, ba: float = 100, pbal: float = 50, slope: float = 0.05, aspect: float = 0, time_step: int = 5) -> None:
        """Grow the tree for the specified number of years.
        
        Args:
            site_index: Site index (base age 25) in feet
            competition_factor: Competition factor (0-1)
            rank: Tree's rank in diameter distribution (0-1)
            relsdi: Relative stand density index (0-12)
            ba: Stand basal area (sq ft/acre)
            pbal: Plot basal area in larger trees (sq ft/acre)
            slope: Ground slope (proportion)
            aspect: Aspect in radians
            time_step: Number of years to grow the tree (default: 5)
        """
        # Increment age by time_step years
        self.age += time_step
        
        # Get transition parameters - hardcoded for now as they aren't in the new config
        xmin = 1.0  # minimum DBH for transition (inches)
        xmax = 3.0  # maximum DBH for transition (inches)
        
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
        
        # Grow using both models, adjusting for time_step
        # Small tree model uses the Chapman-Richards function which depends on age
        # We temporarily apply the time_step to calculate growth, then restore
        original_age = self.age
        self._grow_small_tree(site_index, competition_factor, time_step)
        small_dbh = self.dbh
        small_height = self.height
        
        # Reset and grow with large tree model
        self.dbh = initial_dbh
        self.height = initial_height
        self.age = original_age  # Restore age for large tree growth calculation
        self._grow_large_tree(site_index, competition_factor, ba, pbal, slope, aspect, time_step)
        large_dbh = self.dbh
        large_height = self.height
        
        # Linear blending of results
        self.dbh = (1 - weight) * small_dbh + weight * large_dbh
        self.height = (1 - weight) * small_height + weight * large_height
        
        # Update crown ratio using Weibull model
        self._update_crown_ratio_weibull(rank, relsdi, competition_factor)
    
    def _grow_small_tree(self, site_index, competition_factor, time_step=5):
        """Implement small tree height growth model using Chapman-Richards function.
        
        Args:
            site_index: Site index (base age 25) in feet
            competition_factor: Competition factor (0-1)
            time_step: Number of years to grow (default: 5)
        """
        # For now, using hardcoded parameters since small-tree growth isn't yet in config
        p = {
            'c1': 1.1421,
            'c2': 1.0042,
            'c3': -0.0374,
            'c4': 0.7632,
            'c5': 0.0358
        }
        
        # The Chapman-Richards function computes 5-year growth
        # For other time steps, we need to adjust
        if time_step == 5:
            # Use the direct 5-year growth formula
            potential_growth = (
                p['c1'] * (site_index ** p['c2']) * 
                (1.0 - math.exp(p['c3'] * self.age)) ** 
                (p['c4'] * (site_index ** p['c5']))
            )
        else:
            # For other time periods, grow in annual increments
            # Store initial age
            initial_age = self.age - time_step
            potential_growth = 0
            
            # Calculate growth for each year in the time step
            for year in range(time_step):
                current_age = initial_age + year
                annual_growth = (
                    p['c1'] / 5 * (site_index ** p['c2']) * 
                    (1.0 - math.exp(p['c3'] * current_age)) ** 
                    (p['c4'] * (site_index ** p['c5']))
                )
                potential_growth += annual_growth
        
        # Individual tree growth model shouldn't directly use competition_factor
        # This should be captured by stand-level parameters in the large tree model
        actual_growth = potential_growth
        
        # Update height
        self.height += actual_growth
        
        # Update DBH using height-diameter relationship
        self._update_dbh_from_height()
    
    def _grow_large_tree(self, site_index, competition_factor, ba, pbal, slope, aspect, time_step=5):
        """Implement large tree diameter growth model.
        
        Args:
            site_index: Site index (base age 25) in feet
            competition_factor: Competition factor (0-1)
            ba: Stand basal area (sq ft/acre)
            pbal: Plot basal area in larger trees (sq ft/acre)
            slope: Ground slope (proportion)
            aspect: Aspect in radians
            time_step: Number of years to grow (default: 5)
        """
        # Get large tree diameter growth parameters from config
        p = self.species_params['diameter_growth']['coefficients']
            
        # Forest type and ecological unit effects (not currently implemented)
        fortype_effect = 0.0
        ecounit_effect = 0.0
        
        # Planting effect - hardcoded for now, should be moved to config
        plant_effect = 0.245669
        
        # Calculate ln(DDS) - 5-year growth using the full model
        ln_dds = (
            p['b1'] +
            p['b2'] * math.log(self.dbh) +
            p['b3'] * self.dbh**2 +
            p['b4'] * math.log(self.crown_ratio) +
            p['b5'] * (self.height / site_index) +  # RELHT
            p['b6'] * site_index +
            p['b7'] * ba +
            p['b8'] * pbal +
            p['b9'] * slope +
            p['b10'] * math.cos(aspect) * slope +
            p['b11'] * math.sin(aspect) * slope +
            fortype_effect + 
            ecounit_effect +
            plant_effect
        )
        
        # Competition is already accounted for through ba and pbal
        # No need to further modify growth based on competition_factor
        
        # Convert to diameter growth and update DBH
        # Scale growth based on time_step (model is calibrated for 5-year growth)
        dds = math.exp(ln_dds) * (time_step / 5.0)
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
        # Get crown ratio parameters
        p = self.species_params['crown_ratio']
        
        # Get the equation type
        equation_type = p['equation']
        
        # Calculate average crown ratio based on stand density using appropriate equation
        if equation_type == "4.3.1.3":
            acr = math.exp(p['d0'] + (p['d1'] * math.log(max(1.0, relsdi))) + (p['d2'] * relsdi))
        elif equation_type == "4.3.1.4":
            acr = math.exp(p['d0'] + (p['d1'] * math.log(max(1.0, relsdi))))
        else:
            # Default fallback
            acr = math.exp(3.8284 + (-0.2234 * math.log(max(1.0, relsdi))) + (0.0172 * relsdi))
        
        acr = max(0.2, min(0.85, acr))
        
        # Get Weibull parameters
        weibull_params = p['weibull']
        location = weibull_params['a'] / 100.0
        scale = max(0.03, (weibull_params['b0'] + weibull_params['b1'] * acr) / 100.0)
        shape = max(2.0, weibull_params['c'])
        
        # Calculate density-dependent scaling factor
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
        # Get height-diameter parameters
        hd_params = self.species_params['height_diameter']
        model = hd_params['model']
        p = hd_params['curtis_arney']
        
        # Store original DBH to ensure we don't decrease it
        original_dbh = self.dbh
        
        if self.height <= 4.5:
            self.dbh = max(original_dbh, p['dbw'])  # Set to minimum DBH, but never decrease
        else:
            # Solve Curtis-Arney equation for DBH numerically
            target_height = self.height
            dbh = self.dbh  # Start with current DBH
            
            for _ in range(5):
                height_calc = self._curtis_arney_height(dbh)
                if abs(height_calc - target_height) < 0.01:
                    break
                dbh *= (target_height / height_calc)**0.5
            
            # Ensure DBH never decreases
            self.dbh = max(original_dbh, dbh)
    
    def _update_height_from_dbh(self):
        """Update height based on DBH using Curtis-Arney equation."""
        self.height = self._curtis_arney_height(self.dbh)
    
    def _curtis_arney_height(self, dbh):
        """Calculate height using Curtis-Arney equation."""
        # Get Curtis-Arney parameters
        p = self.species_params['height_diameter']['curtis_arney']
        
        if dbh < 3.0:
            # Linear interpolation for small trees
            h3 = 4.5 + p['p2'] * math.exp(-p['p3'] * 3.0**p['p4'])
            return 4.5 + (h3 - 4.5) * (dbh - p['dbw']) / (3.0 - p['dbw'])
        else:
            # Standard Curtis-Arney equation
            return 4.5 + p['p2'] * math.exp(-p['p3'] * dbh**p['p4'])
    
    def get_volume(self):
        """Calculate tree volume in cubic feet."""
        # Using a standard form factor for now
        form_factor = 0.48
        basal_area = math.pi * (self.dbh / 24)**2
        return basal_area * self.height * form_factor 
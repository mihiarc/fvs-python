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
        from .crown_ratio import create_crown_ratio_model
        
        # Create crown ratio model for this species
        cr_model = create_crown_ratio_model(self.species)
        
        # Calculate CCF from competition factor (rough approximation)
        ccf = 100.0 + 100.0 * competition_factor
        
        try:
            # Predict new crown ratio using the dedicated crown ratio model
            new_cr = cr_model.predict_individual_crown_ratio(rank, relsdi, ccf)
            
            # Apply age-related reduction
            age_factor = 1.0 - 0.003 * self.age  # 0.3% reduction per year
            new_cr *= max(0.5, age_factor)  # Cap age reduction at 50%
            
            # Ensure reasonable bounds
            self.crown_ratio = max(0.05, min(0.95, new_cr))
        except Exception:
            # Fallback to simpler update if crown ratio calculation fails
            reduction = (
                0.15 * competition_factor +  # Competition effect
                0.003 * self.age +          # Age effect
                0.1 * (1.0 - rank)          # Size effect
            )
            self.crown_ratio = max(0.05, min(0.95, 
                self.crown_ratio * (1.0 - min(0.3, reduction))))
    
    def _update_dbh_from_height(self):
        """Update DBH based on height using height-diameter model."""
        from .height_diameter import create_height_diameter_model
        
        # Create height-diameter model for this species
        hd_model = create_height_diameter_model(self.species)
        
        # Store original DBH to ensure we don't decrease it
        original_dbh = self.dbh
        
        if self.height <= 4.5:
            dbw = hd_model.hd_params['curtis_arney']['dbw']
            self.dbh = max(original_dbh, dbw)  # Set to minimum DBH, but never decrease
        else:
            # Solve for DBH given target height
            dbh = hd_model.solve_dbh_from_height(
                target_height=self.height,
                initial_dbh=self.dbh
            )
            
            # Ensure DBH never decreases
            self.dbh = max(original_dbh, dbh)
    
    def _update_height_from_dbh(self):
        """Update height based on DBH using height-diameter model."""
        from .height_diameter import create_height_diameter_model
        
        # Create height-diameter model for this species
        hd_model = create_height_diameter_model(self.species)
        
        # Use the default model specified in configuration
        self.height = hd_model.predict_height(self.dbh)
    
    def get_volume(self):
        """Calculate tree volume in cubic feet using inside bark diameter."""
        from .bark_ratio import create_bark_ratio_model
        
        # Convert DBH outside bark to inside bark for volume calculations
        bark_model = create_bark_ratio_model(self.species)
        dbh_inside_bark = bark_model.apply_bark_ratio_to_dbh(self.dbh)
        
        # Calculate volume using inside bark diameter (FVS standard)
        form_factor = 0.48
        basal_area_ib = math.pi * (dbh_inside_bark / 24)**2
        return basal_area_ib * self.height * form_factor 
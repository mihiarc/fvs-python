"""
Tree class representing an individual tree.
Implements both small-tree and large-tree growth models.
"""
import math
import yaml
import numpy as np
from scipy.stats import weibull_min
from pathlib import Path
from .validation import ParameterValidator
from .logging_config import get_logger, log_model_transition

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
        # Validate parameters
        validated = ParameterValidator.validate_tree_parameters(
            dbh, height, age, crown_ratio, species
        )
        
        self.dbh = validated['dbh']
        self.height = validated['height']
        self.species = species
        self.age = validated['age']
        self.crown_ratio = validated['crown_ratio']
        
        # Set up logging
        self.logger = get_logger(__name__)
        
        # Check height-DBH relationship (disabled warning for small seedlings)
        if self.height > 4.5 and not ParameterValidator.check_height_dbh_relationship(self.dbh, self.height):
            self.logger.warning(
                f"Unusual height-DBH relationship: DBH={self.dbh}, Height={self.height}"
            )
        
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
        
        # Load growth model parameters
        try:
            growth_params_file = loader.cfg_dir / 'growth_model_parameters.yaml'
            self.growth_params = loader._load_config_file(growth_params_file)
        except Exception:
            # Fallback to defaults if file not found
            self.growth_params = {
                'growth_transitions': {'small_to_large_tree': {'xmin': 1.0, 'xmax': 3.0}},
                'small_tree_growth': {'default': {
                    'c1': 1.1421, 'c2': 1.0042, 'c3': -0.0374, 'c4': 0.7632, 'c5': 0.0358
                }}
            }
    
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
        # Validate growth parameters
        validated = ParameterValidator.validate_growth_parameters(
            site_index, competition_factor, ba, pbal, rank, relsdi,
            slope, aspect, time_step, self.species
        )
        
        # Use validated parameters
        site_index = validated['site_index']
        competition_factor = validated['competition_factor']
        ba = validated['ba']
        pbal = validated['pbal']
        rank = validated['rank']
        relsdi = validated['relsdi']
        slope = validated['slope']
        aspect = validated['aspect']
        time_step = validated['time_step']
        
        # Store initial values before any changes
        initial_age = self.age
        initial_dbh = self.dbh
        initial_height = self.height
        
        # Get transition parameters from config
        transition_params = self.growth_params['growth_transitions']['small_to_large_tree']
        xmin = transition_params['xmin']  # minimum DBH for transition (inches)
        xmax = transition_params['xmax']  # maximum DBH for transition (inches)
        
        # Calculate weight for blending growth models based on initial DBH
        if initial_dbh < xmin:
            weight = 0.0
            model_used = "small_tree"
        elif initial_dbh > xmax:
            weight = 1.0
            model_used = "large_tree"
        else:
            weight = (initial_dbh - xmin) / (xmax - xmin)
            model_used = "blended"
            
        # Log model transition if crossing threshold
        if initial_dbh < xmin and self.dbh >= xmin:
            log_model_transition(self.logger, f"{self.species}_{id(self)}", 
                                "small_tree", "blended", self.dbh)
        elif initial_dbh < xmax and self.dbh >= xmax:
            log_model_transition(self.logger, f"{self.species}_{id(self)}", 
                                "blended", "large_tree", self.dbh)
        
        # Temporarily increment age for growth calculations
        self.age = initial_age + time_step
        
        # Calculate small tree growth
        self._grow_small_tree(site_index, competition_factor, time_step)
        small_dbh = self.dbh
        small_height = self.height
        
        # Reset to initial state for large tree model
        self.dbh = initial_dbh
        self.height = initial_height
        
        # Calculate large tree growth
        self._grow_large_tree(site_index, competition_factor, ba, pbal, slope, aspect, time_step)
        large_dbh = self.dbh
        large_height = self.height
        
        # Blend results based on initial DBH
        self.dbh = (1 - weight) * small_dbh + weight * large_dbh
        self.height = (1 - weight) * small_height + weight * large_height
        
        # Ensure age is properly set after growth
        self.age = initial_age + time_step
        
        # Update crown ratio using Weibull model
        self._update_crown_ratio_weibull(rank, relsdi, competition_factor)
    
    def _grow_small_tree(self, site_index, competition_factor, time_step=5):
        """Implement small tree height growth model using Chapman-Richards function.
        
        The Chapman-Richards model predicts cumulative height at a given age,
        not periodic growth. We calculate height at current age and future age,
        then take the difference.
        
        Args:
            site_index: Site index (base age 25) in feet
            competition_factor: Competition factor (0-1)
            time_step: Number of years to grow (default: 5)
        """
        # Get parameters from config
        small_tree_params = self.growth_params.get('small_tree_growth', {})
        if self.species in small_tree_params:
            p = small_tree_params[self.species]
        else:
            p = small_tree_params.get('default', {
                'c1': 1.1421,
                'c2': 1.0042,
                'c3': -0.0374,
                'c4': 0.7632,
                'c5': 0.0358
            })
        
        # Chapman-Richards predicts cumulative height at age t
        # Height(t) = c1 * SI^c2 * (1 - exp(c3 * t))^(c4 * SI^c5)
        
        # Current age (before growth) - age was already incremented in grow()
        current_age = self.age - time_step
        future_age = self.age  # This is current_age + time_step
        
        # Calculate height at current age
        if current_age <= 0:
            current_height = 1.0  # Initial height at planting
        else:
            current_height = (
                p['c1'] * (site_index ** p['c2']) * 
                (1.0 - math.exp(p['c3'] * current_age)) ** 
                (p['c4'] * (site_index ** p['c5']))
            )
        
        # Calculate height at future age
        future_height = (
            p['c1'] * (site_index ** p['c2']) * 
            (1.0 - math.exp(p['c3'] * future_age)) ** 
            (p['c4'] * (site_index ** p['c5']))
        )
        
        # Height growth is the difference
        height_growth = future_height - current_height
        
        # Apply a modifier for competition (subtle effect for small trees)
        # Small trees are less affected by competition than large trees
        max_reduction = self.growth_params.get('competition_effects', {}).get(
            'small_tree_competition', {}).get('max_reduction', 0.2)
        competition_modifier = 1.0 - (max_reduction * competition_factor)
        actual_growth = height_growth * competition_modifier
        
        # Update height with bounds checking
        self.height = max(4.5, self.height + actual_growth)
        
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
        
        # Planting effect from config
        planting_effects = self.growth_params.get('large_tree_modifiers', {}).get('planting_effect', {})
        if self.species in planting_effects:
            plant_effect = planting_effects[self.species]
        else:
            plant_effect = planting_effects.get('default', 0.245669)
        
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
            
            # Apply age-related reduction from config
            cr_params = self.growth_params.get('crown_ratio', {})
            age_reduction_rate = cr_params.get('age_reduction', {}).get('rate', 0.003)
            max_age_reduction = cr_params.get('age_reduction', {}).get('max_reduction', 0.5)
            
            age_factor = 1.0 - age_reduction_rate * self.age
            new_cr *= max(1.0 - max_age_reduction, age_factor)
            
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
    
    def get_volume(self, volume_type: str = 'total_cubic') -> float:
        """Calculate tree volume using USFS Volume Estimator Library.
        
        Args:
            volume_type: Type of volume to return. Options:
                - 'total_cubic': Total cubic volume (default)
                - 'merchantable_cubic': Merchantable cubic volume
                - 'board_foot': Board foot volume
                - 'green_weight': Green weight in pounds
                - 'dry_weight': Dry weight in pounds
                - 'biomass_main_stem': Main stem biomass
                
        Returns:
            Volume in specified units
        """
        from .volume_library import calculate_tree_volume
        
        # Calculate volume using NVEL if available, fallback otherwise
        result = calculate_tree_volume(
            dbh=self.dbh,
            height=self.height,
            species_code=self.species
        )
        
        # Return requested volume type
        volume_mapping = {
            'total_cubic': result.total_cubic_volume,
            'gross_cubic': result.gross_cubic_volume,
            'net_cubic': result.net_cubic_volume,
            'merchantable_cubic': result.merchantable_cubic_volume,
            'board_foot': result.board_foot_volume,
            'cord': result.cord_volume,
            'green_weight': result.green_weight,
            'dry_weight': result.dry_weight,
            'sawlog_cubic': result.sawlog_cubic_volume,
            'sawlog_board_foot': result.sawlog_board_foot,
            'biomass_main_stem': result.biomass_main_stem,
            'biomass_live_branches': result.biomass_live_branches,
            'biomass_foliage': result.biomass_foliage
        }
        
        return volume_mapping.get(volume_type, result.total_cubic_volume)
    
    def get_volume_detailed(self) -> dict:
        """Get detailed volume breakdown for the tree.
        
        Returns:
            Dictionary with all volume types and biomass estimates
        """
        from .volume_library import calculate_tree_volume
        
        result = calculate_tree_volume(
            dbh=self.dbh,
            height=self.height,
            species_code=self.species
        )
        
        return result.to_dict() 
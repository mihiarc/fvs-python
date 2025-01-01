"""
Tree Growth Simulator for FVS-Python.
Handles individual tree growth calculations and model transitions.
"""

from typing import Dict, Optional
import math
import numpy as np

from .growth_models import (
    curtis_arney_height,
    calculate_small_tree_height_growth,
    calculate_large_tree_diameter_growth,
    calculate_growth_weight,
    blend_growth_estimates
)

class TreeGrowthSimulator:
    """Simulates the growth of individual trees using appropriate growth models."""
    
    def __init__(self, species: str, site_index: float, coefficients: Optional[Dict] = None):
        """
        Initialize the tree growth simulator.
        
        Args:
            species: Species code ('LP', 'SP', 'LL', 'SA')
            site_index: Site index (base age 25)
            coefficients: Optional override for species-specific coefficients
        
        Raises:
            ValueError: If species code is invalid or coefficients are missing required values
        """
        self.species = species
        self.site_index = site_index
        self.coefficients = coefficients
        
        # Validate inputs
        if not self._validate_inputs():
            raise ValueError(f"Invalid species code or coefficients: {species}")
    
    def _validate_inputs(self) -> bool:
        """Validate initialization parameters."""
        if not self.species in ['LP', 'SP', 'LL', 'SA']:
            return False
        return True
    
    def simulate_growth(self, tree: 'Tree', stand_conditions: Dict) -> Dict:
        """
        Simulate one growth period for a tree.
        
        Args:
            tree: Tree object with current state
            stand_conditions: Dict containing stand-level metrics
                Required keys: basal_area, plot_basal_area_larger,
                             crown_competition_factor, relative_height
        
        Returns:
            Dict containing growth results:
                - height_growth: Predicted height growth (ft)
                - dbh_growth: Predicted DBH growth (inches)
                - crown_ratio_change: Predicted crown ratio change
        
        Raises:
            ValueError: If required stand conditions are missing
        """
        self._validate_stand_conditions(stand_conditions)
        
        if tree.dbh < 2.0:
            return self._small_tree_growth(tree, stand_conditions)
        elif tree.dbh > 3.0:
            return self._large_tree_growth(tree, stand_conditions)
        else:
            return self._transition_growth(tree, stand_conditions)
    
    def _validate_stand_conditions(self, conditions: Dict) -> None:
        """Validate required stand condition parameters are present."""
        required_keys = {
            'basal_area', 'plot_basal_area_larger',
            'crown_competition_factor', 'relative_height'
        }
        missing = required_keys - set(conditions.keys())
        if missing:
            raise ValueError(f"Missing required stand conditions: {missing}")
    
    def _small_tree_growth(self, tree: 'Tree', conditions: Dict) -> Dict:
        """Calculate growth for small trees (DBH < 2.0 inches)."""
        # Calculate potential height growth using Chapman-Richards
        potential_height = calculate_small_tree_height_growth(
            si=self.site_index,
            aget=tree.age,
            ht=tree.height,
            c1=self.coefficients['c1'],
            c2=self.coefficients['c2'],
            c3=self.coefficients['c3'],
            c4=self.coefficients['c4'],
            c5=self.coefficients['c5']
        )
        
        # Apply competition modifier
        height_growth = potential_height * self._competition_modifier(tree, conditions)
        
        # Calculate DBH from height using reverse Curtis-Arney
        new_height = tree.height + height_growth
        new_dbh = self._estimate_dbh_from_height(new_height)
        dbh_growth = new_dbh - tree.dbh
        
        return {
            'height_growth': height_growth,
            'dbh_growth': dbh_growth,
            'crown_ratio_change': self._estimate_crown_ratio_change(tree, conditions)
        }
    
    def _large_tree_growth(self, tree: 'Tree', conditions: Dict) -> Dict:
        """Calculate growth for large trees (DBH >= 3.0 inches)."""
        # Calculate diameter growth using large tree model
        ln_dds = calculate_large_tree_diameter_growth(
            dbh=tree.dbh,
            cr=tree.crown_ratio,
            relht=conditions['relative_height'],
            si=self.site_index,
            ba=conditions['basal_area'],
            pbal=conditions['plot_basal_area_larger'],
            slope=conditions.get('slope', 0),
            aspect=conditions.get('aspect', 0),
            fortype=self.coefficients['forest_type_factor'],
            ecounit=self.coefficients['ecounit_factor'],
            plant=self.coefficients['planting_factor'],
            b_coeffs=self.coefficients
        )
        
        # Convert ln(DDS) to diameter growth
        dbh_growth = math.exp(ln_dds)
        
        # Calculate height growth using Curtis-Arney relationship
        new_dbh = tree.dbh + dbh_growth
        new_height = curtis_arney_height(new_dbh, self.species, self.coefficients)
        height_growth = new_height - tree.height
        
        return {
            'height_growth': height_growth,
            'dbh_growth': dbh_growth,
            'crown_ratio_change': self._estimate_crown_ratio_change(tree, conditions)
        }
    
    def _transition_growth(self, tree: 'Tree', conditions: Dict) -> Dict:
        """Calculate growth for trees in transition zone (2.0 <= DBH <= 3.0 inches)."""
        # Get growth estimates from both models
        small_growth = self._small_tree_growth(tree, conditions)
        large_growth = self._large_tree_growth(tree, conditions)
        
        # Calculate weight based on DBH
        weight = calculate_growth_weight(
            dbh=tree.dbh,
            xmin=self.coefficients['Xmin'],
            xmax=self.coefficients['Xmax']
        )
        
        # Blend the estimates
        return {
            'height_growth': blend_growth_estimates(
                weight, small_growth['height_growth'], large_growth['height_growth']
            ),
            'dbh_growth': blend_growth_estimates(
                weight, small_growth['dbh_growth'], large_growth['dbh_growth']
            ),
            'crown_ratio_change': blend_growth_estimates(
                weight, small_growth['crown_ratio_change'], large_growth['crown_ratio_change']
            )
        }
    
    def _competition_modifier(self, tree: 'Tree', conditions: Dict) -> float:
        """Calculate competition modifier (0-1) based on stand conditions."""
        ccf = conditions['crown_competition_factor']
        relative_height = conditions['relative_height']
        
        # Basic modifier based on CCF and relative height
        modifier = 1.0 - (0.0001 * ccf) * (1.0 - relative_height)
        return max(0.05, min(1.0, modifier))
    
    def _estimate_crown_ratio_change(self, tree: 'Tree', conditions: Dict) -> float:
        """Estimate change in crown ratio based on growth and competition."""
        ccf = conditions['crown_competition_factor']
        relative_height = conditions['relative_height']
        
        # Basic crown ratio change model
        # Decrease with competition, increase with relative height
        change = 0.01 * (relative_height - 0.5) - 0.0001 * ccf
        
        # Ensure crown ratio stays within bounds
        new_cr = tree.crown_ratio + change
        if new_cr < 0.2:
            change = 0.2 - tree.crown_ratio
        elif new_cr > 0.9:
            change = 0.9 - tree.crown_ratio
            
        return change
    
    def _estimate_dbh_from_height(self, height: float) -> float:
        """Estimate DBH from height using reverse Curtis-Arney relationship."""
        if height <= 4.51:
            return self.coefficients['Dbw']
            
        # Simplified inverse of Curtis-Arney for small trees
        dbh = (height - 4.51) * (3.0 - self.coefficients['Dbw']) / (
            curtis_arney_height(3.0, self.species, self.coefficients) - 4.51
        ) + self.coefficients['Dbw']
        
        return max(self.coefficients['Dbw'], min(3.0, dbh)) 
"""
Stand class managing a collection of trees and stand-level dynamics.
Handles competition, mortality, and stand metrics.
"""
import math
import random
import yaml
import numpy as np
from pathlib import Path
from typing import List, Optional
from .tree import Tree
from .config_loader import load_stand_config
from .validation import ParameterValidator
from .logging_config import get_logger, log_growth_summary

class Stand:
    def __init__(self, trees: Optional[List[Tree]] = None, site_index: float = 70, species: str = 'LP'):
        """Initialize a stand with a list of trees.
        
        Args:
            trees: List of Tree objects. If None, creates an empty stand.
            site_index: Site index (base age 25) in feet
            species: Default species code for stand parameters
            
        Note:
            Empty stands can be initialized but should have trees added before
            running simulations.
        """
        self.trees = trees if trees is not None else []
        
        # Validate site index
        validated_params = ParameterValidator.validate_stand_parameters(
            trees_per_acre=len(self.trees) if self.trees else 1,
            site_index=site_index,
            species_code=species
        )
        self.site_index = validated_params['site_index']
        
        self.age = 0
        self.species = species
        
        # Set up logging
        self.logger = get_logger(__name__)
        
        # Load configuration using new config system
        self.params = load_stand_config(species)
        
        # Load growth model parameters
        try:
            from .config_loader import get_config_loader
            loader = get_config_loader()
            growth_params_file = loader.cfg_dir / 'growth_model_parameters.yaml'
            self.growth_params = loader._load_config_file(growth_params_file)
        except Exception:
            # Fallback defaults
            self.growth_params = {
                'mortality': {
                    'early_mortality': {'age_threshold': 5, 'base_rate': 0.25},
                    'background_mortality': {'base_rate': 0.05, 'competition_threshold': 0.55, 'competition_multiplier': 0.1}
                },
                'initial_tree': {'dbh': {'mean': 0.5, 'std_dev': 0.1, 'minimum': 0.1}}
            }
    
    @classmethod
    def initialize_planted(cls, trees_per_acre: int, site_index: float = 70, species: str = 'LP'):
        """Create a new planted stand.
        
        Args:
            trees_per_acre: Number of trees per acre to plant
            site_index: Site index (base age 25) in feet
            species: Species code for the plantation
            
        Returns:
            Stand: New stand instance
        """
        # Validate parameters
        validated_params = ParameterValidator.validate_stand_parameters(
            trees_per_acre=trees_per_acre,
            site_index=site_index,
            species_code=species
        )
        
        trees_per_acre = validated_params['trees_per_acre']
        site_index = validated_params['site_index']
        
        # Create stand instance to access config
        temp_stand = cls([], site_index, species)
        initial_params = temp_stand.growth_params.get('initial_tree', {})
        
        dbh_params = initial_params.get('dbh', {})
        dbh_mean = dbh_params.get('mean', 0.5)
        dbh_sd = dbh_params.get('std_dev', 0.1)
        dbh_min = dbh_params.get('minimum', 0.1)
        
        initial_height = initial_params.get('height', {}).get('planted', 1.0)
        
        # Create trees with random variation
        trees = [
            Tree(
                dbh=max(dbh_min, dbh_mean + random.gauss(0, dbh_sd)),
                height=initial_height,
                species=species,
                age=0
            )
            for _ in range(trees_per_acre)
        ]
        
        return cls(trees, site_index, species)
    
    def grow(self, years=5):
        """Grow stand for specified number of years.
        
        Args:
            years: Number of years to grow (default 5 years to match FVS)
        """
        # Ensure years is a multiple of 5
        if years % 5 != 0:
            years = 5 * math.ceil(years / 5)
            
        for period in range(0, years, 5):  # Step in 5-year increments
            # Store initial metrics
            initial_count = len(self.trees)
            initial_metrics = self.get_metrics() if self.trees else None
            
            # Calculate competition metrics
            competition_metrics = self._calculate_competition_metrics()
            
            # Grow each tree
            for tree, metrics in zip(self.trees, competition_metrics):
                tree.grow(
                    site_index=self.site_index,
                    competition_factor=metrics['competition_factor']
                )
            
            # Apply mortality
            mortality_count = self._apply_mortality()
            
            self.age += 5
            
            # Log growth summary
            if initial_metrics and self.trees:
                final_metrics = self.get_metrics()
                dbh_growth = final_metrics['mean_dbh'] - initial_metrics['mean_dbh']
                height_growth = final_metrics['mean_height'] - initial_metrics['mean_height']
                log_growth_summary(self.logger, period // 5 + 1, 
                                 dbh_growth, height_growth, mortality_count)
    
    def _calculate_crown_width(self, tree):
        """Calculate maximum crown width for a tree.
        
        Uses equation from FVS Southern Variant for loblolly pine:
        MCW = a1 + (a2 * DBH) + (a3 * DBH^2)
        """
        p = self.params['crown']
        if tree.dbh >= 5.0:
            return p['a1'] + (p['a2'] * tree.dbh) + (p['a3'] * tree.dbh**2)
        else:
            # Linear interpolation for small trees
            mcw_at_5 = p['a1'] + (p['a2'] * 5.0) + (p['a3'] * 5.0**2)
            return mcw_at_5 * (tree.dbh / 5.0)
    
    def _calculate_ccf(self):
        """Calculate Crown Competition Factor.
        
        CCF is the sum of maximum crown areas divided by stand area,
        expressed as a percentage.
        """
        total_crown_area = 0
        for tree in self.trees:
            crown_width = self._calculate_crown_width(tree)
            crown_area = math.pi * (crown_width / 2)**2
            total_crown_area += crown_area
        
        # Convert to percentage (1 acre = 43560 sq ft)
        return (total_crown_area / 43560) * 100
    
    def _calculate_competition_metrics(self):
        """Calculate competition metrics for each tree.
        
        Returns:
            list: Dictionaries containing competition metrics for each tree
        """
        if len(self.trees) <= 1:
            return [{'competition_factor': 0.0, 'pbal': 0.0}] * len(self.trees)
        
        # Sort trees by DBH for PBAL calculation
        sorted_trees = sorted(self.trees, key=lambda t: t.dbh)
        tree_to_rank = {tree: rank for rank, tree in enumerate(sorted_trees)}
        
        # Calculate stand-level metrics
        stand_ba = sum(math.pi * (tree.dbh / 24)**2 for tree in self.trees)
        ccf = self._calculate_ccf()
        max_sdi = self.params['mortality']['max_sdi']
        
        # Calculate metrics for each tree
        metrics = []
        for tree in self.trees:
            # Calculate PBAL (basal area in larger trees)
            larger_trees = sorted_trees[tree_to_rank[tree]+1:]
            pbal = sum(math.pi * (t.dbh / 24)**2 for t in larger_trees)
            
            # Calculate relative position in diameter distribution
            rank = tree_to_rank[tree] / len(self.trees)
            
            # Calculate competition factor combining density and size effects
            density_factor = min(0.8, stand_ba / 150)  # Basic density effect
            ccf_factor = min(0.8, ccf / 200)  # CCF effect
            size_factor = min(1.0, tree.dbh / (sum(t.dbh for t in self.trees) / len(self.trees)))
            
            # Combine factors with weights
            competition_factor = min(0.95, 0.4 * density_factor + 0.4 * ccf_factor + 0.2 * size_factor)
            
            metrics.append({
                'competition_factor': competition_factor,
                'pbal': pbal,
                'rank': rank,
                'relsdi': (stand_ba / max_sdi) * 10  # Relative SDI (0-12 scale)
            })
        
        return metrics
    
    def _apply_mortality(self):
        """Apply mortality based on stand density and tree characteristics.
        
        Returns:
            int: Number of trees that died
        """
        if len(self.trees) <= 1:
            return 0
        
        initial_count = len(self.trees)
        
        # Calculate competition metrics
        basal_area = sum(math.pi * (tree.dbh / 24)**2 for tree in self.trees)
        max_sdi = self.params['mortality']['max_sdi']
        relative_density = basal_area / max_sdi
        
        # Get mortality parameters from config
        mortality_params = self.growth_params.get('mortality', {})
        early_params = mortality_params.get('early_mortality', {})
        background_params = mortality_params.get('background_mortality', {})
        
        # Base mortality rate with competition effect
        age_threshold = early_params.get('age_threshold', 5)
        if self.age <= age_threshold:
            mortality_rate = early_params.get('base_rate', 0.25)
        else:
            # Background mortality rate
            base_rate = background_params.get('base_rate', 0.05)
            comp_threshold = background_params.get('competition_threshold', 0.55)
            comp_multiplier = background_params.get('competition_multiplier', 0.1)
            
            competition_mortality = max(0.0, comp_multiplier * (relative_density - comp_threshold))
            mortality_rate = base_rate + competition_mortality
        
        # Calculate mean DBH
        mean_dbh = sum(tree.dbh for tree in self.trees) / len(self.trees)
        
        # Apply mortality
        survivors = []
        for tree in self.trees:
            # Smaller trees have higher mortality
            size_multiplier = mortality_params.get('size_effect', {}).get('multiplier', 0.2)
            size_effect = 1.0 + max(0.0, size_multiplier * (1.0 - tree.dbh / mean_dbh))
            
            # Check survival (adjusted for 5-year period)
            if random.random() > mortality_rate * size_effect:
                survivors.append(tree)
        
        self.trees = survivors
        mortality_count = initial_count - len(survivors)
        return mortality_count
    
    def get_metrics(self):
        """Calculate stand-level metrics."""
        if not self.trees:
            return {
                'age': self.age,
                'tpa': 0,
                'mean_dbh': 0,
                'mean_height': 0,
                'basal_area': 0,
                'volume': 0,
                'ccf': 0
            }
        
        n_trees = len(self.trees)
        metrics = {
            'age': self.age,
            'tpa': n_trees,
            'mean_dbh': sum(tree.dbh for tree in self.trees) / n_trees,
            'mean_height': sum(tree.height for tree in self.trees) / n_trees,
            'basal_area': sum(math.pi * (tree.dbh / 24)**2 for tree in self.trees),
            'volume': sum(tree.get_volume() for tree in self.trees),
            'ccf': self._calculate_ccf()
        }
        
        return metrics 
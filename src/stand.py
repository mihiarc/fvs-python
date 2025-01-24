"""
Stand class managing a collection of trees and stand-level dynamics.
Handles competition, mortality, and stand metrics.
"""
import math
import random
import yaml
import numpy as np
from pathlib import Path
from .tree import Tree

class Stand:
    def __init__(self, trees, site_index=70):
        """Initialize a stand with a list of trees.
        
        Args:
            trees: List of Tree objects
            site_index: Site index (base age 25) in feet
            
        Raises:
            ValueError: If trees list is empty
        """
        if not trees:
            raise ValueError("Stand must have at least one tree")
        self.trees = trees
        self.site_index = site_index
        self.age = 0
        
        # Load configuration
        config_path = Path(__file__).parent.parent / 'config' / 'loblolly_params.yaml'
        with open(config_path, 'r') as f:
            self.params = yaml.safe_load(f)
    
    @classmethod
    def initialize_planted(cls, trees_per_acre, site_index=70):
        """Create a new planted stand.
        
        Args:
            trees_per_acre: Number of trees per acre to plant
            site_index: Site index (base age 25) in feet
            
        Returns:
            Stand: New stand instance
        """
        if trees_per_acre <= 0:
            raise ValueError(f"Trees per acre must be positive, got {trees_per_acre}")
        
        # Create trees with small random variation
        trees = [
            Tree(
                dbh=max(0.1, 0.5 + random.gauss(0, 0.05)),  # ~0.5" DBH
                height=1.0  # Fixed initial height
            )
            for _ in range(int(trees_per_acre))
        ]
        
        return cls(trees, site_index)
    
    def grow(self, years=5):
        """Grow stand for specified number of years.
        
        Args:
            years: Number of years to grow (default 5 years to match FVS)
        """
        # Ensure years is a multiple of 5
        if years % 5 != 0:
            years = 5 * math.ceil(years / 5)
            
        for _ in range(0, years, 5):  # Step in 5-year increments
            # Calculate competition metrics
            competition_metrics = self._calculate_competition_metrics()
            
            # Grow each tree
            for tree, metrics in zip(self.trees, competition_metrics):
                tree.grow(
                    site_index=self.site_index,
                    competition_factor=metrics['competition_factor']
                )
            
            # Apply mortality
            self._apply_mortality()
            
            self.age += 5
    
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
        """Apply mortality based on stand density and tree characteristics."""
        if len(self.trees) <= 1:
            return
        
        # Calculate competition metrics
        basal_area = sum(math.pi * (tree.dbh / 24)**2 for tree in self.trees)
        max_sdi = self.params['mortality']['max_sdi']
        relative_density = basal_area / max_sdi
        
        # Base mortality rate with competition effect
        if self.age <= 5:
            mortality_rate = 0.25  # 25% mortality in first 5 years
        else:
            # Increased mortality rate for 5-year steps
            base_rate = 0.05  # 5% per 5 years
            competition_mortality = max(0.0, 0.1 * (relative_density - 0.55))
            mortality_rate = base_rate + competition_mortality
        
        # Calculate mean DBH
        mean_dbh = sum(tree.dbh for tree in self.trees) / len(self.trees)
        
        # Apply mortality
        survivors = []
        for tree in self.trees:
            # Smaller trees have higher mortality
            size_effect = 1.0 + max(0.0, 0.2 * (1.0 - tree.dbh / mean_dbh))
            
            # Check survival (adjusted for 5-year period)
            if random.random() > mortality_rate * size_effect:
                survivors.append(tree)
        
        self.trees = survivors
    
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
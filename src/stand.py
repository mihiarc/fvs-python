"""
Stand class managing a collection of trees and stand-level dynamics.
Handles competition, mortality, and stand metrics.
"""
import math
import random
import yaml
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
    
    def grow(self, years=1):
        """Grow stand for specified number of years.
        
        Args:
            years: Number of years to grow
        """
        for _ in range(years):
            # Calculate competition for each tree
            competition_factors = self._calculate_competition_factors()
            
            # Grow each tree
            for tree, cf in zip(self.trees, competition_factors):
                tree.grow(site_index=self.site_index, competition_factor=cf)
            
            # Apply mortality
            self._apply_mortality()
            
            self.age += 1
    
    def _calculate_competition_factors(self):
        """Calculate competition factor for each tree.
        
        Competition is based on:
        1. Stand density relative to maximum (higher density = more competition)
        2. Tree size relative to mean (larger trees experience more competition)
        
        Returns:
            list: Competition factors (0-1) for each tree
        """
        if len(self.trees) <= 1:
            return [0.0] * len(self.trees)
        
        # Basic density effect (0-1)
        stand_ba = sum(math.pi * (tree.dbh / 24)**2 for tree in self.trees)
        density_factor = min(0.8, stand_ba / 150)  # 150 sq ft/acre is typical maximum
        
        # Calculate mean DBH
        mean_dbh = sum(tree.dbh for tree in self.trees) / len(self.trees)
        
        competition_factors = []
        for tree in self.trees:
            # Size effect (larger trees get more competition)
            size_factor = min(1.0, tree.dbh / mean_dbh)
            
            # Total competition increases with both density and size
            cf = density_factor * size_factor
            
            # Ensure reasonable bounds
            competition_factors.append(min(0.8, max(0.1, cf)))
        
        return competition_factors
    
    def _apply_mortality(self):
        """Apply mortality based on stand age and tree size.
        
        Mortality is higher:
        1. During establishment (first 5 years)
        2. For smaller trees (below mean DBH)
        3. Under high competition
        """
        if len(self.trees) <= 1:
            return
        
        # Calculate competition metrics
        basal_area = sum(math.pi * (tree.dbh / 24)**2 for tree in self.trees)
        relative_density = basal_area / 400  # Using max SDI of 400 from params
        
        # Base mortality rate with competition effect
        if self.age <= 5:
            mortality_rate = 0.08  # 8% early mortality
        else:
            mortality_rate = 0.01 + max(0.0, 0.02 * (relative_density - 0.6))  # 1% base + competition
        
        # Calculate mean DBH
        mean_dbh = sum(tree.dbh for tree in self.trees) / len(self.trees)
        
        # Apply mortality
        survivors = []
        for tree in self.trees:
            # Smaller trees have higher mortality
            size_effect = 1.0 + max(0.0, 0.15 * (1.0 - tree.dbh / mean_dbh))
            
            # Check survival
            if random.random() > mortality_rate * size_effect:
                survivors.append(tree)
        
        self.trees = survivors
    
    def get_metrics(self):
        """Calculate stand-level metrics.
        
        Returns:
            dict: Stand metrics including age, TPA, mean DBH, etc.
        """
        if not self.trees:
            return {
                'age': 0,
                'tpa': 0,
                'mean_dbh': 0,
                'mean_height': 0,
                'basal_area': 0,
                'volume': 0
            }
        
        n_trees = len(self.trees)
        metrics = {
            'age': self.age,
            'tpa': n_trees,
            'mean_dbh': sum(tree.dbh for tree in self.trees) / n_trees,
            'mean_height': sum(tree.height for tree in self.trees) / n_trees,
            'basal_area': sum(math.pi * (tree.dbh / 24)**2 for tree in self.trees),
            'volume': sum(tree.get_volume() for tree in self.trees)
        }
        
        return metrics 
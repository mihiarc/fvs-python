#!/usr/bin/env python3
"""
Corrected test script for loblolly pine single tree growth.
Implements proper Chapman-Richards height growth calculation.
"""

import sys
import os
import math

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fvs_python.tree import Tree

class CorrectedTree(Tree):
    """Tree class with corrected small tree growth implementation."""
    
    def _grow_small_tree(self, site_index, competition_factor, time_step=5):
        """Corrected small tree height growth using Chapman-Richards function.
        
        The Chapman-Richards function predicts total height at a given age.
        Height growth is calculated as the difference between predicted heights
        at current age and future age.
        """
        # Chapman-Richards parameters for loblolly pine
        p = {
            'c1': 1.1421,
            'c2': 1.0042,
            'c3': -0.0374,
            'c4': 0.7632,
            'c5': 0.0358
        }
        
        def chapman_richards_height(age, si):
            """Calculate predicted height at given age using Chapman-Richards."""
            return p['c1'] * (si ** p['c2']) * (1.0 - math.exp(p['c3'] * age)) ** (p['c4'] * (si ** p['c5']))
        
        # Calculate current predicted height
        current_predicted_height = chapman_richards_height(self.age, site_index)
        
        # Calculate predicted height after time_step years
        future_predicted_height = chapman_richards_height(self.age + time_step, site_index)
        
        # Height growth is the difference
        height_growth = future_predicted_height - current_predicted_height
        
        # Apply competition modifier (simple approach)
        competition_modifier = 1.0 - 0.3 * competition_factor
        actual_growth = height_growth * competition_modifier
        
        # Update height
        self.height += actual_growth
        
        # Update DBH using height-diameter relationship
        self._update_dbh_from_height()
    
    def _grow_large_tree(self, site_index, competition_factor, ba, pbal, slope, aspect, time_step=5):
        """Corrected large tree diameter growth model."""
        # Get large tree diameter growth parameters from config
        p = self.species_params['diameter_growth']['coefficients']
        
        # Check for very low crown ratio that might cause math errors
        if self.crown_ratio <= 0.01:
            self.crown_ratio = 0.05  # Set minimum crown ratio
        
        # Forest type and ecological unit effects (not currently implemented)
        fortype_effect = 0.0
        ecounit_effect = 0.0
        
        # Planting effect from config
        plant_effect = self.species_params.get('plant', {}).get('value', 0.245669)
        
        try:
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
            
            # Convert to diameter growth and update DBH
            # Scale growth based on time_step (model is calibrated for 5-year growth)
            dds = math.exp(ln_dds) * (time_step / 5.0)
            
            # Ensure positive growth
            if dds > 0:
                self.dbh = math.sqrt(self.dbh**2 + dds)
            
            # Update height using height-diameter relationship
            self._update_height_from_dbh()
            
        except (ValueError, OverflowError) as e:
            # If calculation fails, apply minimal growth
            print(f"Warning: Growth calculation failed for tree (DBH={self.dbh:.1f}, CR={self.crown_ratio:.3f}): {e}")
            self.dbh += 0.1 * (time_step / 5.0)  # Minimal growth
            self._update_height_from_dbh()

def test_corrected_growth():
    """Test the corrected growth implementation."""
    
    print("=== Corrected Loblolly Pine Tree Growth Test ===\n")
    
    # Create a young loblolly pine tree
    tree = CorrectedTree(
        dbh=2.0,           # 2 inches diameter at breast height
        height=12.0,       # 12 feet tall
        species="LP",      # Loblolly Pine
        age=10,            # 10 years old
        crown_ratio=0.8    # 80% live crown
    )
    
    print("Initial Tree Characteristics:")
    print(f"  Species: {tree.species} (Loblolly Pine)")
    print(f"  Age: {tree.age} years")
    print(f"  DBH: {tree.dbh:.1f} inches")
    print(f"  Height: {tree.height:.1f} feet")
    print(f"  Crown Ratio: {tree.crown_ratio:.2f}")
    print(f"  Volume: {tree.get_volume('total_cubic'):.2f} cubic feet")
    
    # Site and stand conditions
    site_index = 70      # Site index (base age 25) - moderate productivity
    ba = 80              # Stand basal area (sq ft/acre)
    pbal = 40            # Plot basal area in larger trees
    competition = 0.3    # Competition factor (0-1)
    
    print(f"\nSite Conditions:")
    print(f"  Site Index: {site_index} feet (base age 25)")
    print(f"  Stand Basal Area: {ba} sq ft/acre")
    print(f"  Competition Factor: {competition}")
    
    print(f"\n{'Age':<5} {'DBH':<6} {'Height':<8} {'Crown':<7} {'Volume':<8} {'Growth Type'}")
    print(f"{'(yr)':<5} {'(in)':<6} {'(ft)':<8} {'Ratio':<7} {'(cu ft)':<8}")
    print("-" * 50)
    
    # Print initial state
    volume = tree.get_volume('total_cubic')
    growth_type = get_growth_model_type(tree.dbh)
    print(f"{tree.age:<5} {tree.dbh:<6.1f} {tree.height:<8.1f} {tree.crown_ratio:<7.2f} {volume:<8.2f} {growth_type}")
    
    # Simulate growth for 40 years (8 periods of 5 years each)
    for period in range(8):
        # Grow the tree for 5 years
        tree.grow(
            site_index=site_index,
            competition_factor=competition,
            rank=0.5,           # Middle of diameter distribution
            relsdi=5.0,         # Relative stand density index
            ba=ba,
            pbal=pbal,
            slope=0.05,         # 5% slope
            aspect=0,           # North-facing
            time_step=5         # 5-year growth period
        )
        
        # Print updated state
        volume = tree.get_volume('total_cubic')
        growth_type = get_growth_model_type(tree.dbh)
        print(f"{tree.age:<5} {tree.dbh:<6.1f} {tree.height:<8.1f} {tree.crown_ratio:<7.2f} {volume:<8.2f} {growth_type}")
    
    print(f"\nFinal Tree Characteristics:")
    print(f"  Age: {tree.age} years")
    print(f"  DBH: {tree.dbh:.1f} inches")
    print(f"  Height: {tree.height:.1f} feet")
    print(f"  Crown Ratio: {tree.crown_ratio:.2f}")
    print(f"  Volume: {tree.get_volume('total_cubic'):.2f} cubic feet")
    
    # Calculate total growth
    initial_dbh = 2.0
    initial_height = 12.0
    dbh_growth = tree.dbh - initial_dbh
    height_growth = tree.height - initial_height
    
    print(f"\nTotal Growth Over 40 Years:")
    print(f"  DBH Growth: +{dbh_growth:.1f} inches")
    print(f"  Height Growth: +{height_growth:.1f} feet")
    print(f"  Average Annual DBH Growth: {dbh_growth/40:.2f} inches/year")
    print(f"  Average Annual Height Growth: {height_growth/40:.1f} feet/year")

def get_growth_model_type(dbh):
    """Determine which growth model is being used based on DBH."""
    xmin, xmax = 1.0, 3.0
    
    if dbh < xmin:
        return "Small tree"
    elif dbh > xmax:
        return "Large tree"
    else:
        weight = (dbh - xmin) / (xmax - xmin)
        return f"Blended ({weight:.1f})"

def test_chapman_richards_directly():
    """Test the Chapman-Richards function directly."""
    
    print("\n\n=== Chapman-Richards Height Growth Test ===\n")
    
    # Parameters for loblolly pine
    p = {
        'c1': 1.1421,
        'c2': 1.0042,
        'c3': -0.0374,
        'c4': 0.7632,
        'c5': 0.0358
    }
    
    def chapman_richards_height(age, si):
        """Calculate predicted height at given age using Chapman-Richards."""
        return p['c1'] * (si ** p['c2']) * (1.0 - math.exp(p['c3'] * age)) ** (p['c4'] * (si ** p['c5']))
    
    site_index = 70
    
    print(f"Chapman-Richards Height Predictions (Site Index {site_index}):")
    print(f"{'Age':<5} {'Height':<8} {'5-yr Growth':<12}")
    print(f"{'(yr)':<5} {'(ft)':<8} {'(ft)':<12}")
    print("-" * 25)
    
    for age in range(5, 51, 5):
        height = chapman_richards_height(age, site_index)
        
        if age >= 10:
            prev_height = chapman_richards_height(age - 5, site_index)
            growth = height - prev_height
        else:
            growth = 0
        
        print(f"{age:<5} {height:<8.1f} {growth:<12.1f}")

def test_different_ages():
    """Test trees starting at different ages."""
    
    print("\n\n=== Different Starting Ages Test ===\n")
    
    ages = [5, 10, 15, 20]
    site_index = 70
    
    print("Comparing trees starting at different ages:")
    print("(All trees grown for 20 years)")
    print()
    
    for start_age in ages:
        # Estimate initial height using Chapman-Richards
        p = {
            'c1': 1.1421,
            'c2': 1.0042,
            'c3': -0.0374,
            'c4': 0.7632,
            'c5': 0.0358
        }
        
        initial_height = p['c1'] * (site_index ** p['c2']) * (1.0 - math.exp(p['c3'] * start_age)) ** (p['c4'] * (site_index ** p['c5']))
        
        # Estimate initial DBH (rough approximation)
        initial_dbh = max(0.5, initial_height / 10)
        
        tree = CorrectedTree(
            dbh=initial_dbh,
            height=initial_height,
            species="LP",
            age=start_age,
            crown_ratio=0.8
        )
        
        # Grow for 20 years
        for _ in range(4):  # 4 periods of 5 years = 20 years
            tree.grow(
                site_index=site_index,
                competition_factor=0.3,
                rank=0.5,
                relsdi=5.0,
                ba=80,
                pbal=40,
                slope=0.05,
                aspect=0,
                time_step=5
            )
        
        print(f"Starting Age {start_age}:")
        print(f"  Initial: DBH={initial_dbh:.1f}\", Height={initial_height:.1f}'")
        print(f"  Final: DBH={tree.dbh:.1f}\", Height={tree.height:.1f}'")
        print(f"  Growth: DBH +{tree.dbh - initial_dbh:.1f}\", Height +{tree.height - initial_height:.1f}'")
        print()

if __name__ == "__main__":
    # Test the corrected growth implementation
    test_corrected_growth()
    
    # Test Chapman-Richards function directly
    test_chapman_richards_directly()
    
    # Test different starting ages
    test_different_ages()
    
    print("=== Corrected Test Complete ===")
    print("This demonstrates the corrected single tree growth mechanics")
    print("for loblolly pine using proper Chapman-Richards height growth.") 
import unittest
import numpy as np
from src.initialize_stand import initialize_stand, get_empirical_dbh_distribution

class TestInitializeFromConditions(unittest.TestCase):
    def test_empirical_distribution(self):
        # Species crosswalk (FIA -> FVS)
        # 131 is Loblolly Pine in FIA, LP in FVS
        fia_to_fvs = {"131": "LP"}
        
        # Set up test conditions with FIA species code
        species_mix = {"131": 1.0}  # Using FIA code 131 (Loblolly Pine)
        trees_per_acre = 100
        
        # Get empirical distribution using FIA code
        dbh_distributions = {
            species: get_empirical_dbh_distribution(species)
            for species in species_mix
        }
        
        # Initialize stand
        stand = initialize_stand(
            {"use_empirical": True},
            trees_per_acre=trees_per_acre,
            species_mix=species_mix,
            initial_dbh_distribution=dbh_distributions
        )
        
        # Convert FIA species codes to FVS codes in the stand
        for tree in stand:
            tree.species = fia_to_fvs[tree.species]
        
        # Verify results
        self.assertEqual(len(stand), trees_per_acre)  # Check total number of trees
        
        # Check species proportions and collect DBH values
        species_counts = {}
        dbh_values = []
        for tree in stand:
            species_counts[tree.species] = species_counts.get(tree.species, 0) + 1
            dbh_values.append(tree.dbh)
            self.assertGreater(tree.dbh, 0)  # All DBH values should be positive
            self.assertEqual(tree.species, "LP")  # All trees should be Loblolly Pine
        
        # Print summary statistics
        print("\nDBH Distribution Summary for Loblolly Pine (LP):")
        print(f"Mean DBH: {np.mean(dbh_values):.2f} inches")
        print(f"Std Dev DBH: {np.std(dbh_values):.2f} inches")
        print(f"Min DBH: {min(dbh_values):.2f} inches")
        print(f"Max DBH: {max(dbh_values):.2f} inches")
        
        # Print histogram-like distribution
        bins = np.linspace(min(dbh_values), max(dbh_values), 10)
        hist, _ = np.histogram(dbh_values, bins=bins)
        print("\nDBH Distribution (count in each bin):")
        for i in range(len(hist)):
            print(f"{bins[i]:.1f}-{bins[i+1]:.1f} inches: {hist[i]} trees")

if __name__ == '__main__':
    unittest.main()
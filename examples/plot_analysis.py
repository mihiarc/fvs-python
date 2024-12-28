"""Example script demonstrating how to use FVS and FIA databases together."""

from pathlib import Path
from src.db_utils import FVSDatabase
from src.fia_utils import FIADatabase

def analyze_plot(plot_id: int, fia_db_path: Path):
    """Analyze trees in a plot using both FIA and FVS data.
    
    Args:
        plot_id: The FIA plot ID to analyze.
        fia_db_path: Path to the FIA database file.
    """
    # Open both database connections
    with FIADatabase(fia_db_path) as fia_db, FVSDatabase('fvs_parameters.db') as fvs_db:
        # Get plot information
        plot_info = fia_db.get_plot_info(plot_id)
        if not plot_info:
            print(f"Plot {plot_id} not found")
            return
            
        print(f"\nAnalyzing Plot {plot_id}")
        print(f"Location: State {plot_info['StateCode']}, County {plot_info['CountyCode']}")
        
        # Get trees in the plot
        trees = fia_db.get_plot_trees(plot_id)
        print(f"\nFound {len(trees)} trees in plot")
        
        # Analyze each tree using FVS parameters
        print("\nTree Analysis:")
        print("-" * 60)
        for _, tree in trees.iterrows():
            species_info = fvs_db.get_species_info(tree['Species'])
            if species_info:
                print(f"\nTree ID: {tree['TreeID']}")
                print(f"Species: {tree['Species']}")
                print(f"DBH: {tree['DBH']:.1f} inches")
                print(f"Height: {tree['Height']:.1f} feet")
                
                # Get ecological coefficients for growth modeling
                eco_coeffs = fvs_db.get_ecological_coefficients(
                    tree['Species'], 
                    plot_info.get('EcologicalUnit', 'default')
                )
                if eco_coeffs:
                    print("Growth Parameters Available")
            else:
                print(f"\nWarning: No FVS parameters found for species {tree['Species']}")

if __name__ == '__main__':
    # Example usage - replace with actual path to your FIA database
    fia_path = Path('data/test_coastal_loblolly.db')
    if not fia_path.exists():
        print(f"Error: FIA database not found at {fia_path}")
    else:
        analyze_plot(12345, fia_path)  # Replace with an actual plot ID from your database 
#!/usr/bin/env python3
"""
Crown Width Calculation Demo for FVS-Python

This demo demonstrates the crown width calculation functionality for the FVS Southern variant,
implementing equations 4.4.1 through 4.4.5 as described in the documentation.

The SN variant calculates maximum crown width for individual trees based on tree and stand attributes.
Crown width is used to calculate:
- Percent Canopy Cover (PCC) using forest-grown crown width (FCW)
- Crown Competition Factor (CCF) using open-grown crown width (OCW)

Equations implemented:
- 4.4.1: Bechtold (2003) - FCW = a1 + (a2 * DBH) + (a3 * DBH^2) + (a4 * CR) + (a5 * HI)
- 4.4.2: Bragg (2001) - FCW = a1 + (a2 * DBH^a3)
- 4.4.3: Ek (1974) - OCW = a1 + (a2 * DBH^a3)
- 4.4.4: Krajicek et al. (1961) - OCW = a1 + (a2 * DBH)
- 4.4.5: Smith et al. (1992) - OCW = a1 + (a2 * DBH * 2.54) + (a3 * (DBH * 2.54)^2) * 3.28084

Hopkins Index: HI = (ELEVATION - 887) / 100) * 1.0 + (LATITUDE – 39.54) * 4.0 + (-82.52 - LONGITUDE) * 1.25
"""

from src.fvs_python.crown_width import (
    create_crown_width_model,
    calculate_hopkins_index,
    compare_crown_width_models
)


def demonstrate_basic_crown_width():
    """Demonstrate basic crown width calculations for different species."""
    print("=" * 80)
    print("BASIC CROWN WIDTH CALCULATIONS")
    print("=" * 80)
    
    # Test cases from documentation
    test_cases = [
        {"species": "LP", "dbh": 10.0, "cr": 50.0, "description": "Loblolly Pine (LP) - Example from documentation"},
        {"species": "SA", "dbh": 15.0, "cr": 60.0, "description": "Slash Pine (SA) - Uses Bechtold equation with all terms"},
        {"species": "SP", "dbh": 8.0, "cr": 45.0, "description": "Shortleaf Pine (SP) - Common southern species"},
        {"species": "WO", "dbh": 12.0, "cr": 55.0, "description": "White Oak (WO) - Hardwood species"},
        {"species": "RM", "dbh": 20.0, "cr": 40.0, "description": "Red Maple (RM) - Another hardwood"},
    ]
    
    # Geographic location for Hopkins Index (example: North Carolina)
    elevation = 1000.0  # feet
    latitude = 35.5     # degrees
    longitude = -80.0   # degrees
    hopkins_index = calculate_hopkins_index(elevation, latitude, longitude)
    
    print(f"Geographic Location: Elevation={elevation} ft, Latitude={latitude}°, Longitude={longitude}°")
    print(f"Hopkins Index: {hopkins_index:.4f}")
    print()
    
    for case in test_cases:
        species = case["species"]
        dbh = case["dbh"]
        crown_ratio = case["cr"]
        
        print(f"{case['description']}")
        print(f"  DBH: {dbh} inches, Crown Ratio: {crown_ratio}%")
        
        model = create_crown_width_model(species)
        
        # Calculate crown widths
        fcw = model.calculate_forest_grown_crown_width(dbh, crown_ratio, hopkins_index)
        ocw = model.calculate_open_grown_crown_width(dbh)
        ccf_contrib = model.calculate_ccf_contribution(dbh)
        
        # Get equation info
        forest_eq_info = model.get_equation_info("forest")
        open_eq_info = model.get_equation_info("open")
        
        print(f"  Forest-grown Crown Width (FCW): {fcw:.2f} feet")
        print(f"    Equation: {forest_eq_info['equation_number']} - {forest_eq_info['equation_info']['name']}")
        print(f"  Open-grown Crown Width (OCW): {ocw:.2f} feet")
        print(f"    Equation: {open_eq_info['equation_number']} - {open_eq_info['equation_info']['name']}")
        print(f"  CCF Contribution: {ccf_contrib:.4f}")
        print()


def demonstrate_hopkins_index_effect():
    """Demonstrate how Hopkins Index affects crown width calculations."""
    print("=" * 80)
    print("HOPKINS INDEX GEOGRAPHIC EFFECTS")
    print("=" * 80)
    
    # Test different geographic locations
    locations = [
        {"name": "North Carolina Mountains", "elevation": 3000, "latitude": 35.5, "longitude": -82.5},
        {"name": "Georgia Piedmont", "elevation": 800, "latitude": 33.5, "longitude": -84.0},
        {"name": "Florida Coastal Plain", "elevation": 50, "latitude": 29.0, "longitude": -82.0},
        {"name": "Texas East", "elevation": 200, "latitude": 31.0, "longitude": -94.0},
    ]
    
    species = "LP"  # Loblolly Pine
    dbh = 12.0
    crown_ratio = 50.0
    
    print(f"Species: {species}, DBH: {dbh} inches, Crown Ratio: {crown_ratio}%")
    print()
    
    model = create_crown_width_model(species)
    
    for location in locations:
        hi = calculate_hopkins_index(location["elevation"], location["latitude"], location["longitude"])
        fcw = model.calculate_forest_grown_crown_width(dbh, crown_ratio, hi)
        
        print(f"{location['name']}:")
        print(f"  Elevation: {location['elevation']} ft, Lat: {location['latitude']}°, Lon: {location['longitude']}°")
        print(f"  Hopkins Index: {hi:.4f}")
        print(f"  Forest Crown Width: {fcw:.2f} feet")
        print()


def demonstrate_size_effects():
    """Demonstrate how tree size affects crown width calculations."""
    print("=" * 80)
    print("TREE SIZE EFFECTS ON CROWN WIDTH")
    print("=" * 80)
    
    species = "SA"  # Slash Pine - uses full Bechtold equation
    crown_ratio = 50.0
    hopkins_index = 0.0
    
    # Range of DBH values
    dbh_values = [2.0, 5.0, 8.0, 12.0, 16.0, 20.0, 25.0, 30.0]
    
    print(f"Species: {species} (Slash Pine)")
    print(f"Crown Ratio: {crown_ratio}%, Hopkins Index: {hopkins_index}")
    print()
    print("DBH (in)  FCW (ft)  OCW (ft)  CCF Contrib  Notes")
    print("-" * 60)
    
    model = create_crown_width_model(species)
    
    for dbh in dbh_values:
        fcw = model.calculate_forest_grown_crown_width(dbh, crown_ratio, hopkins_index)
        ocw = model.calculate_open_grown_crown_width(dbh)
        ccf_contrib = model.calculate_ccf_contribution(dbh)
        
        notes = ""
        if dbh < 5.0:
            notes = "Small tree scaling applied"
        elif dbh >= 30.0:
            notes = "At DBH bound limit"
        
        print(f"{dbh:6.1f}   {fcw:6.2f}   {ocw:6.2f}     {ccf_contrib:6.4f}    {notes}")


def demonstrate_crown_ratio_effects():
    """Demonstrate how crown ratio affects forest-grown crown width."""
    print("=" * 80)
    print("CROWN RATIO EFFECTS ON FOREST-GROWN CROWN WIDTH")
    print("=" * 80)
    
    species = "LP"  # Loblolly Pine
    dbh = 15.0
    hopkins_index = 0.0
    
    # Range of crown ratio values
    crown_ratios = [20, 30, 40, 50, 60, 70, 80, 90]
    
    print(f"Species: {species} (Loblolly Pine)")
    print(f"DBH: {dbh} inches, Hopkins Index: {hopkins_index}")
    print()
    print("Crown Ratio (%)  FCW (ft)  Difference from 50%")
    print("-" * 45)
    
    model = create_crown_width_model(species)
    baseline_fcw = model.calculate_forest_grown_crown_width(dbh, 50.0, hopkins_index)
    
    for cr in crown_ratios:
        fcw = model.calculate_forest_grown_crown_width(dbh, cr, hopkins_index)
        diff = fcw - baseline_fcw
        
        print(f"{cr:12d}     {fcw:6.2f}     {diff:+6.2f}")


def demonstrate_species_comparison():
    """Compare crown width calculations across different species."""
    print("=" * 80)
    print("SPECIES COMPARISON")
    print("=" * 80)
    
    species_list = ["LP", "SA", "SP", "WO", "RM", "CA", "BY", "HM"]
    dbh = 12.0
    crown_ratio = 50.0
    hopkins_index = 0.0
    
    print(f"DBH: {dbh} inches, Crown Ratio: {crown_ratio}%, Hopkins Index: {hopkins_index}")
    print()
    print("Species  FCW (ft)  OCW (ft)  Forest Eq#  Open Eq#   Description")
    print("-" * 75)
    
    for species in species_list:
        try:
            model = create_crown_width_model(species)
            fcw = model.calculate_forest_grown_crown_width(dbh, crown_ratio, hopkins_index)
            ocw = model.calculate_open_grown_crown_width(dbh)
            
            forest_eq = model.forest_grown.get('equation_number', 'N/A')
            open_eq = model.open_grown.get('equation_number', 'N/A')
            
            # Species descriptions
            descriptions = {
                "LP": "Loblolly Pine",
                "SA": "Slash Pine", 
                "SP": "Shortleaf Pine",
                "WO": "White Oak",
                "RM": "Red Maple",
                "CA": "Catalpa",
                "BY": "Bald Cypress",
                "HM": "Eastern Hemlock"
            }
            
            desc = descriptions.get(species, "Unknown")
            
            print(f"{species:7s}  {fcw:6.2f}   {ocw:6.2f}    {forest_eq:8s}  {open_eq:8s}  {desc}")
            
        except Exception as e:
            print(f"{species:7s}  ERROR: {str(e)}")


def demonstrate_ccf_calculation():
    """Demonstrate Crown Competition Factor calculation."""
    print("=" * 80)
    print("CROWN COMPETITION FACTOR (CCF) CALCULATION")
    print("=" * 80)
    
    print("CCF is calculated using open-grown crown width:")
    print("CCF = 0.001803 * OCW^2 (for DBH > 0.1)")
    print("CCF = 0.001 (for DBH <= 0.1)")
    print()
    
    # Example stand with multiple trees
    trees = [
        {"species": "LP", "dbh": 8.5, "count": 15},
        {"species": "LP", "dbh": 12.3, "count": 8},
        {"species": "SA", "dbh": 10.1, "count": 5},
        {"species": "WO", "dbh": 6.2, "count": 12},
        {"species": "RM", "dbh": 4.8, "count": 20},
    ]
    
    print("Example Stand Composition:")
    print("Species  DBH (in)  Count  OCW (ft)  CCF/tree  Total CCF")
    print("-" * 60)
    
    total_ccf = 0.0
    
    for tree in trees:
        model = create_crown_width_model(tree["species"])
        ocw = model.calculate_open_grown_crown_width(tree["dbh"])
        ccf_per_tree = model.calculate_ccf_contribution(tree["dbh"])
        tree_total_ccf = ccf_per_tree * tree["count"]
        total_ccf += tree_total_ccf
        
        print(f"{tree['species']:7s}  {tree['dbh']:6.1f}   {tree['count']:4d}   {ocw:6.2f}    {ccf_per_tree:6.4f}    {tree_total_ccf:7.2f}")
    
    print("-" * 60)
    print(f"Stand Total CCF: {total_ccf:.2f}")


def main():
    """Run all crown width demonstrations."""
    print("FVS-Python Crown Width Calculation Demo")
    print("Southern Variant (SN) - Equations 4.4.1 through 4.4.5")
    print()
    
    demonstrate_basic_crown_width()
    demonstrate_hopkins_index_effect()
    demonstrate_size_effects()
    demonstrate_crown_ratio_effects()
    demonstrate_species_comparison()
    demonstrate_ccf_calculation()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("The crown width module successfully implements:")
    print("• Forest-grown crown width (FCW) for PCC calculations")
    print("• Open-grown crown width (OCW) for CCF calculations")
    print("• Hopkins Index geographic adjustments")
    print("• Species-specific equation assignments")
    print("• Small tree scaling (DBH < 5.0 for FCW, DBH < 3.0 for OCW)")
    print("• Crown ratio and geographic effects")
    print("• Bounds checking and validation")
    print()
    print("All equations from FVS Southern variant documentation are implemented:")
    print("• 4.4.1: Bechtold (2003) - Full equation with CR and HI terms")
    print("• 4.4.2: Bragg (2001) - Power function")
    print("• 4.4.3: Ek (1974) - Open-grown power function")
    print("• 4.4.4: Krajicek et al. (1961) - Linear open-grown")
    print("• 4.4.5: Smith et al. (1992) - Metric conversion equation")


if __name__ == "__main__":
    main() 
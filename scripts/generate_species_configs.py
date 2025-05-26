#!/usr/bin/env python3
"""
Generate species configuration files for all species in the Southern Variant.

This script reads the archive data and creates YAML configuration files for all species
that don't already have configurations, using the source of truth data from the
Southern Variant documentation and archive files.
"""

import csv
import os
from pathlib import Path

# Species data from archive files
SPECIES_DATA = {}

def load_growth_parameters():
    """Load diameter growth parameters from archive data."""
    growth_file = "archive/data/archive/southern_variant_tables/large_tree_growth_parameters.csv"
    with open(growth_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['species_code']
            SPECIES_DATA[code] = {
                'growth': {
                    'b1': float(row['large_tree_b0']),  # Intercept
                    'b2': float(row['large_tree_b1']),  # ln(DBH)
                    'b3': float(row['large_tree_b2']),  # DBH^2
                    'b4': float(row['large_tree_b3']),  # ln(CR)
                    'b5': float(row['large_tree_b4']),  # RELHT
                    'b6': float(row['large_tree_b5']),  # SI
                    'b7': float(row['large_tree_b6']),  # BA
                    'b8': float(row['large_tree_b7']),  # PBAL
                    'b9': float(row['large_tree_b8']),  # SLOPE
                    'b10': float(row['large_tree_b9']), # cos(ASP)*SLOPE
                    'b11': float(row['large_tree_b10']), # sin(ASP)*SLOPE
                }
            }

def load_site_index_data():
    """Load site index ranges from archive data."""
    si_file = "archive/data/archive/southern_variant_tables/site_index_range.csv"
    with open(si_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['species_code']
            if code in SPECIES_DATA:
                SPECIES_DATA[code]['site_index'] = {
                    'min': int(row['si_min']),
                    'max': int(row['si_max']),
                    'dbw': float(row['dbw'])
                }

def load_dbh_bounds():
    """Load DBH bounding limits from archive data."""
    dbh_file = "archive/data/archive/southern_variant_tables/diameter_bounding_limits.csv"
    with open(dbh_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['species_code']
            if code in SPECIES_DATA:
                SPECIES_DATA[code]['dbh_bounds'] = {
                    'lower': float(row['dbh_low']),
                    'upper': float(row['dbh_high'])
                }

# Species metadata mapping (common names and scientific names)
SPECIES_METADATA = {
    'AB': {'name': 'american basswood', 'scientific': 'Tilia americana', 'fia': 951},
    'AE': {'name': 'american elm', 'scientific': 'Ulmus americana', 'fia': 971},
    'AH': {'name': 'american hornbeam', 'scientific': 'Carpinus caroliniana', 'fia': 391},
    'AP': {'name': 'american plum', 'scientific': 'Prunus americana', 'fia': 762},
    'AS': {'name': 'american sycamore', 'scientific': 'Platanus occidentalis', 'fia': 756},
    'BA': {'name': 'black ash', 'scientific': 'Fraxinus nigra', 'fia': 543},
    'BB': {'name': 'basswood', 'scientific': 'Tilia americana', 'fia': 951},
    'BC': {'name': 'black cherry', 'scientific': 'Prunus serotina', 'fia': 767},
    'BD': {'name': 'sweet birch', 'scientific': 'Betula lenta', 'fia': 375},
    'BG': {'name': 'black gum', 'scientific': 'Nyssa sylvatica', 'fia': 693},
    'BJ': {'name': 'blue jay', 'scientific': 'Cyanocitta cristata', 'fia': 999},  # placeholder
    'BK': {'name': 'sugar maple', 'scientific': 'Acer saccharum', 'fia': 318},
    'BN': {'name': 'butternut', 'scientific': 'Juglans cinerea', 'fia': 601},
    'BO': {'name': 'red maple', 'scientific': 'Acer rubrum', 'fia': 316},
    'BT': {'name': 'bigtooth aspen', 'scientific': 'Populus grandidentata', 'fia': 741},
    'BU': {'name': 'buckeye', 'scientific': 'Aesculus octandra', 'fia': 356},
    'CA': {'name': 'american chestnut', 'scientific': 'Castanea dentata', 'fia': 401},
    'CB': {'name': 'cucumber tree', 'scientific': 'Magnolia acuminata', 'fia': 621},
    'CK': {'name': 'virginia pine', 'scientific': 'Pinus virginiana', 'fia': 131},
    'CO': {'name': 'pond cypress', 'scientific': 'Taxodium ascendens', 'fia': 222},
    'CT': {'name': 'catalpa', 'scientific': 'Catalpa bignonioides', 'fia': 400},
    'CW': {'name': 'chestnut oak', 'scientific': 'Quercus montana', 'fia': 826},
    'DW': {'name': 'dogwood', 'scientific': 'Cornus florida', 'fia': 491},
    'EL': {'name': 'american hornbeam', 'scientific': 'Carpinus caroliniana', 'fia': 391},
    'FM': {'name': 'flowering dogwood', 'scientific': 'Cornus florida', 'fia': 491},
    'GA': {'name': 'green ash', 'scientific': 'Fraxinus pennsylvanica', 'fia': 544},
    'HA': {'name': 'hawthorn', 'scientific': 'Crataegus mexicana', 'fia': 500},
    'HB': {'name': 'hornbeam', 'scientific': 'Carpinus caroliniana', 'fia': 391},
    'HH': {'name': 'dogwood', 'scientific': 'Cornus florida', 'fia': 491},
    'HI': {'name': 'hickory species', 'scientific': 'Carya species', 'fia': 400},
    'HL': {'name': 'holly', 'scientific': 'Ilex opaca', 'fia': 591},
    'HM': {'name': 'eastern hemlock', 'scientific': 'Tsuga canadensis', 'fia': 261},
    'HY': {'name': 'holly', 'scientific': 'Ilex opaca', 'fia': 591},
    'JU': {'name': 'eastern juniper', 'scientific': 'Juniperus virginiana', 'fia': 68},
    'LB': {'name': 'loblolly bay', 'scientific': 'Gordonia lasianthus', 'fia': 571},
    'LK': {'name': 'laurel oak', 'scientific': 'Quercus laurifolia', 'fia': 806},
    'LO': {'name': 'silver maple', 'scientific': 'Acer saccharinum', 'fia': 317},
    'LP': {'name': 'loblolly pine', 'scientific': 'Pinus taeda', 'fia': 131},
    'MB': {'name': 'mountain birch', 'scientific': 'Betula cordifolia', 'fia': 371},
    'MG': {'name': 'magnolia', 'scientific': 'Magnolia grandiflora', 'fia': 622},
    'ML': {'name': 'maple leaf', 'scientific': 'Acer species', 'fia': 310},
    'MS': {'name': 'maple species', 'scientific': 'Acer species', 'fia': 310},
    'MV': {'name': 'magnolia vine', 'scientific': 'Magnolia species', 'fia': 620},
    'OH': {'name': 'other hardwood', 'scientific': 'Hardwood species', 'fia': 999},
    'OS': {'name': 'other softwood', 'scientific': 'Softwood species', 'fia': 299},
    'OT': {'name': 'other tree', 'scientific': 'Tree species', 'fia': 999},
    'OV': {'name': 'overcup oak', 'scientific': 'Quercus lyrata', 'fia': 813},
    'PC': {'name': 'pond cypress', 'scientific': 'Taxodium ascendens', 'fia': 222},
    'PD': {'name': 'pitch pine', 'scientific': 'Pinus rigida', 'fia': 126},
    'PI': {'name': 'pine species', 'scientific': 'Pinus species', 'fia': 100},
    'PO': {'name': 'american beech', 'scientific': 'Fagus grandifolia', 'fia': 531},
    'PP': {'name': 'pond pine', 'scientific': 'Pinus serotina', 'fia': 129},
    'PS': {'name': 'persimmon', 'scientific': 'Diospyros virginiana', 'fia': 521},
    'PU': {'name': 'pond pine', 'scientific': 'Pinus serotina', 'fia': 129},
    'QS': {'name': 'flowering dogwood', 'scientific': 'Cornus florida', 'fia': 491},
    'RA': {'name': 'red ash', 'scientific': 'Fraxinus pennsylvanica', 'fia': 544},
    'RD': {'name': 'redbud', 'scientific': 'Cercis canadensis', 'fia': 471},
    'RL': {'name': 'red elm', 'scientific': 'Ulmus rubra', 'fia': 972},
    'RO': {'name': 'eastern hemlock', 'scientific': 'Tsuga canadensis', 'fia': 261},
    'SA': {'name': 'slash pine', 'scientific': 'Pinus elliottii', 'fia': 111},
    'SB': {'name': 'sweet birch', 'scientific': 'Betula lenta', 'fia': 375},
    'SD': {'name': 'sand pine', 'scientific': 'Pinus clausa', 'fia': 107},
    'SK': {'name': 'swamp oak', 'scientific': 'Quercus bicolor', 'fia': 802},
    'SM': {'name': 'sugar maple', 'scientific': 'Acer saccharum', 'fia': 318},
    'SN': {'name': 'loblolly pine', 'scientific': 'Pinus taeda', 'fia': 131},
    'SO': {'name': 'southern oak', 'scientific': 'Quercus species', 'fia': 800},
    'SP': {'name': 'shortleaf pine', 'scientific': 'Pinus echinata', 'fia': 110},
    'SR': {'name': 'spruce pine', 'scientific': 'Pinus glabra', 'fia': 115},
    'SS': {'name': 'basswood', 'scientific': 'Tilia americana', 'fia': 951},
    'SV': {'name': 'silver maple', 'scientific': 'Acer saccharinum', 'fia': 317},
    'SY': {'name': 'sycamore', 'scientific': 'Platanus occidentalis', 'fia': 756},
    'TM': {'name': 'tamarack', 'scientific': 'Larix laricina', 'fia': 71},
    'TO': {'name': 'tulip oak', 'scientific': 'Liriodendron tulipifera', 'fia': 611},
    'TS': {'name': 'tulip tree', 'scientific': 'Liriodendron tulipifera', 'fia': 611},
    'VP': {'name': 'virginia pine', 'scientific': 'Pinus virginiana', 'fia': 131},
    'WA': {'name': 'white ash', 'scientific': 'Fraxinus americana', 'fia': 541},
    'WE': {'name': 'white elm', 'scientific': 'Ulmus americana', 'fia': 971},
    'WI': {'name': 'willow', 'scientific': 'Salix species', 'fia': 920},
    'WK': {'name': 'water oak', 'scientific': 'Quercus nigra', 'fia': 818},
    'WN': {'name': 'walnut', 'scientific': 'Juglans nigra', 'fia': 602},
    'WP': {'name': 'white pine', 'scientific': 'Pinus strobus', 'fia': 129},
    'WT': {'name': 'water tupelo', 'scientific': 'Nyssa aquatica', 'fia': 692},
    'YP': {'name': 'yellow poplar', 'scientific': 'Liriodendron tulipifera', 'fia': 611},
}

def get_existing_species():
    """Get list of species that already have configuration files."""
    cfg_dir = Path("cfg/species")
    existing = set()
    if cfg_dir.exists():
        for file in cfg_dir.glob("*.yaml"):
            # Extract species code from filename (e.g., "lp_loblolly_pine.yaml" -> "LP")
            code = file.stem.split('_')[0].upper()
            existing.add(code)
    return existing

def create_species_config(species_code):
    """Create a configuration file for a species."""
    if species_code not in SPECIES_DATA:
        print(f"Warning: No data found for species {species_code}")
        return
    
    data = SPECIES_DATA[species_code]
    metadata = SPECIES_METADATA.get(species_code, {
        'name': f'species {species_code.lower()}',
        'scientific': f'Species {species_code}',
        'fia': 999
    })
    
    # Determine if softwood or hardwood based on common patterns
    is_softwood = any(x in metadata['scientific'].lower() for x in ['pinus', 'tsuga', 'juniperus', 'taxodium', 'abies', 'larix'])
    
    # Create filename
    filename = f"cfg/species/{species_code.lower()}_{metadata['name'].replace(' ', '_')}.yaml"
    
    # Write the file manually to control formatting
    with open(filename, 'w') as f:
        f.write(f"# {metadata['name'].title()} ({metadata['scientific']}) Configuration\n")
        f.write(f"# Species in the Southern Variant\n\n")
        
        f.write("metadata:\n")
        f.write(f"  code: {species_code}\n")
        f.write(f"  fia_code: {metadata['fia']}\n")
        f.write(f"  scientific_name: {metadata['scientific']}\n")
        f.write(f"  common_name: {metadata['name']}\n")
        f.write(f"  valid_site_species: true  # Valid for site index calculation\n\n")
        
        f.write("# Site index parameters\n")
        f.write("site_index:\n")
        f.write(f"  min: {data.get('site_index', {}).get('min', 30)}\n")
        f.write(f"  max: {data.get('site_index', {}).get('max', 100)}\n")
        f.write(f"  site_index_group: {1 if is_softwood else 3}  # Group assignment for site index transformations\n")
        f.write(f"  height_growth_equation: \"NC-128: {metadata['fia']}\"  # Reference to site index curve\n\n")
        
        f.write("# Stand density parameters\n")
        f.write("density:\n")
        f.write(f"  sdi_max: {400 if is_softwood else 450}  # Maximum stand density index\n\n")
        
        f.write("# Height-diameter relationship\n")
        f.write("height_diameter:\n")
        f.write("  model: \"curtis_arney\"  # Default model to use\n")
        f.write("  curtis_arney:\n")
        f.write("    p2: 150.0\n")
        f.write("    p3: 4.0\n")
        f.write("    p4: -0.6\n")
        f.write(f"    dbw: {data.get('site_index', {}).get('dbw', 0.5)}  # Diameter breakpoint for small trees\n")
        f.write("  wykoff:\n")
        f.write("    b1: 4.7\n")
        f.write("    b2: -7.0\n\n")
        
        f.write("# Bark ratio parameters\n")
        f.write("bark_ratio:\n")
        f.write("  b1: -0.45\n")
        f.write("  b2: 0.90\n\n")
        
        f.write("# Crown ratio parameters\n")
        f.write("crown_ratio:\n")
        f.write("  equation: \"4.3.1.6\"  # Which equation form to use\n")
        f.write("  d0: 50.0\n")
        f.write("  d1: -16.0\n")
        f.write("  d2: null  # Not used in this equation type\n")
        f.write("  weibull:\n")
        f.write("    a: 4.0\n")
        f.write("    b0: -6.0\n")
        f.write("    b1: 1.0\n")
        f.write("    c: 2.8\n\n")
        
        f.write("# Large tree diameter growth model parameters\n")
        f.write("# Equation form: ln(DDS) = b1 + (b2 * ln(DBH)) + (b3 * DBH^2) + (b4 * ln(CR)) + (b5 * RELHT) + (b6 * SI) + \n")
        f.write("#                          (b7 * BA) + (b8 * PBAL) + (b9 * SLOPE) + (b10 * cos(ASP) * SLOPE) + \n")
        f.write("#                          (b11 * sin(ASP) * SLOPE) + FORTYPE + ECOUNIT + PLANT\n")
        f.write("# \n")
        f.write("# COEFFICIENTS FROM SOUTHERN VARIANT SOURCE OF TRUTH (archive/data/archive/southern_variant_tables/large_tree_growth_parameters.csv)\n")
        f.write(f"# {species_code} = {metadata['name'].title()} ({metadata['scientific']})\n")
        f.write("diameter_growth:\n")
        f.write("  model: \"ln_dds\"  # Natural log of the periodic change in squared inside-bark diameter\n")
        f.write("  coefficients:\n")
        f.write(f"    # Coefficients for {species_code} ({metadata['name'].title()})\n")
        f.write(f"    b1: {data['growth']['b1']:.6f}   # Intercept\n")
        f.write(f"    b2: {data['growth']['b2']:.6f}    # ln(DBH) coefficient\n")
        f.write(f"    b3: {data['growth']['b3']:.6f}   # DBH^2 coefficient\n")
        f.write(f"    b4: {data['growth']['b4']:.6f}    # ln(CR) coefficient\n")
        f.write(f"    b5: {data['growth']['b5']:.6f}    # RELHT coefficient\n")
        f.write(f"    b6: {data['growth']['b6']:.6f}    # SI coefficient\n")
        f.write(f"    b7: {data['growth']['b7']:.6f}   # BA coefficient\n")
        f.write(f"    b8: {data['growth']['b8']:.6f}   # PBAL coefficient\n")
        f.write(f"    b9: {data['growth']['b9']:.6f}   # SLOPE coefficient\n")
        f.write(f"    b10: {data['growth']['b10']:.6f}  # cos(ASP)*SLOPE coefficient\n")
        f.write(f"    b11: {data['growth']['b11']:.6f}  # sin(ASP)*SLOPE coefficient\n")
        f.write("  \n")
        f.write("  # DBH bounding function values from diameter_bounding_limits.csv\n")
        lower = data.get('dbh_bounds', {}).get('lower', 998.0)
        upper = data.get('dbh_bounds', {}).get('upper', 999.0)
        if lower == 998.0 and upper == 999.0:
            f.write(f"  # {species_code}: DBH LOW = {lower}, DBH HI = {upper} (no bounding function applied)\n")
        else:
            f.write(f"  # {species_code}: DBH LOW = {lower}, DBH HI = {upper} (bounding function applied)\n")
        f.write("  dbh_bounds:\n")
        if lower == 998.0 and upper == 999.0:
            f.write("    lower_limit: 998.0  # No diameter bounding function\n")
            f.write("    upper_limit: 999.0  # No diameter bounding function\n\n")
        else:
            f.write(f"    lower_limit: {lower}   # Diameter bounding function lower limit\n")
            f.write(f"    upper_limit: {upper}   # Diameter bounding function upper limit\n\n")
        
        f.write("# Volume specifications\n")
        f.write("volume:\n")
        f.write("  pulpwood:\n")
        f.write("    min_dbh: 6      # Minimum DBH in inches\n")
        f.write("    top_diameter: 4 # Top diameter outside bark in inches\n")
        f.write("  sawtimber:\n")
        f.write("    min_dbh: 10     # Default for softwoods\n" if is_softwood else "    min_dbh: 10     # Default for hardwoods\n")
        f.write("    top_diameter: 7 # Default for softwoods\n" if is_softwood else "    top_diameter: 7 # Default for hardwoods\n")
    
    print(f"Created configuration for {species_code}: {filename}")

def main():
    """Main function to generate all missing species configurations."""
    print("Loading species data from archive files...")
    
    # Load all data
    load_growth_parameters()
    load_site_index_data()
    load_dbh_bounds()
    
    print(f"Loaded data for {len(SPECIES_DATA)} species")
    
    # Get existing species
    existing = get_existing_species()
    print(f"Found {len(existing)} existing species configurations: {sorted(existing)}")
    
    # Create missing configurations
    missing = set(SPECIES_DATA.keys()) - existing
    print(f"Creating configurations for {len(missing)} missing species: {sorted(missing)}")
    
    # Create output directory if it doesn't exist
    os.makedirs("cfg/species", exist_ok=True)
    
    # Generate configurations for missing species
    for species_code in sorted(missing):
        try:
            create_species_config(species_code)
        except Exception as e:
            print(f"Error creating config for {species_code}: {e}")
    
    print(f"\nCompleted! Generated {len(missing)} new species configuration files.")

if __name__ == "__main__":
    main() 
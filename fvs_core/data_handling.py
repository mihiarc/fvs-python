import pandas as pd
from pathlib import Path
from .site_index import calculate_rsisp, calculate_mgspix, calculate_mgrsi, calculate_sisp

# Read data from CSV files
data_dir = Path(__file__).parent.parent / 'data'
species_data = pd.read_csv(data_dir / 'species_data.csv', index_col=0).to_dict('index')
site_index_groups = pd.read_csv(data_dir / 'site_index_groups.csv', index_col=0).to_dict('index')

# Convert string representation of lists back to actual lists in site_index_groups
for group in site_index_groups.values():
    group['mapped species'] = eval(group['mapped species'])

def calculate_site_index(site_species, site_index_value, target_species):
    """
    Calculate the site index for a target species based on the site index of another species.
    
    Args:
        site_species (str): The species code for which we have a site index
        site_index_value (float): The known site index value
        target_species (str): The species code for which we want to calculate the site index
    
    Returns:
        float: The calculated site index for the target species, or None if calculation is not possible
    """
    # Default to WO if site_species is invalid
    if site_species not in species_data:
        site_species = "WO"
    
    # Return None if target_species is invalid
    if target_species not in species_data:
        return None
        
    # Get site index ranges for both species
    site_sp_data = species_data[site_species]
    target_sp_data = species_data[target_species]
    
    # Find the site index group that contains both species
    matching_group = None
    for group_id, group_data in site_index_groups.items():
        if (site_species == group_data["site index species"] or 
            site_species in group_data["mapped species"]) and \
           (target_species == group_data["site index species"] or 
            target_species in group_data["mapped species"]):
            matching_group = group_data
            break
    
    if not matching_group:
        return None
        
    # Calculate relative site index for site species
    rsisp = calculate_rsisp(
        site_index_value,
        site_sp_data["si_min"],
        site_sp_data["si_max"]
    )
    
    # Calculate modified growth site productivity index
    mgspix = calculate_mgspix(
        rsisp,
        site_sp_data["si_min"],
        site_sp_data["si_max"],
        matching_group["a"],
        matching_group["b"]
    )
    
    # Calculate modified growth relative site index
    mgrsi = calculate_mgrsi(
        mgspix,
        target_sp_data["si_min"],
        target_sp_data["si_max"],
        matching_group["c"],
        matching_group["d"]
    )
    
    # Calculate final site index for target species
    return calculate_sisp(
        mgrsi,
        target_sp_data["si_min"],
        target_sp_data["si_max"]
    )

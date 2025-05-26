#!/usr/bin/env python3
"""
Script to update species YAML files with large tree height growth coefficients
from the Southern variant coefficient JSON files.
"""

import json
import yaml
import os
from pathlib import Path

def load_coefficients():
    """Load coefficients from the JSON file (using part2 which has all coefficients)"""
    with open('cfg/sn_large_tree_height_growth_coefficients_part2.json', 'r') as f:
        data = json.load(f)
    return data['coefficients']

def update_species_file(species_file_path, species_code, coefficients):
    """Update a single species YAML file with the coefficients"""
    
    # Load the existing YAML file
    with open(species_file_path, 'r') as f:
        species_data = yaml.safe_load(f)
    
    # Get coefficients for this species
    if species_code.upper() not in coefficients:
        print(f"Warning: No coefficients found for species {species_code}")
        return False
    
    species_coeffs = coefficients[species_code.upper()]
    
    # Update the diameter_growth section
    if 'diameter_growth' not in species_data:
        species_data['diameter_growth'] = {}
    
    species_data['diameter_growth']['model'] = 'ln_dds'
    species_data['diameter_growth']['coefficients'] = {}
    
    # Add all coefficients (b1-b11)
    for coeff_name, coeff_value in species_coeffs.items():
        species_data['diameter_growth']['coefficients'][coeff_name] = coeff_value
    
    # Write back to file
    with open(species_file_path, 'w') as f:
        yaml.dump(species_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated {species_file_path} with coefficients for {species_code}")
    return True

def main():
    """Main function to update all species files"""
    
    # Load coefficients
    coefficients = load_coefficients()
    print(f"Loaded coefficients for {len(coefficients)} species")
    
    # Get all species YAML files
    species_dir = Path('cfg/species')
    species_files = list(species_dir.glob('*.yaml'))
    
    updated_count = 0
    
    for species_file in species_files:
        # Extract species code from filename (e.g., 'ab_american_basswood.yaml' -> 'AB')
        species_code = species_file.stem.split('_')[0].upper()
        
        if update_species_file(species_file, species_code, coefficients):
            updated_count += 1
    
    print(f"\nUpdated {updated_count} species files out of {len(species_files)} total files")
    
    # List species codes that have coefficients but no corresponding files
    existing_codes = {f.stem.split('_')[0].upper() for f in species_files}
    coeff_codes = set(coefficients.keys())
    missing_files = coeff_codes - existing_codes
    
    if missing_files:
        print(f"\nSpecies codes with coefficients but no YAML files: {sorted(missing_files)}")
    
    # List files that don't have coefficients
    missing_coeffs = existing_codes - coeff_codes
    if missing_coeffs:
        print(f"Species files without coefficients: {sorted(missing_coeffs)}")

if __name__ == '__main__':
    main() 
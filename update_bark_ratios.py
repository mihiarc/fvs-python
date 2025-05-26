#!/usr/bin/env python3
"""
Script to update bark ratio coefficients in species YAML files
using the values from sn_bark_ratio_coefficients.json
"""

import json
import yaml
import os
from pathlib import Path

def load_bark_ratio_coefficients():
    """Load bark ratio coefficients from JSON file"""
    with open('docs/sn_bark_ratio_coefficients.json', 'r') as f:
        data = json.load(f)
    return data['species_coefficients']

def update_species_file(species_file_path, species_code, coefficients):
    """Update a single species YAML file with new bark ratio coefficients"""
    try:
        with open(species_file_path, 'r') as f:
            species_data = yaml.safe_load(f)
        
        # Get the coefficients for this species
        if species_code in coefficients:
            b1 = coefficients[species_code]['b1']
            b2 = coefficients[species_code]['b2']
            
            # Update the bark ratio section
            if 'bark_ratio' not in species_data:
                species_data['bark_ratio'] = {}
            
            species_data['bark_ratio']['b1'] = b1
            species_data['bark_ratio']['b2'] = b2
            
            # Write back to file
            with open(species_file_path, 'w') as f:
                yaml.dump(species_data, f, default_flow_style=False, sort_keys=False)
            
            print(f"Updated {species_code}: b1={b1}, b2={b2}")
            return True
        else:
            print(f"Warning: No coefficients found for species {species_code}")
            return False
            
    except Exception as e:
        print(f"Error updating {species_file_path}: {e}")
        return False

def main():
    """Main function to update all species files"""
    # Load bark ratio coefficients
    coefficients = load_bark_ratio_coefficients()
    
    # Get all species YAML files
    species_dir = Path('cfg/species')
    species_files = list(species_dir.glob('*.yaml'))
    
    updated_count = 0
    total_count = len(species_files)
    
    print(f"Found {total_count} species files to update...")
    print()
    
    for species_file in species_files:
        # Extract species code from filename (e.g., 'ab_american_basswood.yaml' -> 'AB')
        species_code = species_file.stem.split('_')[0].upper()
        
        if update_species_file(species_file, species_code, coefficients):
            updated_count += 1
    
    print()
    print(f"Successfully updated {updated_count} out of {total_count} species files")
    
    # Show which species codes were not found
    all_species_codes = {f.stem.split('_')[0].upper() for f in species_files}
    missing_codes = all_species_codes - set(coefficients.keys())
    if missing_codes:
        print(f"Species codes without coefficients: {sorted(missing_codes)}")

if __name__ == "__main__":
    main() 
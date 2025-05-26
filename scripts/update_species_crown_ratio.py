#!/usr/bin/env python3

"""
Update species configuration files with crown ratio coefficients from SN variant.
Reads the extracted crown ratio coefficients and updates all species YAML files.
"""

import json
import yaml
from pathlib import Path
import sys

def load_crown_ratio_coefficients():
    """Load crown ratio coefficients from the extracted JSON file."""
    crown_ratio_file = Path("docs/sn_crown_ratio_coefficients.json")
    
    if not crown_ratio_file.exists():
        print(f"Error: Crown ratio coefficients file not found: {crown_ratio_file}")
        sys.exit(1)
    
    with open(crown_ratio_file, 'r') as f:
        return json.load(f)

def update_species_file(species_file, species_code, coefficients):
    """Update a single species YAML file with crown ratio coefficients."""
    
    # Load existing YAML
    with open(species_file, 'r') as f:
        species_data = yaml.safe_load(f)
    
    # Get coefficients for this species
    if species_code in coefficients['species_coefficients']:
        species_coeffs = coefficients['species_coefficients'][species_code]
        
        # Update crown ratio section
        if 'crown_ratio' not in species_data:
            species_data['crown_ratio'] = {}
        
        # Update equation type and parameters
        species_data['crown_ratio']['equation'] = species_coeffs['acr_equation']
        species_data['crown_ratio']['d0'] = species_coeffs['d0']
        species_data['crown_ratio']['d1'] = species_coeffs.get('d1')
        species_data['crown_ratio']['d2'] = species_coeffs.get('d2')
        
        # Update Weibull parameters
        if 'weibull' not in species_data['crown_ratio']:
            species_data['crown_ratio']['weibull'] = {}
        
        species_data['crown_ratio']['weibull']['a'] = species_coeffs['a']
        species_data['crown_ratio']['weibull']['b0'] = species_coeffs['b0']
        species_data['crown_ratio']['weibull']['b1'] = species_coeffs['b1']
        species_data['crown_ratio']['weibull']['c'] = species_coeffs['c']
        
        # Write updated YAML back to file
        with open(species_file, 'w') as f:
            yaml.dump(species_data, f, default_flow_style=False, sort_keys=False)
        
        return True
    else:
        print(f"Warning: No crown ratio coefficients found for species {species_code}")
        return False

def main():
    """Main function to update all species files."""
    
    # Load crown ratio coefficients
    print("Loading crown ratio coefficients...")
    coefficients = load_crown_ratio_coefficients()
    
    # Find all species YAML files
    species_dir = Path("cfg/species")
    if not species_dir.exists():
        print(f"Error: Species directory not found: {species_dir}")
        sys.exit(1)
    
    species_files = list(species_dir.glob("*.yaml"))
    
    if not species_files:
        print(f"Error: No YAML files found in {species_dir}")
        sys.exit(1)
    
    print(f"Found {len(species_files)} species files")
    
    updated_count = 0
    skipped_count = 0
    
    # Update each species file
    for species_file in sorted(species_files):
        # Extract species code from filename (e.g., "ab_american_basswood.yaml" -> "AB")
        species_code = species_file.stem.split('_')[0].upper()
        
        print(f"Processing {species_file.name} (species: {species_code})...")
        
        try:
            if update_species_file(species_file, species_code, coefficients):
                updated_count += 1
                print(f"  ✓ Updated {species_code}")
            else:
                skipped_count += 1
                print(f"  - Skipped {species_code} (no coefficients)")
        except Exception as e:
            print(f"  ✗ Error updating {species_code}: {e}")
            skipped_count += 1
    
    print(f"\nUpdate complete!")
    print(f"Updated: {updated_count} species")
    print(f"Skipped: {skipped_count} species")
    
    # Show summary of equation types used
    print(f"\nEquation types in crown ratio coefficients:")
    equation_counts = {}
    for species_code, coeffs in coefficients['species_coefficients'].items():
        eq_type = coeffs['acr_equation']
        equation_counts[eq_type] = equation_counts.get(eq_type, 0) + 1
    
    for eq_type, count in sorted(equation_counts.items()):
        print(f"  {eq_type}: {count} species")

if __name__ == "__main__":
    main() 
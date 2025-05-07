# FVS-Python Configuration

This directory contains YAML configuration files for the FVS-Python implementation. These files define the parameters and functional forms for the Southern (SN) variant of the Forest Vegetation Simulator.

## Configuration Structure

The configuration is organized into the following files:

### Main Configuration File

- `species_config.yaml`: Main configuration file that references all species-specific configuration files

### Shared Parameter Files

- `functional_forms.yaml`: Mathematical definitions of equations used across species
- `site_index_transformation.yaml`: Parameters for transforming site index between species

### Species-Specific Files

Individual species parameter files are stored in the `species/` directory with filenames following the pattern `<code>_<name>.yaml`, for example:
- `species/lp_loblolly_pine.yaml`
- `species/sa_slash_pine.yaml`
- `species/wo_white_oak.yaml`

## Configuration Format

Each species configuration file includes:

1. **Metadata**: Species codes, scientific name, common name
2. **Site Index Parameters**: Range and grouping information
3. **Density Parameters**: Maximum SDI and related values
4. **Height-Diameter Relationship**: Curtis-Arney and Wykoff equation parameters
5. **Bark Ratio Parameters**: Coefficients for inside/outside bark conversion
6. **Crown Ratio Parameters**: Coefficients for crown ratio estimation

## Usage

To use these configuration files in your FVS-Python implementation:

```python
import yaml

# Load main configuration
with open('cfg/species_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access a specific species
species_code = 'LP'  # Loblolly pine
species_info = config['species'][species_code]
species_file = species_info['file']

# Load species configuration
with open(f'cfg/{species_file}', 'r') as f:
    species_config = yaml.safe_load(f)

# Access specific parameters
height_diameter_params = species_config['height_diameter']
```

## Extending

To add a new species:

1. Create a new YAML file in the `species/` directory
2. Add the species to the `species_config.yaml` file
3. Ensure all required parameters are included

## References

The parameters in these files are derived from:
- FVS Southern Variant Overview documentation
- USDA Forest Service research papers
- Southern Research Station publications 
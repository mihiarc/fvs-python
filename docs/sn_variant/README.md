# Southern Variant Documentation

## Overview
This directory contains the complete documentation for the Southern Variant of the Forest Vegetation Simulator (FVS), broken down into manageable sections while preserving all original text and data from the source document.

## Document Structure

### [01_diameter_growth_models.md](01_diameter_growth_models.md)
**Diameter Growth Models**
- Complete coefficients for diameter increment models (Tables 4.7.1.1 - 4.7.1.8)
- Species-specific parameters (b1-b11 coefficients)
- DBH bounding function values
- All softwood and hardwood species covered

### [02_height_growth_models.md](02_height_growth_models.md)
**Height Growth Models**
- Large-tree height growth equations (Section 4.7.2)
- Crown ratio and relative height modifiers
- Shade tolerance classifications by species
- Relative height modifier coefficients

### [03_mortality_models.md](03_mortality_models.md)
**Mortality Models**
- Background mortality equations (Section 5.0)
- Density-dependent mortality thresholds
- Mortality dispersion models
- Species-specific mortality coefficients and weights

### [04_volume_equations.md](04_volume_equations.md)
**Volume Equations**
- Cubic foot volume equations (Section 7.0)
- Board foot volume equations (Scribner rule)
- Species-specific volume coefficients
- Volume calculation applications

### [05_ecological_unit_codes.md](05_ecological_unit_codes.md)
**Ecological Unit Codes**
- Complete ecological unit classifications (Section 11.1)
- State-by-state ecological provinces and sections
- Site productivity implications
- Usage in FVS modeling

## Key Species Codes

### Primary Pine Species
- **LP** - Loblolly Pine
- **SP** - Slash Pine
- **LL** - Longleaf Pine
- **VP** - Virginia Pine
- **WP** - White Pine
- **SR** - Spruce Pine

### Primary Hardwood Species
- **RM** - Red Maple
- **SM** - Sugar Maple
- **BE** - American Beech
- **HI** - Hickory
- **WO** - White Oak
- **RO** - Red Oak

### Other Important Species
- **BY** - Bald Cypress
- **HM** - Eastern Hemlock
- **SS** - Sweetgum
- **YP** - Yellow Poplar

## Model Equations Summary

### Diameter Growth
```
DG = f(DBH, competition, site, species coefficients b1-b11)
```

### Height Growth
```
HTG = POTHTG * (0.25 * HGMDCR + 0.75 * HGMDRH)
```

### Mortality
```
Background: RI = exp(p0 + p1 * DBH)
Density-dependent: Triggered at 55% of maximum SDI
```

### Volume
```
Cubic Foot: CFVOL = b0 + b1*DBH² + b2*DBH²*HT + b3*DBH*HT² + b4*HT²
Board Foot: BFVOL = c0 + c1*DBH² + c2*DBH²*HT + c3*DBH*HT² + c4*HT²
```

## Geographic Coverage

The Southern Variant covers the following states:
- Alabama
- Arkansas  
- Florida
- Georgia
- Kentucky
- Louisiana
- Mississippi
- North Carolina
- South Carolina
- Tennessee
- Texas
- Virginia
- West Virginia

## Implementation Guidelines

### For FVS-Python Development

1. **Parameter Loading**: Use the coefficient tables to populate species-specific parameters
2. **Equation Implementation**: Implement the mathematical models exactly as specified
3. **Species Validation**: Ensure species codes match the documented classifications
4. **Regional Applicability**: Verify ecological unit codes for geographic accuracy

### Data Requirements

**Minimum Tree Data:**
- Species code
- DBH (diameter at breast height)
- Height
- Trees per acre
- Crown ratio (for height growth)

**Stand Data:**
- Site index
- Ecological unit code
- Stand density index (SDI)
- Age (for even-aged stands)

**Optional Data:**
- Aspect and slope
- Elevation
- Soil characteristics

## Source of Truth

**Important**: These documents represent the authoritative source for all growth equations and coefficients. When implementing FVS-Python:

1. **Never modify growth functions or coefficients** without documentation
2. **Reference these documents** for all parameter values
3. **Validate implementations** against the documented equations
4. **Preserve equation forms** exactly as specified

## Usage in FVS-Python

### Configuration Integration
The parameters from these documents should be integrated into the FVS-Python configuration system:

```python
# Example: Loading diameter growth coefficients for Loblolly Pine
species_params = {
    'LP': {
        'diameter_growth': {
            'b1': -1.321662,
            'b2': 1.640507,
            'b3': -0.000285,
            # ... additional coefficients
        }
    }
}
```

### Model Implementation
Each equation should be implemented as a separate function with clear documentation:

```python
def calculate_diameter_growth(dbh, competition_index, species_params):
    """Calculate diameter growth using Southern Variant equations."""
    # Implementation based on documented equations
    pass
```

## Quality Assurance

When using these documents:

1. **Cross-reference** equation numbers with original FVS documentation
2. **Validate** coefficient values against multiple sources when possible
3. **Test** implementations with known data sets
4. **Document** any assumptions or modifications made during implementation

## Updates and Maintenance

These documents should be:
- **Version controlled** with the FVS-Python project
- **Updated** only when official FVS documentation changes
- **Reviewed** periodically for accuracy and completeness
- **Referenced** in all code that implements the equations

---

*This documentation is derived from the official FVS Southern Variant documentation and serves as the source of truth for FVS-Python implementation.* 
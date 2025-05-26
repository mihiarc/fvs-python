# Crown Competition Factor (CCF) Module

## Overview

The Crown Competition Factor (CCF) module implements the FVS Southern variant equations for calculating crown competition factor at both individual tree and stand levels. CCF is a relative measurement of stand density based on tree diameters and crown dimensions, providing a useful metric for forest management decisions.

## Key Features

- **Individual Tree CCF**: Calculate CCF for individual trees using equation 4.5.1
- **Stand-level CCF**: Sum individual tree CCF values for stand-level assessment
- **CCF Interpretation**: Automatic interpretation with management recommendations
- **Thinning Analysis**: Analyze CCF changes after thinning operations
- **Target Density Planning**: Estimate trees per acre needed for target CCF values
- **Integration**: Seamless integration with existing Stand and Tree classes

## Mathematical Foundation

### Equation 4.5.1 (Individual Tree CCF)

For trees with DBH > 0.1 inches:
```
CCFt = 0.001803 × OCWt²
```

For trees with DBH ≤ 0.1 inches:
```
CCFt = 0.001
```

Where:
- `CCFt` = Crown competition factor for an individual tree (percentage of acre)
- `OCWt` = Open-grown crown width for the tree (feet)
- `DBH` = Diameter at breast height (inches)

### Stand CCF
```
CCF = Σ CCFt
```
Stand CCF is the summation of all individual tree CCF values.

## Usage Examples

### Basic Individual Tree CCF

```python
from fvs_python.crown_competition_factor import calculate_individual_ccf

# Calculate CCF for a 10-inch DBH tree
ccf = calculate_individual_ccf(dbh=10.0, species_code="LP")
print(f"Individual tree CCF: {ccf:.4f}")
```

### Stand-level CCF Calculation

```python
from fvs_python.crown_competition_factor import calculate_stand_ccf

# Define tree data
trees = [
    {"dbh": 8.0},
    {"dbh": 10.0}, 
    {"dbh": 12.0},
    {"dbh": 14.0}
]

# Calculate stand CCF
stand_ccf = calculate_stand_ccf(trees, species_code="LP")
print(f"Stand CCF: {stand_ccf:.1f}")
```

### Integration with Stand Objects

```python
from fvs_python.stand import Stand
from fvs_python.tree import Tree
from fvs_python.crown_competition_factor import calculate_ccf_from_stand

# Create trees and stand
trees = [
    Tree(dbh=10.0, height=50.0),
    Tree(dbh=12.0, height=55.0),
    Tree(dbh=8.0, height=45.0)
]
stand = Stand(trees, site_index=70)

# Calculate CCF
ccf = calculate_ccf_from_stand(stand)
print(f"Stand CCF: {ccf:.3f}")
```

### CCF Interpretation

```python
from fvs_python.crown_competition_factor import interpret_ccf

ccf_value = 150.0
interpretation = interpret_ccf(ccf_value)

print(f"CCF: {interpretation['ccf_value']}")
print(f"Stocking Level: {interpretation['stocking_level']}")
print(f"Management: {interpretation['management_recommendation']}")
```

### Thinning Impact Analysis

```python
from fvs_python.crown_competition_factor import create_ccf_model

model = create_ccf_model()

# Pre-thinning trees
pre_thin = [{"dbh": 8.0}, {"dbh": 10.0}, {"dbh": 12.0}, {"dbh": 14.0}]

# Trees to remove
removed = [{"dbh": 8.0}, {"dbh": 10.0}]

# Analyze thinning impact
results = model.calculate_ccf_change_after_thinning(pre_thin, removed)
print(f"CCF reduction: {results['ccf_reduction_percent']:.1f}%")
```

### Target Density Planning

```python
from fvs_python.crown_competition_factor import create_ccf_model

model = create_ccf_model()

# Estimate trees per acre for target CCF
target_ccf = 150.0
mean_dbh = 12.0
tpa = model.estimate_trees_per_acre_at_ccf(target_ccf, mean_dbh)
print(f"Trees per acre needed: {tpa:.0f}")
```

## CCF Interpretation Guidelines

| CCF Range | Stocking Level | Interpretation | Management Recommendation |
|-----------|----------------|----------------|---------------------------|
| < 100 | Low density | Tree crowns don't touch; gaps exist | Consider regeneration or planting |
| = 100 | Optimal theoretical | Tree crowns just touch | Monitor for competition development |
| 100-200 | Optimal range | Crown overlap and competition present | Normal management practices |
| > 200 | High density | Significant crown overlap and competition | Consider thinning to reduce competition |

## API Reference

### Classes

#### `CrownCompetitionFactorModel`

Main class for CCF calculations and analysis.

**Methods:**
- `calculate_individual_ccf(dbh, open_crown_width=None, species_code="LP")`: Calculate individual tree CCF
- `calculate_stand_ccf(trees_data, species_code="LP")`: Calculate stand-level CCF
- `interpret_ccf_value(ccf)`: Interpret CCF value with management recommendations
- `calculate_ccf_change_after_thinning(pre_thin_trees, removed_trees, species_code="LP")`: Analyze thinning impacts
- `estimate_trees_per_acre_at_ccf(target_ccf, mean_dbh, species_code="LP")`: Estimate TPA for target CCF

### Standalone Functions

- `create_ccf_model()`: Factory function to create CCF model
- `calculate_individual_ccf(dbh, open_crown_width=None, species_code="LP")`: Calculate individual tree CCF
- `calculate_stand_ccf(trees_data, species_code="LP")`: Calculate stand CCF
- `calculate_ccf_from_stand(stand)`: Calculate CCF from Stand object
- `interpret_ccf(ccf)`: Interpret CCF value
- `validate_ccf_implementation()`: Validate implementation with test cases

## Configuration

The module loads parameters from `cfg/sn_crown_competition_factor.json`, which contains:

- **Coefficient**: 0.001803 (conversion factor for equation 4.5.1)
- **Small tree CCF**: 0.001 (fixed value for DBH ≤ 0.1 inches)
- **DBH threshold**: 0.1 inches (threshold for small tree treatment)

## Dependencies

The CCF module depends on:
- `crown_width` module for open-grown crown width calculations
- `config_loader` for parameter management
- Standard Python libraries: `json`, `math`, `typing`, `pathlib`

## Validation

The module includes comprehensive validation with test cases covering:
- Small tree CCF calculations (DBH ≤ 0.1 inches)
- Standard CCF calculations for various tree sizes
- Stand-level CCF summation
- Integration with existing classes

Run validation:
```python
from fvs_python.crown_competition_factor import validate_ccf_implementation
results = validate_ccf_implementation()
print(f"Tests passed: {results['passed']}/{results['passed'] + results['failed']}")
```

## Example Applications

### Forest Management Planning

```python
# Assess current stand density
current_ccf = calculate_ccf_from_stand(my_stand)
interpretation = interpret_ccf(current_ccf)

if interpretation['stocking_level'] == 'High density':
    print("Consider thinning operation")
elif interpretation['stocking_level'] == 'Low density':
    print("Consider regeneration activities")
```

### Thinning Prescription Development

```python
# Analyze different thinning scenarios
model = create_ccf_model()

scenarios = [
    {"name": "Light thin", "remove": light_thin_trees},
    {"name": "Heavy thin", "remove": heavy_thin_trees}
]

for scenario in scenarios:
    results = model.calculate_ccf_change_after_thinning(
        current_trees, scenario["remove"]
    )
    print(f"{scenario['name']}: {results['ccf_reduction_percent']:.1f}% CCF reduction")
```

### Plantation Establishment

```python
# Plan initial planting density
target_ccf = 120  # Target CCF at rotation
expected_dbh = 14.0  # Expected DBH at rotation

tpa = model.estimate_trees_per_acre_at_ccf(target_ccf, expected_dbh)
print(f"Plant {tpa:.0f} trees per acre")
```

## References

- Krajicek, J.E.; Brinkman, K.A.; Gingrich, S.F. 1961. Crown competition—a measure of density. Forest Science 7(1): 35-42.
- FVS Southern Variant Documentation - Section 4.5
- Dixon, Gary E. 2002. Essential FVS: A User's Guide to the Forest Vegetation Simulator.

## Testing

Run the demonstration script to see all features in action:

```bash
python demo_crown_competition_factor.py
```

This will demonstrate:
- Individual tree CCF calculations
- Stand-level CCF calculations  
- CCF interpretation and management recommendations
- Thinning impact analysis
- Target density planning
- Implementation validation 
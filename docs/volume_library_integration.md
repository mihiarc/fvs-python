# Volume Library Integration

## Overview

The FVS-Python package now includes full integration with the USFS Volume Estimator Library (NVEL), providing professional-grade volume calculations for forest inventory and growth modeling. This integration replaces the simple form-factor-based volume calculations with industry-standard volume equations used by the Forest Service.

## Features

### Professional Volume Calculations
- **NVEL Integration**: Direct access to USFS Volume Estimator Library equations
- **Multiple Volume Types**: Total cubic, merchantable cubic, board foot, biomass, and weight estimates
- **Species-Specific Equations**: Proper volume equations for each FVS Southern variant species
- **Automatic Fallback**: Graceful degradation when NVEL is unavailable

### Seamless Integration
- **Tree Class Enhancement**: Enhanced `get_volume()` method with multiple volume types
- **Stand-Level Calculations**: Automatic volume aggregation at stand level
- **Backward Compatibility**: Existing code continues to work without modification
- **Error Handling**: Robust error handling with informative warnings

## Installation and Setup

### Prerequisites
- Windows operating system (NVEL DLL is Windows-only)
- FVS-Python package installed
- Volume library DLL (`vollib.dll`) available

### DLL Location
The volume library automatically searches for `vollib.dll` in these locations:
1. `VolLibDll20250512/vollib-64bits/vollib.dll` (relative to package root)
2. `VolLibDll20250512/vollib-32bits/vollib.dll` (relative to package root)
3. `vollib/vollib.dll` (relative to package root)
4. `vollib.dll` (current directory)

### Verification
```python
from fvs_python import get_volume_library_info, validate_volume_library

# Check if volume library is available
info = get_volume_library_info()
print(f"Volume Library Available: {info['available']}")
print(f"Version: {info['version']}")

# Validate functionality
validation = validate_volume_library()
print(f"Validation Passed: {validation['dll_available']}")
```

## Usage

### Basic Tree Volume Calculation

```python
from fvs_python import Tree

# Create a tree
tree = Tree(dbh=12.0, height=60.0, species='LP', age=15)

# Get total cubic volume (default)
volume = tree.get_volume()
print(f"Total cubic volume: {volume:.2f} cubic feet")

# Get specific volume types
board_feet = tree.get_volume('board_foot')
green_weight = tree.get_volume('green_weight')
biomass = tree.get_volume('biomass_main_stem')

print(f"Board foot volume: {board_feet:.2f} board feet")
print(f"Green weight: {green_weight:.2f} pounds")
print(f"Main stem biomass: {biomass:.2f} pounds")
```

### Available Volume Types

| Volume Type | Description | Units |
|-------------|-------------|-------|
| `total_cubic` | Total cubic volume (default) | cubic feet |
| `gross_cubic` | Gross cubic volume | cubic feet |
| `net_cubic` | Net cubic volume | cubic feet |
| `merchantable_cubic` | Merchantable cubic volume | cubic feet |
| `board_foot` | Board foot volume | board feet |
| `cord` | Cord volume | cords |
| `green_weight` | Green weight | pounds |
| `dry_weight` | Dry weight | pounds |
| `sawlog_cubic` | Sawlog cubic volume | cubic feet |
| `sawlog_board_foot` | Sawlog board foot volume | board feet |
| `biomass_main_stem` | Main stem biomass | pounds |
| `biomass_live_branches` | Live branch biomass | pounds |
| `biomass_foliage` | Foliage biomass | pounds |

### Detailed Volume Information

```python
# Get complete volume breakdown
detailed = tree.get_volume_detailed()

print(f"Total cubic volume: {detailed['total_cubic_volume']:.2f}")
print(f"Board foot volume: {detailed['board_foot_volume']:.2f}")
print(f"Green weight: {detailed['green_weight']:.2f}")
print(f"Error flag: {detailed['error_flag']}")

# Check if calculation was successful
if detailed['error_flag'] == 0:
    print("✓ NVEL calculation successful")
else:
    print("⚠ Using fallback calculation")
```

### Direct Volume Library Access

```python
from fvs_python import calculate_tree_volume, VolumeLibrary

# Direct calculation
result = calculate_tree_volume(
    dbh=15.0,
    height=70.0,
    species_code='LP'
)

print(f"Total volume: {result.total_cubic_volume:.2f} cubic feet")
print(f"Board feet: {result.board_foot_volume:.2f} board feet")

# Advanced usage with custom parameters
vol_lib = VolumeLibrary()
result = vol_lib.calculate_volume(
    dbh=15.0,
    height=70.0,
    species_code='LP',
    region=8,  # Southern Region
    forest="01",
    height_type="F",  # Total height
    live_dead="L"     # Live tree
)
```

### Stand-Level Volume Calculations

```python
from fvs_python import Stand, Tree

# Create stand with multiple trees
stand = Stand()
trees_data = [
    {'dbh': 8.0, 'height': 45.0, 'species': 'LP'},
    {'dbh': 10.0, 'height': 55.0, 'species': 'LP'},
    {'dbh': 12.0, 'height': 65.0, 'species': 'SP'},
]

for tree_data in trees_data:
    tree = Tree(**tree_data)
    stand.add_tree(tree)

# Get stand metrics (automatically uses new volume calculations)
metrics = stand.get_metrics()
print(f"Total stand volume: {metrics['volume']:.2f} cubic feet")

# Calculate volume by species
volume_by_species = {}
for tree in stand.trees:
    species = tree.species
    if species not in volume_by_species:
        volume_by_species[species] = 0
    volume_by_species[species] += tree.get_volume()

for species, volume in volume_by_species.items():
    print(f"{species}: {volume:.2f} cubic feet")
```

## Supported Species

The volume library supports all FVS Southern variant species:

### Pine Species
- **LP**: Loblolly Pine (Pinus taeda)
- **SP**: Shortleaf Pine (Pinus echinata)
- **LL**: Longleaf Pine (Pinus palustris)
- **SA**: Slash Pine (Pinus elliottii)
- **VP**: Virginia Pine (Pinus virginiana)
- **PD**: Pitch Pine (Pinus rigida)
- **SR**: Spruce Pine (Pinus glabra)
- **PP**: Pond Pine (Pinus serotina)
- **SD**: Sand Pine (Pinus clausa)

### Hardwood Species
- **WO**: White Oak (Quercus alba)
- **SO**: Southern Red Oak (Quercus falcata)
- **WK**: Water Oak (Quercus nigra)
- **LK**: Laurel Oak (Quercus laurifolia)
- **HI**: Hickory species (Carya spp.)
- **SU**: Sweetgum (Liquidambar styraciflua)
- **YP**: Yellow Poplar (Liriodendron tulipifera)
- **RM**: Red Maple (Acer rubrum)
- **BC**: Black Cherry (Prunus serotina)
- **SY**: American Sycamore (Platanus occidentalis)
- **BG**: Black Gum (Nyssa sylvatica)
- **WE**: White Elm (Ulmus americana)
- **BE**: American Beech (Fagus grandifolia)
- **BY**: Bald Cypress (Taxodium distichum)

## Technical Details

### Volume Equation Selection
The library automatically selects appropriate volume equations based on:
- **Species**: FVS species code mapped to NVEL species code
- **Region**: Forest Service region (default: Region 8 - Southern)
- **Forest**: Forest code (default: "01")
- **District**: District code (default: "01")

### Error Handling
The integration includes comprehensive error handling:

1. **DLL Not Found**: Automatic fallback to form-factor calculation
2. **Species Not Supported**: Uses fallback calculation with warning
3. **Calculation Errors**: Returns fallback result with error flag
4. **Platform Issues**: Graceful degradation on non-Windows systems

### Fallback Calculation
When NVEL is unavailable, the system uses the original FVS-Python calculation:
```python
# Fallback method (same as original Tree.get_volume())
dbh_inside_bark = bark_ratio_model.apply_bark_ratio_to_dbh(dbh)
form_factor = 0.48
basal_area_ib = π * (dbh_inside_bark / 24)²
volume = basal_area_ib * height * form_factor
```

## Performance Considerations

### Caching
- Volume library instance is cached globally
- Species mappings are loaded once at initialization
- DLL loading is performed once per session

### Memory Usage
- Minimal memory overhead for volume calculations
- Results are not cached (calculated on-demand)
- DLL remains loaded for session duration

### Speed
- NVEL calculations are very fast (microseconds per tree)
- Fallback calculations are even faster
- No significant performance impact on existing code

## Migration Guide

### Existing Code Compatibility
Existing code using `tree.get_volume()` will continue to work without modification:

```python
# This code works exactly the same as before
tree = Tree(dbh=10.0, height=50.0, species='LP')
volume = tree.get_volume()  # Now uses NVEL if available
```

### Enhanced Functionality
To take advantage of new features:

```python
# Old way (still works)
volume = tree.get_volume()

# New way (enhanced)
cubic_volume = tree.get_volume('total_cubic')
board_feet = tree.get_volume('board_foot')
biomass = tree.get_volume('biomass_main_stem')

# Detailed breakdown
all_volumes = tree.get_volume_detailed()
```

### Stand Calculations
Stand-level calculations automatically benefit from improved volume estimates:

```python
# No code changes needed - automatically uses new volume calculations
stand = Stand()
# ... add trees ...
metrics = stand.get_metrics()  # Uses NVEL volumes
```

## Troubleshooting

### Common Issues

#### Volume Library Not Found
```
Warning: Volume library DLL not found. Volume calculations will use fallback method.
```
**Solution**: Ensure `vollib.dll` is in one of the expected locations.

#### Platform Compatibility
```
Warning: Volume library DLL is only available for Windows.
```
**Solution**: This is expected on non-Windows systems. Fallback calculations will be used.

#### Species Not Supported
```
Warning: Volume calculation failed: Species 'XX' not found.
```
**Solution**: Check that the species code is valid for FVS Southern variant.

### Validation
Use the validation function to diagnose issues:

```python
from fvs_python import validate_volume_library

validation = validate_volume_library()
print(f"DLL Available: {validation['dll_available']}")
print(f"Version: {validation['version']}")

for test in validation['test_results']:
    print(f"{test['species']}: {'✓' if test['success'] else '✗'}")
```

### Debug Information
Get detailed information about the volume library:

```python
from fvs_python import get_volume_library_info

info = get_volume_library_info()
print(f"Available: {info['available']}")
print(f"Version: {info['version']}")
print(f"DLL Path: {info['dll_path']}")
print(f"Supported Species: {info['supported_species']}")
```

## Examples

### Complete Example: Growth Simulation with Volume Tracking

```python
from fvs_python import Stand, Tree

# Initialize planted stand
stand = Stand()
initial_trees = [
    {'dbh': 0.5, 'height': 1.0, 'species': 'LP', 'age': 0},
    {'dbh': 0.5, 'height': 1.0, 'species': 'LP', 'age': 0},
    # ... more trees
]

for tree_data in initial_trees:
    stand.add_tree(Tree(**tree_data))

# Simulate growth and track volume
results = []
for age in range(0, 51, 5):
    # Grow trees
    for tree in stand.trees:
        tree.grow(site_index=70, competition_factor=0.1, time_step=5)
    
    # Calculate volumes
    total_volume = sum(tree.get_volume() for tree in stand.trees)
    board_feet = sum(tree.get_volume('board_foot') for tree in stand.trees)
    biomass = sum(tree.get_volume('biomass_main_stem') for tree in stand.trees)
    
    results.append({
        'age': age,
        'volume_cubic': total_volume,
        'volume_board_feet': board_feet,
        'biomass_pounds': biomass,
        'trees': len(stand.trees)
    })

# Display results
for result in results:
    print(f"Age {result['age']:2d}: "
          f"{result['volume_cubic']:6.1f} cu ft, "
          f"{result['volume_board_feet']:6.0f} bd ft, "
          f"{result['biomass_pounds']:6.0f} lbs biomass")
```

### Volume Comparison Example

```python
from fvs_python import Tree

# Compare volume calculations for different species
species_list = ['LP', 'SP', 'LL', 'SA']
dbh, height = 12.0, 60.0

print(f"Volume comparison for {dbh}\" DBH, {height}' height:")
print("-" * 60)

for species in species_list:
    tree = Tree(dbh=dbh, height=height, species=species)
    
    cubic = tree.get_volume('total_cubic')
    board_feet = tree.get_volume('board_foot')
    biomass = tree.get_volume('biomass_main_stem')
    
    print(f"{species}: {cubic:5.1f} cu ft, {board_feet:5.0f} bd ft, {biomass:5.0f} lbs")
```

## API Reference

### Tree Class Methods

#### `get_volume(volume_type='total_cubic') -> float`
Calculate tree volume using NVEL equations.

**Parameters:**
- `volume_type` (str): Type of volume to calculate (see table above)

**Returns:**
- `float`: Volume in appropriate units

#### `get_volume_detailed() -> dict`
Get complete volume breakdown.

**Returns:**
- `dict`: Dictionary with all volume types and error information

### Module Functions

#### `calculate_tree_volume(dbh, height, species_code, **kwargs) -> VolumeResult`
Direct volume calculation function.

**Parameters:**
- `dbh` (float): Diameter at breast height (inches)
- `height` (float): Total height (feet)
- `species_code` (str): FVS species code
- `**kwargs`: Additional parameters for VolumeLibrary.calculate_volume()

**Returns:**
- `VolumeResult`: Object containing all volume calculations

#### `get_volume_library_info() -> dict`
Get information about volume library availability.

**Returns:**
- `dict`: Library information including availability, version, and supported species

#### `validate_volume_library() -> dict`
Validate volume library installation and functionality.

**Returns:**
- `dict`: Validation results including test outcomes for each species

### Classes

#### `VolumeLibrary`
Main wrapper class for USFS Volume Estimator Library.

#### `VolumeResult`
Container for volume calculation results with named attributes for each volume type.

#### `FortranChar`
Helper class for Fortran string handling (internal use).

---

This integration provides FVS-Python with professional-grade volume calculations while maintaining backward compatibility and providing graceful fallback when the volume library is unavailable. 
# FIA Database Variables Documentation

This document provides detailed information about all variables in the test database (`test_coastal_loblolly.db`).

## Table Structure

The database consists of three base tables (`stands`, `trees`, `growth`) and two views (`complete_tree_data`, `stand_summary`).

## Base Tables

### Stands Table

Contains stand-level characteristics. Each record represents a unique forest stand.

| Variable | Type | Description | Range/Units | Notes |
|----------|------|-------------|-------------|--------|
| STAND_CN | TEXT | Stand identifier | - | Primary key, links to trees table |
| LATITUDE | REAL | Stand latitude | 30.75° to 33.02°N | Coastal Georgia region |
| LONGITUDE | REAL | Stand longitude | -81.92° to -81.05° | Coastal Georgia region |
| ELEVATION | TEXT | Stand elevation | - | Elevation above sea level |
| SLOPE | REAL | Terrain slope | 0° to 35° | Steepness of terrain |
| ASPECT | REAL | Slope aspect | 0° to 360° | Direction slope faces |
| FOREST_TYPE | TEXT | Forest type classification | - | Classification code |
| SITE_SPECIES | TEXT | Site index species | e.g., '131' | Species used for site index |
| SITE_INDEX | REAL | Site productivity index | 52 to 154 | Measure of site quality |
| STATE | REAL | State code | 13 | Georgia |
| COUNTY | REAL | County code | 29 to 251 | Georgia county codes |

### Trees Table

Contains tree-level measurements. Each record represents an individual tree or group of similar trees.

| Variable | Type | Description | Range/Units | Notes |
|----------|------|-------------|-------------|--------|
| STAND_CN | TEXT | Stand identifier | - | Foreign key to stands table |
| TREE_CN | TEXT | Tree identifier | - | Primary key, links to growth table |
| SPECIES | TEXT | Species code | e.g., '131' | '131' = Loblolly Pine |
| DIAMETER | REAL | Tree diameter | 0.1 to 37.8 inches | Diameter at breast height (DBH) |
| HEIGHT | REAL | Tree height | 6 to 135 feet | Total tree height |
| CROWN_RATIO | REAL | Crown ratio | 1% to 99% | Live crown to total height ratio |
| CROWN_CLASS | REAL | Crown class | 0 to 5 | Tree crown position |
| TREE_COUNT | REAL | Number of trees | 0.52 to 100.11 | Trees represented by this record |

### Growth Table

Contains growth and mortality measurements for each tree.

| Variable | Type | Description | Range/Units | Notes |
|----------|------|-------------|-------------|--------|
| TREE_CN | TEXT | Tree identifier | - | Foreign key to trees table |
| GROWTH_RATE | REAL | Annual growth rate | 2.75 to 91.68 | Annual diameter growth |
| REMOVAL_RATE | REAL | Removal rate | - | Rate of tree removals |
| MORTALITY_RATE | REAL | Mortality rate | - | Rate of tree mortality |

## Views

### Complete Tree Data View

Combines all tables for comprehensive analysis. Includes all columns from stands, trees, and growth tables.

Key statistics:
- Total records: 724,333
- Average diameter: 9.31 inches
- Average height: 61.57 feet
- Average growth rate: 6.13 units/year

### Stand Summary View

Provides aggregated statistics for each stand.

| Variable | Type | Description | Range/Units | Notes |
|----------|------|-------------|-------------|--------|
| STAND_CN | TEXT | Stand identifier | - | Primary key |
| LATITUDE | REAL | Stand latitude | 30.75° to 33.02°N | Location |
| LONGITUDE | REAL | Stand longitude | -81.92° to -81.05° | Location |
| ELEVATION | TEXT | Stand elevation | - | Elevation |
| SLOPE | REAL | Terrain slope | 0° to 35° | Steepness |
| ASPECT | REAL | Slope aspect | 0° to 360° | Direction |
| SITE_INDEX | REAL | Site productivity | 52 to 154 | Site quality |
| tree_count | INTEGER | Trees in stand | 1 to 3,895 | Total trees per stand |
| avg_diameter | REAL | Mean diameter | 0.1 to 33 inches | Average DBH |
| avg_height | REAL | Mean height | 7 to 132.5 feet | Average height |
| avg_growth_rate | REAL | Mean growth | 2.75 to 60 | Average annual growth |

## Additional Information

### Crown Class Codes
- 0: Unknown
- 1: Open grown
- 2: Dominant
- 3: Co-dominant
- 4: Intermediate
- 5: Overtopped

### Species Codes
Common species in the database:
- 131: Loblolly Pine
- 121: Longleaf Pine
- 110: Shortleaf Pine
- 132: Virginia Pine
- 611: Water Oak
- 812: Yellow Poplar
- 694: Sweetgum

### Data Coverage
- Geographic: Coastal Georgia counties
- Species focus: Primarily Loblolly Pine
- Time period: Single measurement
- Sample size: 1,901 stands, 116,829 trees

### Relationships
- Each stand (STAND_CN) can have multiple trees
- Each tree (TREE_CN) has one growth record
- All measurements are linked through STAND_CN and TREE_CN 
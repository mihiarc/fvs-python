# Database Schema

The FVS-Python project uses a SQLite database to store species data, growth coefficients, and other parameters needed for forest growth modeling. This document describes the database structure and relationships.

## Tables Overview

### Species Table
```sql
CREATE TABLE species (
    species_code TEXT PRIMARY KEY NOT NULL
);
```
Primary table containing species codes.

### Site Index Groups Table
```sql
CREATE TABLE site_index_groups (
    site_index_species TEXT PRIMARY KEY NOT NULL,
    mapped_species TEXT NOT NULL,
    site_type TEXT NOT NULL,
    a REAL NOT NULL,
    b REAL NOT NULL,
    c REAL NOT NULL,
    d REAL NOT NULL
);
```
Contains site index group definitions and their coefficients.

### Site Index Range Table
```sql
CREATE TABLE site_index_range (
    species_code TEXT PRIMARY KEY NOT NULL,
    si_min REAL NOT NULL,
    si_max REAL NOT NULL,
    dbw REAL NOT NULL
);
```
Contains site index ranges and diameter-bark-width ratios for each species.

### Bark Thickness Table
```sql
CREATE TABLE bark_thickness (
    species_code TEXT PRIMARY KEY NOT NULL,
    bark_b0 REAL NOT NULL,
    bark_b1 REAL NOT NULL
);
```
Contains bark thickness coefficients for each species.

### Wykoff Functions Table
```sql
CREATE TABLE wykoff_functions (
    species_code TEXT PRIMARY KEY NOT NULL,
    wykoffoff_b0 REAL NOT NULL,
    wykoffoff_b1 REAL NOT NULL
);
```
Contains Wykoff height-diameter relationship coefficients.

### Curtis-Arney Functions Table
```sql
CREATE TABLE curtis_arney_functions (
    species_code TEXT PRIMARY KEY NOT NULL,
    dbw REAL NOT NULL,
    curtis_arneyarney_b0 REAL NOT NULL,
    curtis_arneyarney_b1 REAL NOT NULL,
    curtis_arneyarney_b2 REAL NOT NULL
);
```
Contains Curtis-Arney height-diameter relationship coefficients.

### Large Tree Growth Table
```sql
CREATE TABLE large_tree_growth (
    species_code TEXT PRIMARY KEY NOT NULL,
    large_tree_b0 REAL NOT NULL,
    large_tree_b1 REAL NOT NULL,
    large_tree_b2 REAL NOT NULL,
    large_tree_b3 REAL NOT NULL,
    large_tree_b4 REAL NOT NULL,
    large_tree_b5 REAL NOT NULL,
    large_tree_b6 REAL NOT NULL,
    large_tree_b7 REAL NOT NULL,
    large_tree_b8 REAL NOT NULL,
    large_tree_b9 REAL NOT NULL,
    large_tree_b10 REAL NOT NULL
);
```
Contains growth model coefficients for large trees.

### Small Tree Growth Table
```sql
CREATE TABLE small_tree_growth (
    species_code TEXT PRIMARY KEY NOT NULL,
    small_tree_b0 REAL NOT NULL,
    small_tree_b1 REAL NOT NULL,
    small_tree_b2 REAL NOT NULL,
    small_tree_b3 REAL NOT NULL,
    small_tree_b4 REAL NOT NULL
);
```
Contains growth model coefficients for small trees.

### Forest Types Table
```sql
CREATE TABLE forest_types (
    fia_fortypcd INTEGER NOT NULL,
    fvs_fortypcd TEXT NOT NULL,
    fvs_fortypcd_name TEXT NOT NULL,
    PRIMARY KEY (fia_fortypcd, fvs_fortypcd)
);
```
Defines forest type classifications and their mappings between FIA and FVS codes.

### Ecological Units Table
```sql
CREATE TABLE ecological_units (
    fvs_ecounit TEXT PRIMARY KEY NOT NULL,
    fvspy_ecounit INTEGER NOT NULL
);
```
Defines ecological unit classifications.

### Ecological Coefficients Table
```sql
CREATE TABLE ecological_coefficients (
    fvs_spcd TEXT NOT NULL,
    fvspy_base_ecounit TEXT NOT NULL,
    ecounit_m221 REAL NOT NULL,
    ecounit_m222 REAL NOT NULL,
    ecounit_t231 REAL NOT NULL,
    ecounit_221 REAL NOT NULL,
    ecounit_222 REAL NOT NULL,
    ecounit_231t REAL NOT NULL,
    ecounit_231l REAL NOT NULL,
    ecounit_232 REAL NOT NULL,
    ecounit_234 REAL NOT NULL,
    ecounit_255 REAL NOT NULL,
    ecounit_411 REAL NOT NULL,
    PRIMARY KEY (fvs_spcd, fvspy_base_ecounit)
);
```
Contains coefficients for ecological unit calculations.

### Species Crown Ratio Table
```sql
CREATE TABLE species_crown_ratio (
    species_code TEXT PRIMARY KEY NOT NULL,
    acr_equation_number INTEGER NOT NULL,
    a REAL NOT NULL,
    b0 REAL NOT NULL,
    b1 REAL NOT NULL,
    c REAL NOT NULL,
    d0 REAL NOT NULL,
    d1 REAL NOT NULL,
    d2 REAL NOT NULL,
    crown_width REAL NOT NULL
);
```
Contains coefficients for calculating Actual Crown Ratio (ACR) and crown width for each species. The `acr_equation_number` field specifies which equation variant to use for ACR calculations.

## Indexes

The following indexes are created for better query performance:

```sql
CREATE INDEX idx_forest_types_fia ON forest_types(fia_fortypcd);
CREATE INDEX idx_forest_types_fvs ON forest_types(fvs_fortypcd);
CREATE INDEX idx_ecological_coefficients_ecounit ON ecological_coefficients(fvspy_base_ecounit);
```

## Data Organization

The database is organized to support the following key aspects of forest growth modeling:

1. **Species Information**: Basic species data and codes
2. **Site Index**: Site index groups, ranges, and coefficients
3. **Tree Measurements**: 
   - Bark thickness coefficients
   - Height-diameter relationships (Wykoff and Curtis-Arney functions)
4. **Growth Models**:
   - Small tree growth coefficients
   - Large tree growth coefficients
5. **Forest Classification**:
   - Forest types (FIA and FVS mappings)
   - Ecological units and coefficients
6. **Crown Modeling**: Crown ratio and width coefficients

## Usage Notes

1. Species codes are used as primary keys in most tables, ensuring data consistency
2. Forest types have a composite primary key of FIA and FVS codes
3. Ecological coefficients use a composite key of species code and base ecological unit
4. All coefficient tables use REAL data type for precision in calculations
5. Text fields are used for codes and names to maintain readability 
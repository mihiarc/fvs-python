# Database Schema

The FVS-Python project uses a SQLite database to store species data, growth coefficients, and other parameters needed for forest growth modeling. This document describes the database structure and relationships.

## Tables Overview

### Species Table
```sql
CREATE TABLE species (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    FIA_code INTEGER NOT NULL
);
```
Primary table containing species information and FIA codes. Species codes are limited to 2 characters.

### Height-Diameter Coefficients Table
```sql
CREATE TABLE height_diameter_coefficients (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    CurtisArney_b0 NUMERIC NOT NULL,
    CurtisArney_b1 NUMERIC NOT NULL,
    CurtisArney_b2 NUMERIC NOT NULL,
    Wykoff_b0 NUMERIC NOT NULL,
    Wykoff_b1 NUMERIC NOT NULL,
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);
```
Contains coefficients for height-diameter relationships using both Curtis-Arney and Wykoff equations.

### Small Tree Coefficients Table
```sql
CREATE TABLE small_tree_coefficients (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    b0 NUMERIC NOT NULL,
    b1 NUMERIC NOT NULL,
    b2 NUMERIC NOT NULL,
    b3 NUMERIC NOT NULL,
    b4 NUMERIC NOT NULL,
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);
```
Contains growth model coefficients specifically for small trees (DBH < 3.0 inches).

### Large Tree Coefficients Table
```sql
CREATE TABLE large_tree_coefficients (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    b0 NUMERIC NOT NULL,
    b1 NUMERIC NOT NULL,
    b2 NUMERIC NOT NULL,
    b3 NUMERIC NOT NULL,
    b4 NUMERIC NOT NULL,
    b5 NUMERIC NOT NULL,
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);
```
Contains growth model coefficients specifically for large trees (DBH >= 3.0 inches).

### Species Parameters Table
```sql
CREATE TABLE species_parameters (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    si_min INTEGER NOT NULL,
    si_max INTEGER NOT NULL,
    dbh_min NUMERIC NOT NULL DEFAULT 1.0,  -- Minimum DBH for growth calculations
    dbh_max NUMERIC NOT NULL DEFAULT 40.0, -- Maximum DBH for growth calculations
    growth_transition_dbh_min NUMERIC NOT NULL DEFAULT 3.0,  -- DBH threshold for small to large tree transition start
    growth_transition_dbh_max NUMERIC NOT NULL DEFAULT 6.0,  -- DBH threshold for small to large tree transition end
    Dbw NUMERIC NOT NULL,  -- Diameter at breast height and bark width ratio
    Bark_b0 NUMERIC NOT NULL, -- Bark ratio coefficient 0
    Bark_b1 NUMERIC NOT NULL, -- Bark ratio coefficient 1
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);
```
Contains species-specific parameters including:
- Site index ranges (si_min, si_max)
- DBH limits for growth calculations (dbh_min, dbh_max)
- Growth model transition thresholds (growth_transition_dbh_min, growth_transition_dbh_max)
- Bark ratio parameters (Dbw, Bark_b0, Bark_b1)

Default values are provided for DBH-related parameters to ensure consistent behavior.

### Forest Types Table
```sql
CREATE TABLE forest_types (
    fvs_fortypcd TEXT(6) PRIMARY KEY NOT NULL,
    fvs_fortypcd_name TEXT(50) NOT NULL,
    fia_fortypcd INTEGER NOT NULL
);
```
Defines forest type classifications. Forest type codes are limited to 6 characters, and names are limited to 50 characters.

### Ecological Units Table
```sql
CREATE TABLE ecological_units (
    fvs_ecounit TEXT(4) PRIMARY KEY NOT NULL,
    fvspy_ecounit INTEGER NOT NULL
);
```
Defines ecological unit classifications. Ecological unit codes are limited to 4 characters.

### Ecological Coefficients Tables

The ecological coefficients are split into two tables to separate base coefficients from species-specific adjustments:

```sql
-- Base coefficients for ecological units
CREATE TABLE ecological_coefficients (
    fvs_ecounit TEXT(4) PRIMARY KEY NOT NULL,
    base_b0 NUMERIC NOT NULL DEFAULT 0.0,
    base_b1 NUMERIC NOT NULL DEFAULT 0.0,
    -- ... (b2 through b11)
    FOREIGN KEY (fvs_ecounit) REFERENCES ecological_units(fvs_ecounit)
);

-- Species-specific adjustments
CREATE TABLE ecological_species_adjustments (
    species_code TEXT(2) NOT NULL,
    fvs_ecounit TEXT(4) NOT NULL,
    adjustment_b0 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b1 NUMERIC NOT NULL DEFAULT 0.0,
    -- ... (b2 through b11)
    PRIMARY KEY (species_code, fvs_ecounit),
    FOREIGN KEY (species_code) REFERENCES species(species_code),
    FOREIGN KEY (fvs_ecounit) REFERENCES ecological_units(fvs_ecounit)
);
```

This structure allows for:
- Base coefficients that apply to all species within an ecological unit
- Species-specific adjustments that modify the base coefficients
- Default values of 0.0 for adjustments, meaning no modification to base coefficients
- Reduced data redundancy when coefficients are similar across species

### Forest Type Coefficients Tables

Similarly, forest type coefficients are split into base coefficients and species-specific adjustments:

```sql
-- Base coefficients for forest types
CREATE TABLE forest_type_coefficients (
    fvs_fortypcd TEXT(6) PRIMARY KEY NOT NULL,
    base_lohd NUMERIC NOT NULL DEFAULT 0.0,
    base_nohd NUMERIC NOT NULL DEFAULT 0.0,
    -- ... (other coefficients)
    FOREIGN KEY (fvs_fortypcd) REFERENCES forest_types(fvs_fortypcd)
);

-- Species-specific adjustments
CREATE TABLE forest_type_species_adjustments (
    species_code TEXT(2) NOT NULL,
    fvs_fortypcd TEXT(6) NOT NULL,
    adjustment_lohd NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_nohd NUMERIC NOT NULL DEFAULT 0.0,
    -- ... (other adjustments)
    PRIMARY KEY (species_code, fvs_fortypcd),
    FOREIGN KEY (species_code) REFERENCES species(species_code),
    FOREIGN KEY (fvs_fortypcd) REFERENCES forest_types(fvs_fortypcd)
);
```

Benefits of this structure:
- Base coefficients capture the general characteristics of each forest type
- Species-specific adjustments allow fine-tuning for individual species
- Default values of 0.0 for adjustments maintain base coefficients when no adjustment is needed
- Reduced redundancy in coefficient storage

### Crown Ratio Coefficients Table
```sql
CREATE TABLE crown_ratio_coefficients (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    acr_equation_type INTEGER NOT NULL,  -- Identifier for which ACR equation to use (1, 2, etc.)
    a NUMERIC NOT NULL,   -- Asymptote parameter
    b0 NUMERIC NOT NULL,  -- Intercept parameter
    b1 NUMERIC NOT NULL,  -- Slope parameter
    c NUMERIC NOT NULL,   -- Shape parameter
    d0 NUMERIC NOT NULL,  -- Competition intercept
    d1 NUMERIC NOT NULL,  -- Competition slope 1
    d2 NUMERIC NOT NULL,  -- Competition slope 2
    sd NUMERIC NOT NULL,  -- Standard deviation
    Xmin NUMERIC NOT NULL, -- Minimum value for X
    Xmax NUMERIC NOT NULL, -- Maximum value for X
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);
```
Contains coefficients for calculating Actual Crown Ratio (ACR) for each species. The table includes:
- `acr_equation_type`: Specifies which ACR equation to use for the species (1, 2, etc.)
- Equation parameters:
  - `a`: Asymptote parameter
  - `b0`, `b1`: Intercept and slope parameters
  - `c`: Shape parameter
  - `d0`, `d1`, `d2`: Competition parameters
  - `sd`: Standard deviation
  - `Xmin`, `Xmax`: Valid range for input values

## Data Type Choices

- `TEXT(n)`: Used for fixed-length string fields with a maximum length of n characters
- `INTEGER`: Used for whole number values (e.g., FIA codes, site index values)
- `NUMERIC`: Used for decimal values that require exact precision (coefficients and scaling factors)

## Growth Model Organization

The growth coefficients have been split into three separate tables to better organize the different aspects of tree growth modeling:

1. `height_diameter_coefficients`: Contains parameters for height-diameter relationships
2. `small_tree_coefficients`: Specific to growth modeling of trees with DBH < growth_transition_dbh_min
3. `large_tree_coefficients`: Specific to growth modeling of trees with DBH >= growth_transition_dbh_max

Growth model transitions are controlled by parameters in the `species_parameters` table:
- Trees with DBH < growth_transition_dbh_min use only small tree growth equations
- Trees with DBH > growth_transition_dbh_max use only large tree growth equations
- Trees with DBH between these values use a weighted blend of both equations

## Relationships

- All tables with `species_code` have a foreign key relationship to the `species` table
- Ecological and forest type tables use a two-level structure:
  1. Base coefficients linked to their respective unit/type
  2. Species-specific adjustments linked to both species and unit/type

## Indexes

The following indexes are created for better query performance:

```sql
CREATE INDEX idx_species_fia ON species(FIA_code);
CREATE INDEX idx_forest_types_fia ON forest_types(fia_fortypcd);
CREATE INDEX idx_ecological_species_adjustments_ecounit ON ecological_species_adjustments(fvs_ecounit);
CREATE INDEX idx_forest_type_species_adjustments_fortypcd ON forest_type_species_adjustments(fvs_fortypcd);
``` 
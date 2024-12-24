# Database Schema

The FVS-Python project uses a SQLite database to store species data, growth coefficients, and other parameters needed for forest growth modeling. This document describes the database structure and relationships.

## Tables Overview

### Species Table
```sql
CREATE TABLE species (
    species_code TEXT PRIMARY KEY NOT NULL,
    FIA_code INTEGER NOT NULL
);
```
Primary table containing species information and FIA codes.

### Growth Coefficients Table
```sql
CREATE TABLE growth_coefficients (
    species_code TEXT PRIMARY KEY NOT NULL,
    CurtisArney_b0 REAL NOT NULL,
    CurtisArney_b1 REAL NOT NULL,
    CurtisArney_b2 REAL NOT NULL,
    Wykoff_b0 REAL NOT NULL,
    Wykoff_b1 REAL NOT NULL,
    small_tree_b0 REAL NOT NULL,
    small_tree_b1 REAL NOT NULL,
    small_tree_b2 REAL NOT NULL,
    small_tree_b3 REAL NOT NULL,
    small_tree_b4 REAL NOT NULL,
    ln_dds_b0 REAL NOT NULL,
    ln_dds_b1 REAL NOT NULL,
    ln_dds_b2 REAL NOT NULL,
    ln_dds_b3 REAL NOT NULL,
    ln_dds_b4 REAL NOT NULL,
    ln_dds_b5 REAL NOT NULL,
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);
```
Contains growth model coefficients for each species.

### Species Scaling Factors Table
```sql
CREATE TABLE species_scaling_factors (
    species_code TEXT PRIMARY KEY NOT NULL,
    si_min REAL NOT NULL,
    si_max REAL NOT NULL,
    Dbw REAL NOT NULL,
    Bark_b0 REAL NOT NULL,
    Bark_b1 REAL NOT NULL,
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);
```
Contains scaling factors used in various calculations.

### Forest Types Table
```sql
CREATE TABLE forest_types (
    fvs_fortypcd TEXT PRIMARY KEY NOT NULL,
    fvs_fortypcd_name TEXT NOT NULL,
    fia_fortypcd INTEGER NOT NULL
);
```
Defines forest type classifications.

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
    species_code TEXT NOT NULL,
    fvs_ecounit TEXT NOT NULL,
    ecounit_b0 REAL NOT NULL,
    ecounit_b1 REAL NOT NULL,
    ecounit_b2 REAL NOT NULL,
    ecounit_b3 REAL NOT NULL,
    ecounit_b4 REAL NOT NULL,
    ecounit_b5 REAL NOT NULL,
    ecounit_b6 REAL NOT NULL,
    ecounit_b7 REAL NOT NULL,
    ecounit_b8 REAL NOT NULL,
    ecounit_b9 REAL NOT NULL,
    ecounit_b10 REAL NOT NULL,
    ecounit_b11 REAL NOT NULL,
    PRIMARY KEY (species_code, fvs_ecounit),
    FOREIGN KEY (species_code) REFERENCES species(species_code),
    FOREIGN KEY (fvs_ecounit) REFERENCES ecological_units(fvs_ecounit)
);
```
Contains coefficients for ecological unit calculations.

### Forest Type Coefficients Table
```sql
CREATE TABLE forest_type_coefficients (
    species_code TEXT NOT NULL,
    fvs_fortypcd TEXT NOT NULL,
    ftlohd REAL NOT NULL,
    ftnohd REAL NOT NULL,
    ftokpn REAL NOT NULL,
    ftsfhp REAL NOT NULL,
    ftuphd REAL NOT NULL,
    ftupok REAL NOT NULL,
    ftylpn REAL NOT NULL,
    PRIMARY KEY (species_code, fvs_fortypcd),
    FOREIGN KEY (species_code) REFERENCES species(species_code),
    FOREIGN KEY (fvs_fortypcd) REFERENCES forest_types(fvs_fortypcd)
);
```
Contains coefficients for forest type calculations.

## Relationships

- All tables with `species_code` have a foreign key relationship to the `species` table
- `ecological_coefficients` links species to ecological units
- `forest_type_coefficients` links species to forest types

## Indexes

The following indexes are created for better query performance:

```sql
CREATE INDEX idx_species_fia ON species(FIA_code);
CREATE INDEX idx_forest_types_fia ON forest_types(fia_fortypcd);
CREATE INDEX idx_ecological_coefficients_ecounit ON ecological_coefficients(fvs_ecounit);
CREATE INDEX idx_forest_type_coefficients_fortypcd ON forest_type_coefficients(fvs_fortypcd);
``` 
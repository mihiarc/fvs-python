-- Drop existing tables if they exist
DROP TABLE IF EXISTS forest_type_coefficients;
DROP TABLE IF EXISTS ecological_coefficients;
DROP TABLE IF EXISTS site_index_groups;
DROP TABLE IF EXISTS site_index_range;
DROP TABLE IF EXISTS bark_thickness;
DROP TABLE IF EXISTS wykoff_functions;
DROP TABLE IF EXISTS curtis_arney_functions;
DROP TABLE IF EXISTS large_tree_growth;
DROP TABLE IF EXISTS small_tree_growth;
DROP TABLE IF EXISTS forest_types;
DROP TABLE IF EXISTS ecological_units;
DROP TABLE IF EXISTS species_crown_ratio;
DROP TABLE IF EXISTS species;

-- Create tables with proper constraints

CREATE TABLE species (
    species_code TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE site_index_groups (
    site_index_species TEXT PRIMARY KEY NOT NULL,
    mapped_species TEXT NOT NULL,
    site_type TEXT NOT NULL,
    a REAL NOT NULL,
    b REAL NOT NULL,
    c REAL NOT NULL,
    d REAL NOT NULL
);

CREATE TABLE site_index_range (
    species_code TEXT PRIMARY KEY NOT NULL,
    si_min REAL NOT NULL,
    si_max REAL NOT NULL,
    dbw REAL NOT NULL
);

CREATE TABLE bark_thickness (
    species_code TEXT PRIMARY KEY NOT NULL,
    bark_b0 REAL NOT NULL,
    bark_b1 REAL NOT NULL
);

CREATE TABLE wykoff_functions (
    species_code TEXT PRIMARY KEY NOT NULL,
    wykoffoff_b0 REAL NOT NULL,
    wykoffoff_b1 REAL NOT NULL
);

CREATE TABLE curtis_arney_functions (
    species_code TEXT PRIMARY KEY NOT NULL,
    dbw REAL NOT NULL,
    curtis_arneyarney_b0 REAL NOT NULL,
    curtis_arneyarney_b1 REAL NOT NULL,
    curtis_arneyarney_b2 REAL NOT NULL
);

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

CREATE TABLE small_tree_growth (
    species_code TEXT PRIMARY KEY NOT NULL,
    small_tree_b0 REAL NOT NULL,
    small_tree_b1 REAL NOT NULL,
    small_tree_b2 REAL NOT NULL,
    small_tree_b3 REAL NOT NULL,
    small_tree_b4 REAL NOT NULL
);

CREATE TABLE forest_types (
    fia_fortypcd INTEGER NOT NULL,
    fvs_fortypcd TEXT NOT NULL,
    fvs_fortypcd_name TEXT NOT NULL,
    PRIMARY KEY (fia_fortypcd, fvs_fortypcd)
);

CREATE TABLE ecological_units (
    fvs_ecounit TEXT PRIMARY KEY NOT NULL,
    fvspy_ecounit INTEGER NOT NULL
);

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

CREATE TABLE species_crown_ratio (
    species_code TEXT PRIMARY KEY NOT NULL,
    a REAL NOT NULL,
    b0 REAL NOT NULL,
    b1 REAL NOT NULL,
    c REAL NOT NULL,
    d0 REAL NOT NULL,
    d1 REAL NOT NULL,
    d2 REAL NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_forest_types_fia ON forest_types(fia_fortypcd);
CREATE INDEX idx_forest_types_fvs ON forest_types(fvs_fortypcd);
CREATE INDEX idx_ecological_coefficients_ecounit ON ecological_coefficients(fvspy_base_ecounit); 
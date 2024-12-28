-- Drop existing tables if they exist
DROP TABLE IF EXISTS crown_width_forest_grown;
DROP TABLE IF EXISTS crown_width_open_grown;
DROP TABLE IF EXISTS diameter_bounding_limits;
DROP TABLE IF EXISTS planted_coefficients;
DROP TABLE IF EXISTS shade_tolerance_by_species;
DROP TABLE IF EXISTS shade_tolerance_coefficients;

-- Create forest grown crown width table
CREATE TABLE crown_width_forest_grown (
    species_code TEXT PRIMARY KEY NOT NULL,
    fia_spcd INTEGER NOT NULL,
    equation_number INTEGER NOT NULL,
    a1 REAL NOT NULL,
    a2 REAL NOT NULL,
    a3 REAL,
    a4 REAL,
    a5 REAL,
    dbh_bound REAL,
    fcw_bound REAL
);

-- Create open grown crown width table
CREATE TABLE crown_width_open_grown (
    species_code TEXT PRIMARY KEY NOT NULL,
    fia_spcd INTEGER NOT NULL,
    equation_number INTEGER NOT NULL,
    a1 REAL NOT NULL,
    a2 REAL NOT NULL,
    a3 REAL,
    a4 REAL,
    a5 REAL,
    dbh_bound REAL,
    ocw_bound REAL
);

-- Create diameter bounding limits table
CREATE TABLE diameter_bounding_limits (
    species_code TEXT PRIMARY KEY NOT NULL,
    dbh_low REAL NOT NULL,
    dbh_high REAL NOT NULL
);

-- Create planted coefficients table
CREATE TABLE planted_coefficients (
    species_code TEXT PRIMARY KEY NOT NULL,
    plant_coefficient REAL NOT NULL
);

-- Create shade tolerance by species table
CREATE TABLE shade_tolerance_by_species (
    species_code TEXT PRIMARY KEY NOT NULL,
    shade_tolerance TEXT NOT NULL,
    FOREIGN KEY (shade_tolerance) REFERENCES shade_tolerance_coefficients(shade_tolerance)
);

-- Create shade tolerance coefficients table
CREATE TABLE shade_tolerance_coefficients (
    shade_tolerance TEXT PRIMARY KEY NOT NULL,
    rhr REAL NOT NULL,
    rhyxs REAL NOT NULL,
    rhm REAL NOT NULL,
    rhb REAL NOT NULL,
    rhxs REAL NOT NULL,
    rhk REAL NOT NULL
); 
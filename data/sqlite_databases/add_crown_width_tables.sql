-- Drop existing tables if they exist
DROP TABLE IF EXISTS crown_width_forest_grown;
DROP TABLE IF EXISTS crown_width_open_grown;

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
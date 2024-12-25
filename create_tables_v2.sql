-- Drop existing tables if they exist
DROP TABLE IF EXISTS forest_type_species_adjustments;
DROP TABLE IF EXISTS forest_type_coefficients;
DROP TABLE IF EXISTS ecological_species_adjustments;
DROP TABLE IF EXISTS ecological_coefficients;
DROP TABLE IF EXISTS species_parameters;
DROP TABLE IF EXISTS large_tree_coefficients;
DROP TABLE IF EXISTS small_tree_coefficients;
DROP TABLE IF EXISTS height_diameter_coefficients;
DROP TABLE IF EXISTS crown_ratio_coefficients;
DROP TABLE IF EXISTS forest_types;
DROP TABLE IF EXISTS ecological_units;
DROP TABLE IF EXISTS species;

-- Create tables with proper constraints

CREATE TABLE species (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    FIA_code INTEGER NOT NULL
);

CREATE TABLE height_diameter_coefficients (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    CurtisArney_b0 NUMERIC NOT NULL,
    CurtisArney_b1 NUMERIC NOT NULL,
    CurtisArney_b2 NUMERIC NOT NULL,
    Wykoff_b0 NUMERIC NOT NULL,
    Wykoff_b1 NUMERIC NOT NULL,
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);

CREATE TABLE small_tree_coefficients (
    species_code TEXT(2) PRIMARY KEY NOT NULL,
    b0 NUMERIC NOT NULL,
    b1 NUMERIC NOT NULL,
    b2 NUMERIC NOT NULL,
    b3 NUMERIC NOT NULL,
    b4 NUMERIC NOT NULL,
    FOREIGN KEY (species_code) REFERENCES species(species_code)
);

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

CREATE TABLE forest_types (
    fvs_fortypcd TEXT(6) PRIMARY KEY NOT NULL,
    fvs_fortypcd_name TEXT(50) NOT NULL,
    fia_fortypcd INTEGER NOT NULL
);

CREATE TABLE ecological_units (
    fvs_ecounit TEXT(4) PRIMARY KEY NOT NULL,
    fvspy_ecounit INTEGER NOT NULL
);

-- Base coefficients for ecological units
CREATE TABLE ecological_coefficients (
    fvs_ecounit TEXT(4) PRIMARY KEY NOT NULL,
    base_b0 NUMERIC NOT NULL DEFAULT 0.0,
    base_b1 NUMERIC NOT NULL DEFAULT 0.0,
    base_b2 NUMERIC NOT NULL DEFAULT 0.0,
    base_b3 NUMERIC NOT NULL DEFAULT 0.0,
    base_b4 NUMERIC NOT NULL DEFAULT 0.0,
    base_b5 NUMERIC NOT NULL DEFAULT 0.0,
    base_b6 NUMERIC NOT NULL DEFAULT 0.0,
    base_b7 NUMERIC NOT NULL DEFAULT 0.0,
    base_b8 NUMERIC NOT NULL DEFAULT 0.0,
    base_b9 NUMERIC NOT NULL DEFAULT 0.0,
    base_b10 NUMERIC NOT NULL DEFAULT 0.0,
    base_b11 NUMERIC NOT NULL DEFAULT 0.0,
    FOREIGN KEY (fvs_ecounit) REFERENCES ecological_units(fvs_ecounit)
);

-- Species-specific adjustments to ecological coefficients
CREATE TABLE ecological_species_adjustments (
    species_code TEXT(2) NOT NULL,
    fvs_ecounit TEXT(4) NOT NULL,
    adjustment_b0 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b1 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b2 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b3 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b4 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b5 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b6 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b7 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b8 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b9 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b10 NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_b11 NUMERIC NOT NULL DEFAULT 0.0,
    PRIMARY KEY (species_code, fvs_ecounit),
    FOREIGN KEY (species_code) REFERENCES species(species_code),
    FOREIGN KEY (fvs_ecounit) REFERENCES ecological_units(fvs_ecounit)
);

-- Base coefficients for forest types
CREATE TABLE forest_type_coefficients (
    fvs_fortypcd TEXT(6) PRIMARY KEY NOT NULL,
    base_lohd NUMERIC NOT NULL DEFAULT 0.0,
    base_nohd NUMERIC NOT NULL DEFAULT 0.0,
    base_okpn NUMERIC NOT NULL DEFAULT 0.0,
    base_sfhp NUMERIC NOT NULL DEFAULT 0.0,
    base_uphd NUMERIC NOT NULL DEFAULT 0.0,
    base_upok NUMERIC NOT NULL DEFAULT 0.0,
    base_ylpn NUMERIC NOT NULL DEFAULT 0.0,
    FOREIGN KEY (fvs_fortypcd) REFERENCES forest_types(fvs_fortypcd)
);

-- Species-specific adjustments to forest type coefficients
CREATE TABLE forest_type_species_adjustments (
    species_code TEXT(2) NOT NULL,
    fvs_fortypcd TEXT(6) NOT NULL,
    adjustment_lohd NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_nohd NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_okpn NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_sfhp NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_uphd NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_upok NUMERIC NOT NULL DEFAULT 0.0,
    adjustment_ylpn NUMERIC NOT NULL DEFAULT 0.0,
    PRIMARY KEY (species_code, fvs_fortypcd),
    FOREIGN KEY (species_code) REFERENCES species(species_code),
    FOREIGN KEY (fvs_fortypcd) REFERENCES forest_types(fvs_fortypcd)
);

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

-- Create indexes for better query performance
CREATE INDEX idx_species_fia ON species(FIA_code);
CREATE INDEX idx_forest_types_fia ON forest_types(fia_fortypcd);
CREATE INDEX idx_ecological_species_adjustments_ecounit ON ecological_species_adjustments(fvs_ecounit);
CREATE INDEX idx_forest_type_species_adjustments_fortypcd ON forest_type_species_adjustments(fvs_fortypcd); 
-- Drop existing tables if they exist
DROP TABLE IF EXISTS competition_coefficients;
DROP TABLE IF EXISTS crown_competition_coefficients;

-- Create competition coefficients table
CREATE TABLE competition_coefficients (
    species_code TEXT PRIMARY KEY NOT NULL,
    ccf_min REAL NOT NULL DEFAULT 0.0,  -- Minimum CCF for competition effects
    ccf_max REAL NOT NULL DEFAULT 200.0, -- Maximum CCF for competition effects
    pccf_min REAL NOT NULL DEFAULT 0.0,  -- Minimum PCCF for competition effects
    pccf_max REAL NOT NULL DEFAULT 100.0, -- Maximum PCCF for competition effects
    density_scale_factor REAL NOT NULL DEFAULT 0.00167, -- Factor for density-dependent scaling
    density_min_scale REAL NOT NULL DEFAULT 0.3,  -- Minimum density scale
    density_max_scale REAL NOT NULL DEFAULT 1.0,  -- Maximum density scale
    point_effect_min REAL NOT NULL DEFAULT 0.3,   -- Minimum point competition effect
    point_effect_max REAL NOT NULL DEFAULT 1.0    -- Maximum point competition effect
);

-- Create crown competition coefficients table
CREATE TABLE crown_competition_coefficients (
    species_code TEXT PRIMARY KEY NOT NULL,
    crown_ratio_weight REAL NOT NULL DEFAULT 0.25,  -- Weight for crown ratio modifier (0-1)
    height_ratio_weight REAL NOT NULL DEFAULT 0.75, -- Weight for height ratio modifier (0-1)
    crown_ratio_min REAL NOT NULL DEFAULT 0.0,      -- Minimum crown ratio for modifier
    crown_ratio_max REAL NOT NULL DEFAULT 1.0,      -- Maximum crown ratio for modifier
    height_ratio_min REAL NOT NULL DEFAULT 0.0,     -- Minimum height ratio for modifier
    height_ratio_max REAL NOT NULL DEFAULT 1.0      -- Maximum height ratio for modifier
);

-- Insert default competition coefficients for all species
INSERT INTO competition_coefficients (species_code)
SELECT species_code FROM species;

-- Insert default crown competition coefficients for all species
INSERT INTO crown_competition_coefficients (species_code)
SELECT species_code FROM species; 
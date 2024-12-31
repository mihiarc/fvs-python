-- Create species mapping table
CREATE TABLE IF NOT EXISTS species_mapping (
    species_code TEXT PRIMARY KEY NOT NULL,
    fia_spcd TEXT NOT NULL
);

-- Insert mappings from crown width tables
INSERT INTO species_mapping (species_code, fia_spcd)
SELECT DISTINCT species_code, fia_spcd 
FROM crown_width_forest_grown; 
-- Add ecological unit mappings
CREATE TABLE IF NOT EXISTS ecological_units (
    fvs_ecounit TEXT PRIMARY KEY NOT NULL,
    fvspy_ecounit INTEGER NOT NULL
);

INSERT INTO ecological_units (fvs_ecounit, fvspy_ecounit) VALUES
    ('M221', 1),
    ('M222', 2),
    ('M231', 3),
    ('221', 4),
    ('222', 5),
    ('232', 6),
    ('234', 7),
    ('255', 8),
    ('411', 9),
    ('231T', 10),
    ('231L', 11);

-- Add ecological coefficients
CREATE TABLE IF NOT EXISTS ecological_coefficients (
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

-- Insert coefficients for our main species
INSERT INTO ecological_coefficients (
    fvs_spcd, fvspy_base_ecounit, 
    ecounit_m221, ecounit_m222, ecounit_t231, ecounit_221, ecounit_222,
    ecounit_231t, ecounit_231l, ecounit_232, ecounit_234, ecounit_255, ecounit_411
) VALUES
    -- Loblolly Pine (LP)
    ('131', '6', -0.069716, 0.581967, 0.790149, -0.584818, -0.364073, -0.183317, 0.256273, 1e-06, 0.28179, 0.274618, 1e-06),
    -- Shortleaf Pine (SP)
    ('110', '11', -0.569409, -0.252741, -0.265699, -0.694484, -0.285112, -0.504565, 1e-06, -0.113258, 0.114097, 0.092458, 1e-06),
    -- Longleaf Pine (LL)
    ('121', '6', 1e-06, 1e-06, 1e-06, 1e-06, 1e-06, -0.175073, -0.067793, 1e-06, 0.123262, 1e-06, 1e-06),
    -- Slash Pine (SA)
    ('111', '6', 1e-06, 1e-06, 1e-06, 1e-06, 1e-06, -0.025549, 0.324111, 1e-06, 0.306793, 1e-06, -0.342293); 
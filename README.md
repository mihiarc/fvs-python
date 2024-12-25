# fvs-python

# fvs-southern-python

This project aims to create a Python implementation of the Southern variant of the Forest Vegetation Simulator (FVS). FVS is a widely used growth and yield model for forest management. This project focuses on reimplementing the core growth projection and economic analysis components of the Southern variant in a modular and maintainable Python library.

## Project Goals

*   Reimplement key growth and yield algorithms from the Southern FVS variant in Python.
*   Provide functions for economic analysis, including Net Present Value (NPV), Internal Rate of Return (IRR), and Land Expectation Value (LEV) calculations.
*   Create a well-documented and testable Python library (`fvs_core`) that can be easily integrated into other projects.
*   Maintain the option to expose the functionality as a web API in the future.

## Project Structure

```
fvs-python/
├── fvs_core/          # Core FVS logic
│   ├── growth_models.py
│   ├── data_handling.py
│   ├── db_utils.py
│   └── __init__.py
├── data/              # Raw data files
│   ├── species_data.csv              # Species-specific parameters
│   ├── ecounit_codes.csv            # Ecological unit coefficients
│   ├── base_ecounit_codes.csv       # Base ecological unit definitions
│   ├── forest_type_group_codes.csv  # Forest type definitions
│   └── ln_dds_species_growth_parameters.csv  # Growth parameters
├── tests/             # Unit tests
│   ├── test_db_utils.py
│   └── __init__.py
├── docs/              # Documentation
├── create_tables_v2.sql  # Database schema
├── load_data.py         # Database population script
├── fvspy.db            # SQLite database
├── .gitignore
├── setup.py           # Setup script for the package
├── README.md
├── LICENSE
└── requirements.txt
```

## Data Structure

### Raw Data Files
- `species_data.csv`: Contains species-specific parameters including growth coefficients and scaling factors
- `ecounit_codes.csv`: Contains ecological unit coefficients for different species
- `base_ecounit_codes.csv`: Defines base ecological units and their mappings
- `forest_type_group_codes.csv`: Defines forest type groups and their FIA codes
- `ln_dds_species_growth_parameters.csv`: Contains species-specific growth parameters

### Database Structure (fvspy.db)

The SQLite database contains the following tables:

1. `species`: Primary species information
   - Primary key: species_code

2. `site_index_groups`: Site index group definitions
   - Primary key: site_index_species
   - Fields: mapped_species, site_type, coefficients (a, b, c, d)

3. `site_index_range`: Site index ranges for species
   - Primary key: species_code
   - Fields: si_min, si_max, dbw

4. `bark_thickness`: Bark thickness coefficients
   - Primary key: species_code
   - Fields: bark_b0, bark_b1

5. `wykoff_functions`: Wykoff height-diameter coefficients
   - Primary key: species_code
   - Fields: wykoffoff_b0, wykoffoff_b1

6. `curtis_arney_functions`: Curtis-Arney height-diameter coefficients
   - Primary key: species_code
   - Fields: dbw, curtis_arneyarney_b0, curtis_arneyarney_b1, curtis_arneyarney_b2

7. `large_tree_growth`: Large tree growth coefficients
   - Primary key: species_code
   - Fields: large_tree_b0 through large_tree_b10

8. `small_tree_growth`: Small tree growth coefficients
   - Primary key: species_code
   - Fields: small_tree_b0 through small_tree_b4

9. `forest_types`: Forest type definitions
   - Composite key: (fia_fortypcd, fvs_fortypcd)
   - Fields: fvs_fortypcd_name

10. `ecological_units`: Ecological unit definitions
    - Primary key: fvs_ecounit
    - Fields: fvspy_ecounit

11. `ecological_coefficients`: Coefficients for ecological unit calculations
    - Composite key: (fvs_spcd, fvspy_base_ecounit)
    - Fields: coefficients for each ecological unit (m221, m222, etc.)

12. `species_crown_ratio`: Crown ratio coefficients
    - Primary key: species_code
    - Fields: a, b0, b1, c, d0, d1, d2

The database schema and detailed documentation can be found in `docs/database_schema.md`.

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/mihiarc/fvs-python.git
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # For Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the package:**

    ```bash
    pip install -e .  # Installs the package in editable mode
    ```

5.  **Initialize the database:**

    ```bash
    python load_data.py  # Creates and populates the SQLite database
    ```

## Example Usage

```python
from fvs_core import growth, economics

stand = {...}  # Your stand data (to be defined according to FVS inputs)
projected_stand = growth.project_growth(stand, 20)
cash_flows = [...] # Calculated from projected_stand
npv = economics.calculate_npv(cash_flows, 0.05)
print(f"Net Present Value: {npv}")
```

More detailed examples can be found in the examples/ directory.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.   

## Acknowledgements
This project is based on the Southern variant of the Forest Vegetation Simulator (FVS), developed by the USDA Forest Service.

## Contact
Chris Mihiar
chris.mihiar@gmail.com
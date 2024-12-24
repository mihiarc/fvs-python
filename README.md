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
   - Fields: species_code, FIA_code

2. `growth_coefficients`: Species-specific growth model parameters
   - Primary key: species_code
   - Foreign key reference to species table

3. `species_scaling_factors`: Scaling factors for species calculations
   - Primary key: species_code
   - Foreign key reference to species table

4. `forest_types`: Forest type definitions
   - Primary key: fvs_fortypcd
   - Fields: fvs_fortypcd, fvs_fortypcd_name, fia_fortypcd

5. `ecological_units`: Ecological unit definitions
   - Primary key: fvs_ecounit
   - Fields: fvs_ecounit, fvspy_ecounit

6. `ecological_coefficients`: Coefficients for ecological unit calculations
   - Primary key: (species_code, fvs_ecounit)
   - Foreign key references to species and ecological_units tables

7. `forest_type_coefficients`: Coefficients for forest type calculations
   - Primary key: (species_code, fvs_fortypcd)
   - Foreign key references to species and forest_types tables

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
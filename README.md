# fvs-python

# fvs-southern-python

This project aims to create a Python implementation of the Southern variant of the Forest Vegetation Simulator (FVS). FVS is a widely used growth and yield model for forest management. This project focuses on reimplementing the core growth projection and economic analysis components of the Southern variant in a modular and maintainable Python library.

## Project Goals

*   Reimplement key growth and yield algorithms from the Southern FVS variant in Python.
*   Provide functions for economic analysis, including Net Present Value (NPV), Internal Rate of Return (IRR), and Land Expectation Value (LEV) calculations.
*   Create a well-documented and testable Python library (`fvs_core`) that can be easily integrated into other projects.
*   Maintain the option to expose the functionality as a web API in the future.

## Project Structure

fvs-python/
├── fvs_core/   (Core FVS logic)
│   ├── growth.py
│   ├── economic_analysis.py
│   ├── init.py
|-- examples/   (Example usage scripts)
|   |-- basic_projection.py
|   |-- economic_analysis.py
|-- tests/      (Unit tests)
|   |-- test_growth.py
|   |-- test_economics.py
|   |-- init.py
|-- data/       (Data files)
|   |-- species_data.csv
|   |-- site_index_groups.csv
|-- docs/       (Documentation)
|-- .gitignore
|-- setup.py     (Setup script for the package)
|-- README.md
|-- LICENSE
|-- requirements.txt

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
    pip install . # Installs the package in editable mode
    ```

## Example Usage

```python
from fvs_core import growth, economics

stand = {...}  # Your stand data (to be defined according to FVS inputs)
projected_stand = growth.project_growth(stand, 20)
cash_flows = [...] # Calculated from projected_stand
npv = economics.calculate_npv(cash_flows, 0.05)
print(f"Net Present Value: {npv}")

More detailed examples can be found in the examples/ directory.

Contributing
 Contributions are welcome! Please open an issue or submit a pull request.

License
 This project is licensed under the MIT License.   

Acknowledgements
 This project is based on the Southern variant of the Forest Vegetation Simulator (FVS), developed by the USDA Forest Service.

Contact
Chris Mihiar
chris.mihiar@gmail.com

**Key Improvements:**

*   **Clearer Project Goals:** Explicitly states the objectives of the project.
*   **Detailed Project Structure:** Provides a more comprehensive explanation of the project's organization.
*   **More Complete Getting Started Instructions:** Includes instructions for creating a virtual environment, installing dependencies, and installing the package.
*   **Example Usage:** Shows a basic example of how to use the library.
*   **Contribution and License Information:** Adds sections for contributing and license information.
*   **Acknowledgements:** Acknowledges the original FVS developers.
*   **Contact Information:** Provides contact information for the project maintainer.
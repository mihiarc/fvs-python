# Configuration API Reference

## Overview

The `fvs_python.config` module provides a type-safe, hierarchical configuration system for FVS-Python.

## Classes

### SpeciesConfig

Configuration for species-specific parameters.

#### Attributes
- `code` (str): Species code (LP, SP, LL, SA)
- `name` (str): Full species name
- `min_dbh` (float): Minimum DBH in inches
- `max_dbh` (float): Maximum DBH in inches
- `min_height` (float): Minimum height in feet
- `max_height` (float): Maximum height in feet
- `min_crown_ratio` (float): Minimum crown ratio (0-1), default: 0.2
- `max_crown_ratio` (float): Maximum crown ratio (0-1), default: 0.9

### GrowthModelConfig

Configuration for growth model parameters.

#### Attributes
- `height_diameter_model` (str): Height-diameter relationship model to use, default: "curtis_arney"
- `small_tree_threshold` (float): DBH threshold for small tree classification (inches), default: 3.0
- `large_tree_threshold` (float): DBH threshold for large tree classification (inches), default: 5.0
- `timestep` (int): Simulation timestep in years, default: 5

### PathConfig

Configuration for data and file paths.

#### Attributes
- `data_dir` (Path): Root data directory
- `raw_data_dir` (Path): Raw data directory
- `processed_data_dir` (Path): Processed data directory
- `external_data_dir` (Path): External data directory
- `database_path` (Path): Path to SQLite database

#### Methods
- `set_raw_data_dir()`: Validator that sets raw_data_dir relative to data_dir
- `set_processed_data_dir()`: Validator that sets processed_data_dir relative to data_dir
- `set_external_data_dir()`: Validator that sets external_data_dir relative to data_dir
- `set_database_path()`: Validator that sets database_path relative to processed_data_dir

### LogConfig

Configuration for logging.

#### Attributes
- `level` (str): Default logging level, default: "INFO"
- `file_path` (Path): Path to log file
- `format` (str): Log message format

### SystemConfig

Configuration for system settings.

#### Attributes
- `n_jobs` (int): Number of jobs for parallel processing (-1 for all cores), default: -1
- `random_seed` (int): Random seed for reproducibility, default: 42
- `cache_dir` (Path): Directory for caching intermediate results

### FVSConfig

Main configuration class for FVS-Python.

#### Attributes
- `species` (Dict[str, SpeciesConfig]): Species-specific configurations
- `growth_model` (GrowthModelConfig): Growth model configuration
- `paths` (PathConfig): Path configuration
- `logging` (LogConfig): Logging configuration
- `system` (SystemConfig): System configuration

#### Methods
- `load_default() -> FVSConfig`: Load default configuration
- `load_from_file(path: Union[str, Path]) -> FVSConfig`: Load configuration from YAML file
- `save_to_file(path: Union[str, Path]) -> None`: Save configuration to YAML file

## Functions

### get_config() -> FVSConfig

Get the global configuration instance.

#### Returns
- FVSConfig: The global configuration instance

#### Behavior
1. If global config exists, return it
2. Try to load from FVS_CONFIG environment variable
3. Fall back to default configuration

### set_config(config: FVSConfig) -> None

Set the global configuration instance.

#### Parameters
- `config` (FVSConfig): The configuration instance to set as global

## Usage Examples

### Basic Usage
```python
from fvs_python.config import get_config

# Get configuration
config = get_config()

# Access values
species_config = config.species["LP"]
data_dir = config.paths.data_dir
```

### Custom Configuration
```python
from fvs_python.config import FVSConfig, set_config

# Load custom config
config = FVSConfig.load_from_file("my_config.yaml")

# Set as global config
set_config(config)
```

### Modifying Configuration
```python
config = get_config()

# Modify values
config.system.random_seed = 123
config.logging.level = "DEBUG"

# Save changes
config.save_to_file("modified_config.yaml")
```

## Type Hints

The module uses type hints throughout for better IDE support and runtime type checking:

```python
from typing import Dict, Union
from pathlib import Path

def load_from_file(path: Union[str, Path]) -> FVSConfig: ...
def get_species_config(species_code: str) -> SpeciesConfig: ...
```

## Validation

All configuration classes inherit from `pydantic.BaseModel`, providing:
- Type validation
- Data conversion
- Error messages
- JSON schema generation

Example validation:
```python
from pydantic import ValidationError

try:
    config = FVSConfig.load_from_file("invalid_config.yaml")
except ValidationError as e:
    print(f"Configuration error: {e}")
``` 
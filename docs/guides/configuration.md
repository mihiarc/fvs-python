# Configuration Guide

This guide explains how to configure FVS-Python for your needs. The configuration system is designed to be flexible, type-safe, and easy to use.

## Overview

FVS-Python uses a hierarchical configuration system that can be loaded from:
1. Environment variables
2. YAML configuration files
3. Default values

## Configuration Structure

The configuration is organized into several sections:

### Species Configuration
Controls species-specific parameters for each supported pine species:
```yaml
species:
  LP:  # Loblolly Pine
    code: "LP"
    name: "Loblolly Pine"
    min_dbh: 0.1        # inches
    max_dbh: 40.0       # inches
    min_height: 4.5     # feet
    max_height: 200.0   # feet
    min_crown_ratio: 0.2
    max_crown_ratio: 0.9
```

### Growth Model Configuration
Controls growth model behavior:
```yaml
growth_model:
  height_diameter_model: "curtis_arney"
  small_tree_threshold: 3.0  # inches
  large_tree_threshold: 5.0  # inches
  timestep: 5               # years
```

### Path Configuration
Manages file and directory paths:
```yaml
paths:
  data_dir: "data"
  raw_data_dir: "data/raw"
  processed_data_dir: "data/processed"
  external_data_dir: "data/external"
  database_path: "data/processed/fvspy.db"
```

### Logging Configuration
Controls logging behavior:
```yaml
logging:
  level: "INFO"
  file_path: "logs/fvs_python.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### System Configuration
Controls system-wide settings:
```yaml
system:
  n_jobs: -1           # -1 for all cores
  random_seed: 42
  cache_dir: ".cache"
```

## Usage

### Basic Usage

```python
from fvs_python.config import get_config

# Get the global configuration
config = get_config()

# Access configuration values
species_config = config.species["LP"]
data_dir = config.paths.data_dir
log_level = config.logging.level
```

### Custom Configuration File

1. Create a YAML file with your configuration:
```yaml
# my_config.yaml
species:
  LP:
    code: "LP"
    name: "Loblolly Pine"
    min_dbh: 0.5
    max_dbh: 35.0
    min_height: 4.5
    max_height: 180.0
    min_crown_ratio: 0.2
    max_crown_ratio: 0.9
# ... other settings ...
```

2. Load your configuration:
```python
from fvs_python.config import FVSConfig

config = FVSConfig.load_from_file("my_config.yaml")
```

### Environment Variables

Set the `FVS_CONFIG` environment variable to point to your configuration file:
```bash
export FVS_CONFIG=/path/to/my_config.yaml
```

The configuration will be automatically loaded from this file when `get_config()` is called.

## Validation

The configuration system uses Pydantic for validation, ensuring:
- All required fields are present
- Values are of the correct type
- Values are within acceptable ranges
- Paths are properly resolved

## Best Practices

1. **Version Control**: Keep your configuration files in version control
2. **Environment Separation**: Use different configuration files for development, testing, and production
3. **Documentation**: Document any custom configuration settings
4. **Validation**: Always validate configuration values before use
5. **Security**: Keep sensitive information in environment variables, not configuration files

## Common Tasks

### Saving Configuration
```python
config = get_config()
config.save_to_file("my_config.yaml")
```

### Modifying Configuration
```python
config = get_config()
config.system.random_seed = 123
config.logging.level = "DEBUG"
```

### Creating Development Configuration
```yaml
# config/development.yaml
logging:
  level: "DEBUG"
  file_path: "logs/development.log"

system:
  n_jobs: 1  # Single process for debugging
```

### Creating Production Configuration
```yaml
# config/production.yaml
logging:
  level: "WARNING"
  file_path: "/var/log/fvs_python.log"

system:
  n_jobs: -1  # Use all cores
```

## Troubleshooting

### Common Issues

1. **Configuration Not Found**
   - Check if the configuration file exists
   - Verify the path in `FVS_CONFIG` environment variable
   - Ensure file permissions are correct

2. **Validation Errors**
   - Check if all required fields are present
   - Verify value types match the expected types
   - Ensure values are within acceptable ranges

3. **Path Resolution**
   - Ensure all paths are relative to the project root
   - Check if directories exist
   - Verify file permissions

### Getting Help

If you encounter issues:
1. Check the logs for error messages
2. Verify your configuration against the default configuration
3. Consult the API documentation
4. File an issue on GitHub 
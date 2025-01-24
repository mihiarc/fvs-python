"""
Configuration management for FVS-Python.

This module provides a centralized configuration system for the FVS-Python project.
It handles loading configuration from environment variables, files, and defaults,
and provides type-safe access to configuration values.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator
import yaml

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

class SpeciesConfig(BaseModel):
    """Configuration for species-specific parameters."""
    
    code: str = Field(..., description="Species code (LP, SP, LL, SA)")
    name: str = Field(..., description="Full species name")
    min_dbh: float = Field(..., description="Minimum DBH in inches")
    max_dbh: float = Field(..., description="Maximum DBH in inches")
    min_height: float = Field(..., description="Minimum height in feet")
    max_height: float = Field(..., description="Maximum height in feet")
    min_crown_ratio: float = Field(0.2, description="Minimum crown ratio (0-1)")
    max_crown_ratio: float = Field(0.9, description="Maximum crown ratio (0-1)")

class GrowthModelConfig(BaseModel):
    """Configuration for growth model parameters."""
    
    height_diameter_model: str = Field(
        "curtis_arney",
        description="Height-diameter relationship model to use"
    )
    small_tree_threshold: float = Field(
        3.0,
        description="DBH threshold for small tree classification (inches)"
    )
    large_tree_threshold: float = Field(
        5.0,
        description="DBH threshold for large tree classification (inches)"
    )
    timestep: int = Field(
        5,
        description="Simulation timestep in years"
    )

class PathConfig(BaseModel):
    """Configuration for data and file paths."""
    
    data_dir: Path = Field(
        PROJECT_ROOT / "data",
        description="Root data directory"
    )
    raw_data_dir: Path = Field(
        None,
        description="Raw data directory"
    )
    processed_data_dir: Path = Field(
        None,
        description="Processed data directory"
    )
    external_data_dir: Path = Field(
        None,
        description="External data directory"
    )
    database_path: Path = Field(
        None,
        description="Path to SQLite database"
    )
    
    @validator("raw_data_dir", pre=True, always=True)
    def set_raw_data_dir(cls, v, values):
        return v or values["data_dir"] / "raw"
    
    @validator("processed_data_dir", pre=True, always=True)
    def set_processed_data_dir(cls, v, values):
        return v or values["data_dir"] / "processed"
    
    @validator("external_data_dir", pre=True, always=True)
    def set_external_data_dir(cls, v, values):
        return v or values["data_dir"] / "external"
    
    @validator("database_path", pre=True, always=True)
    def set_database_path(cls, v, values):
        return v or values["processed_data_dir"] / "fvspy.db"

class LogConfig(BaseModel):
    """Configuration for logging."""
    
    level: str = Field(
        "INFO",
        description="Default logging level"
    )
    file_path: Path = Field(
        PROJECT_ROOT / "logs" / "fvs_python.log",
        description="Path to log file"
    )
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )

class SystemConfig(BaseModel):
    """Configuration for system settings."""
    
    n_jobs: int = Field(
        -1,
        description="Number of jobs for parallel processing (-1 for all cores)"
    )
    random_seed: int = Field(
        42,
        description="Random seed for reproducibility"
    )
    cache_dir: Path = Field(
        PROJECT_ROOT / ".cache",
        description="Directory for caching intermediate results"
    )

class FVSConfig(BaseModel):
    """Main configuration class for FVS-Python."""
    
    species: Dict[str, SpeciesConfig] = Field(
        ...,
        description="Species-specific configurations"
    )
    growth_model: GrowthModelConfig = Field(
        default_factory=GrowthModelConfig,
        description="Growth model configuration"
    )
    paths: PathConfig = Field(
        default_factory=PathConfig,
        description="Path configuration"
    )
    logging: LogConfig = Field(
        default_factory=LogConfig,
        description="Logging configuration"
    )
    system: SystemConfig = Field(
        default_factory=SystemConfig,
        description="System configuration"
    )
    
    @classmethod
    def load_default(cls) -> "FVSConfig":
        """Load default configuration."""
        return cls(
            species={
                "LP": SpeciesConfig(
                    code="LP",
                    name="Loblolly Pine",
                    min_dbh=0.1,
                    max_dbh=40.0,
                    min_height=4.5,
                    max_height=200.0
                ),
                "SP": SpeciesConfig(
                    code="SP",
                    name="Shortleaf Pine",
                    min_dbh=0.1,
                    max_dbh=40.0,
                    min_height=4.5,
                    max_height=200.0
                ),
                "LL": SpeciesConfig(
                    code="LL",
                    name="Longleaf Pine",
                    min_dbh=0.1,
                    max_dbh=40.0,
                    min_height=4.5,
                    max_height=200.0
                ),
                "SA": SpeciesConfig(
                    code="SA",
                    name="Slash Pine",
                    min_dbh=0.1,
                    max_dbh=40.0,
                    min_height=4.5,
                    max_height=200.0
                )
            }
        )
    
    @classmethod
    def load_from_file(cls, path: Union[str, Path]) -> "FVSConfig":
        """Load configuration from YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(path) as f:
            config_dict = yaml.safe_load(f)
        
        return cls(**config_dict)
    
    def save_to_file(self, path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            yaml.dump(self.dict(), f, default_flow_style=False)

# Global configuration instance
_config: Optional[FVSConfig] = None

def get_config() -> FVSConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Try to load from environment variable
        config_path = os.getenv("FVS_CONFIG")
        if config_path:
            _config = FVSConfig.load_from_file(config_path)
        else:
            _config = FVSConfig.load_default()
    return _config

def set_config(config: FVSConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config 
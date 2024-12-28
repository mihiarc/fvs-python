"""
FVS-Python Core Module

This module provides the core functionality for the Forest Vegetation Simulator (FVS)
Python implementation, focusing on the Southern variant.
"""

from . import growth_models
from . import crown_ratio
from . import data_handling
from . import volume

__all__ = ['growth_models', 'crown_ratio', 'data_handling', 'volume']

__version__ = '0.1.0'

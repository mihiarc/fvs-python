"""
FVS-Python Core Module

This module provides the core functionality for the Forest Vegetation Simulator (FVS)
Python implementation, focusing on the Southern variant.
"""

from .data_handling import calculate_site_index, species_data, site_index_groups
from .site_index import calculate_rsisp, calculate_mgspix, calculate_mgrsi, calculate_sisp

__all__ = [
    'calculate_site_index',
    'species_data',
    'site_index_groups',
    'calculate_rsisp',
    'calculate_mgspix',
    'calculate_mgrsi',
    'calculate_sisp'
]

__version__ = '0.1.0'

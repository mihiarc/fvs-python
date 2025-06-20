"""
FVS-Python: Southern Yellow Pine Growth Simulator

A Python implementation of forest growth models based on the 
Forest Vegetation Simulator (FVS) Southern variant.
"""

from .stand import Stand
from .tree import Tree
from .config_loader import get_config_loader, load_stand_config, load_tree_config
from .height_diameter import create_height_diameter_model, curtis_arney_height, wykoff_height
from .crown_ratio import create_crown_ratio_model, calculate_average_crown_ratio, predict_tree_crown_ratio
from .bark_ratio import create_bark_ratio_model, calculate_dib_from_dob, calculate_bark_ratio
from .crown_width import create_crown_width_model, calculate_forest_crown_width, calculate_open_crown_width, calculate_ccf_contribution, calculate_hopkins_index
from .crown_competition_factor import create_ccf_model, calculate_individual_ccf, calculate_stand_ccf, calculate_ccf_from_stand, interpret_ccf
from .volume_library import (
    VolumeLibrary, VolumeResult, calculate_tree_volume, 
    get_volume_library, get_volume_library_info, validate_volume_library
)
from .main import main

__version__ = "0.1.0"
__author__ = "FVS-Python Development Team"

__all__ = [
    "Stand",
    "Tree", 
    "get_config_loader",
    "load_stand_config",
    "load_tree_config",
    "create_height_diameter_model",
    "curtis_arney_height",
    "wykoff_height",
    "create_crown_ratio_model", 
    "calculate_average_crown_ratio",
    "predict_tree_crown_ratio",
    "create_bark_ratio_model",
    "calculate_dib_from_dob",
    "calculate_bark_ratio",
    "create_crown_width_model",
    "calculate_forest_crown_width",
    "calculate_open_crown_width",
    "calculate_ccf_contribution",
    "calculate_hopkins_index",
    "create_ccf_model",
    "calculate_individual_ccf",
    "calculate_stand_ccf",
    "calculate_ccf_from_stand",
    "interpret_ccf",
    "VolumeLibrary",
    "VolumeResult", 
    "calculate_tree_volume",
    "get_volume_library",
    "get_volume_library_info",
    "validate_volume_library",
    "main"
]

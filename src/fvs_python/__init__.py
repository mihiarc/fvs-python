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
    "main"
]

"""
Configuration loader for FVS-Python.
Provides unified access to the new YAML configuration system.
"""
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads and manages FVS configuration from the cfg/ directory."""
    
    def __init__(self, cfg_dir: Path = None):
        """Initialize the configuration loader.
        
        Args:
            cfg_dir: Path to the configuration directory. Defaults to ../cfg relative to this file.
        """
        if cfg_dir is None:
            cfg_dir = Path(__file__).parent.parent / 'cfg'
        self.cfg_dir = cfg_dir
        
        # Load main configuration files
        self._load_main_config()
    
    def _load_main_config(self):
        """Load the main configuration files."""
        # Load species configuration
        with open(self.cfg_dir / 'species_config.yaml', 'r') as f:
            self.species_config = yaml.safe_load(f)
        
        # Load functional forms
        with open(self.cfg_dir / self.species_config['functional_forms_file'], 'r') as f:
            self.functional_forms = yaml.safe_load(f)
        
        # Load site index transformations
        with open(self.cfg_dir / self.species_config['site_index_transformation_file'], 'r') as f:
            self.site_index_params = yaml.safe_load(f)
    
    def load_species_config(self, species_code: str) -> Dict[str, Any]:
        """Load configuration for a specific species.
        
        Args:
            species_code: Species code (e.g., 'LP', 'SP', 'SA', 'LL')
            
        Returns:
            Dictionary containing species-specific parameters
        """
        if species_code not in self.species_config['species']:
            raise ValueError(f"Unknown species code: {species_code}")
        
        species_info = self.species_config['species'][species_code]
        species_file = self.cfg_dir / species_info['file']
        
        with open(species_file, 'r') as f:
            return yaml.safe_load(f)
    
    def get_stand_params(self, species_code: str = 'LP') -> Dict[str, Any]:
        """Get parameters needed for Stand class in the legacy format.
        
        Args:
            species_code: Species code (default: 'LP' for loblolly pine)
            
        Returns:
            Dictionary with parameters in the format expected by Stand class
        """
        species_params = self.load_species_config(species_code)
        
        # Convert to legacy format expected by Stand class
        stand_params = {
            'species': species_code.lower() + '_pine',
            'crown': {
                # Extract crown width parameters for loblolly pine
                'a1': 0.7380,  # From README.md species data
                'a2': 0.2450,
                'a3': 0.000809
            },
            'mortality': {
                'max_sdi': species_params.get('density', {}).get('sdi_max', 480),
                'background_rate': 0.005,
                'competition_threshold': 0.55
            },
            'volume': {
                'form_factor': 0.48
            }
        }
        
        return stand_params
    
    def get_tree_params(self, species_code: str = 'LP') -> Dict[str, Any]:
        """Get parameters needed for Tree class.
        
        Args:
            species_code: Species code (default: 'LP' for loblolly pine)
            
        Returns:
            Dictionary with parameters for Tree class
        """
        return self.load_species_config(species_code)


# Global configuration loader instance
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def load_stand_config(species_code: str = 'LP') -> Dict[str, Any]:
    """Convenience function to load stand configuration."""
    return get_config_loader().get_stand_params(species_code)

def load_tree_config(species_code: str = 'LP') -> Dict[str, Any]:
    """Convenience function to load tree configuration."""
    return get_config_loader().get_tree_params(species_code) 
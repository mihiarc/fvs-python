#!/usr/bin/env python3
"""
Command-line interface for FVS-Python.
Provides easy access to simulation and configuration management.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from .main import main as run_simulation
from .config_loader import convert_yaml_to_toml, get_config_loader


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="fvs-simulate",
        description="FVS-Python: Southern Yellow Pine Growth Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a basic simulation
  fvs-simulate run

  # Run simulation with custom parameters
  fvs-simulate run --years 40 --timestep 5 --species LP --site-index 70

  # Convert YAML configs to TOML
  fvs-simulate convert-config --output-dir ./cfg/toml

  # Validate configuration files
  fvs-simulate validate-config

  # Show configuration for a species
  fvs-simulate show-config --species LP
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run simulation command
    run_parser = subparsers.add_parser(
        "run", 
        help="Run forest growth simulation"
    )
    run_parser.add_argument(
        "--years", 
        type=int, 
        default=50,
        help="Total simulation length in years (default: 50)"
    )
    run_parser.add_argument(
        "--timestep", 
        type=int, 
        default=5,
        help="Years between measurements (default: 5)"
    )
    run_parser.add_argument(
        "--species", 
        type=str, 
        default="LP",
        choices=["LP", "SP", "SA", "LL"],
        help="Species code (default: LP for Loblolly Pine)"
    )
    run_parser.add_argument(
        "--site-index", 
        type=float, 
        default=70.0,
        help="Site index (base age 25) in feet (default: 70)"
    )
    run_parser.add_argument(
        "--trees-per-acre", 
        type=int, 
        default=500,
        help="Initial trees per acre (default: 500)"
    )
    run_parser.add_argument(
        "--output-dir", 
        type=Path, 
        default=None,
        help="Output directory for results (default: ./output)"
    )
    run_parser.add_argument(
        "--config-dir", 
        type=Path, 
        default=None,
        help="Configuration directory (default: ./cfg)"
    )
    
    # Convert configuration command
    convert_parser = subparsers.add_parser(
        "convert-config",
        help="Convert YAML configuration files to TOML format"
    )
    convert_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Input directory with YAML configs (default: ./cfg)"
    )
    convert_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for TOML configs (default: ./cfg/toml)"
    )
    
    # Validate configuration command
    validate_parser = subparsers.add_parser(
        "validate-config",
        help="Validate configuration files"
    )
    validate_parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Configuration directory to validate (default: ./cfg)"
    )
    
    # Show configuration command
    show_parser = subparsers.add_parser(
        "show-config",
        help="Display configuration for a species"
    )
    show_parser.add_argument(
        "--species",
        type=str,
        default="LP",
        choices=["LP", "SP", "SA", "LL"],
        help="Species code to show config for (default: LP)"
    )
    show_parser.add_argument(
        "--format",
        type=str,
        default="yaml",
        choices=["yaml", "json"],
        help="Output format (default: yaml)"
    )
    
    return parser


def cmd_run(args) -> int:
    """Run forest growth simulation."""
    try:
        print(f"Running FVS simulation for {args.species} species...")
        print(f"Parameters: {args.years} years, {args.timestep}-year timesteps")
        print(f"Site index: {args.site_index}, Trees/acre: {args.trees_per_acre}")
        
        # Set up output directory
        if args.output_dir:
            output_dir = args.output_dir
        else:
            output_dir = Path.cwd() / "output"
        
        output_dir.mkdir(exist_ok=True)
        print(f"Output directory: {output_dir}")
        
        # Run the simulation
        run_simulation()
        
        print("Simulation completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error running simulation: {e}", file=sys.stderr)
        return 1


def cmd_convert_config(args) -> int:
    """Convert YAML configuration files to TOML."""
    try:
        print("Converting YAML configuration files to TOML...")
        
        input_dir = args.input_dir or Path.cwd() / "cfg"
        output_dir = args.output_dir or input_dir / "toml"
        
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        
        convert_yaml_to_toml(input_dir, output_dir)
        
        print("Configuration conversion completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error converting configuration: {e}", file=sys.stderr)
        return 1


def cmd_validate_config(args) -> int:
    """Validate configuration files."""
    try:
        print("Validating configuration files...")
        
        config_dir = args.config_dir or Path.cwd() / "cfg"
        print(f"Configuration directory: {config_dir}")
        
        # Try to load the configuration
        loader = get_config_loader()
        
        # Test loading each species
        species_codes = ["LP", "SP", "SA", "LL"]
        for species in species_codes:
            try:
                config = loader.load_species_config(species)
                print(f"✓ {species}: Configuration loaded successfully")
            except Exception as e:
                print(f"✗ {species}: Error loading configuration - {e}")
        
        print("Configuration validation completed!")
        return 0
        
    except Exception as e:
        print(f"Error validating configuration: {e}", file=sys.stderr)
        return 1


def cmd_show_config(args) -> int:
    """Display configuration for a species."""
    try:
        loader = get_config_loader()
        config = loader.load_species_config(args.species)
        
        print(f"Configuration for species {args.species}:")
        print("-" * 40)
        
        if args.format == "yaml":
            import yaml
            print(yaml.dump(config, default_flow_style=False, sort_keys=False))
        elif args.format == "json":
            import json
            print(json.dumps(config, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error showing configuration: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate command handler
    if args.command == "run":
        return cmd_run(args)
    elif args.command == "convert-config":
        return cmd_convert_config(args)
    elif args.command == "validate-config":
        return cmd_validate_config(args)
    elif args.command == "show-config":
        return cmd_show_config(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
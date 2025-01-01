"""Script to generate growth model test report."""

import os
import sys
import datetime
import pytest
import platform
from pathlib import Path

def run_visualization_tests(tmp_path):
    """Run visualization tests and collect results."""
    # Import and run tests
    from test_growth_visualizations import (
        test_visualize_height_diameter_relationship,
        test_visualize_growth_rates,
        test_visualize_competition_effects,
        test_visualize_crown_ratio_dynamics
    )
    
    # Run tests and save plots
    test_visualize_height_diameter_relationship(tmp_path)
    test_visualize_growth_rates(tmp_path)
    test_visualize_competition_effects(tmp_path)
    test_visualize_crown_ratio_dynamics(tmp_path)
    
    return tmp_path

def copy_plots(source_dir, target_dir):
    """Copy generated plots to report directory."""
    plot_files = [
        'height_diameter_relationship.png',
        'growth_rates.png',
        'competition_effects.png',
        'crown_ratio_dynamics.png'
    ]
    
    for plot in plot_files:
        source = source_dir / plot
        target = target_dir / plot
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

def generate_report(report_dir: Path, species: str = 'LP', site_index: float = 70.0):
    """Generate test report with results."""
    # Create temporary directory for plots
    tmp_path = Path(report_dir) / 'temp'
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    # Run tests and generate plots
    plot_dir = run_visualization_tests(tmp_path)
    
    # Copy plots to report directory
    copy_plots(plot_dir, report_dir)
    
    # Read template
    template_path = Path(__file__).parent / 'test_report_template.md'
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Fill in template
    report = template.format(
        DATE=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        SPECIES=species,
        SITE_INDEX=site_index,
        VERSION=pytest.__version__,
        TESTER=os.getenv('USER', 'unknown'),
        STATUS='DRAFT'
    )
    
    # Write report
    report_path = report_dir / 'growth_model_test_report.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    return report_path

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Generate growth model test report')
    parser.add_argument('--species', default='LP', help='Species code')
    parser.add_argument('--site-index', type=float, default=70.0, help='Site index')
    parser.add_argument('--output-dir', default='reports', help='Output directory')
    args = parser.parse_args()
    
    # Generate report
    output_dir = Path(args.output_dir)
    report_path = generate_report(
        output_dir,
        species=args.species,
        site_index=args.site_index
    )
    
    print(f'Report generated: {report_path}') 
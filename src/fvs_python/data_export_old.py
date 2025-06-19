"""
Data export utilities for FVS-Python.
Provides various formats for exporting simulation results.
"""
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

from .logging_config import get_logger


class DataExporter:
    """Handles export of simulation data to various formats."""
    
    def __init__(self, output_dir: Path):
        """Initialize the data exporter.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.logger = get_logger(__name__)
    
    def export_to_csv(self, 
                     data: Union[pd.DataFrame, List[Dict]], 
                     filename: str,
                     include_metadata: bool = True) -> Path:
        """Export data to CSV format.
        
        Args:
            data: Data to export (DataFrame or list of dicts)
            filename: Output filename
            include_metadata: Whether to include metadata header
            
        Returns:
            Path to exported file
        """
        filepath = self.output_dir / f"{filename}.csv"
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        with open(filepath, 'w', newline='') as f:
            if include_metadata:
                # Write metadata header
                f.write(f"# FVS-Python Export\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Records: {len(df)}\n")
                f.write(f"# Columns: {', '.join(df.columns)}\n")
                f.write("#\n")
            
            # Write data
            df.to_csv(f, index=False)
        
        self.logger.info(f"Exported {len(df)} records to {filepath}")
        return filepath
    
    def export_to_json(self, 
                      data: Union[pd.DataFrame, List[Dict], Dict], 
                      filename: str,
                      include_metadata: bool = True,
                      format_style: str = 'records') -> Path:
        """Export data to JSON format.
        
        Args:
            data: Data to export
            filename: Output filename
            include_metadata: Whether to include metadata
            format_style: JSON format ('records', 'values', 'index', 'split')
            
        Returns:
            Path to exported file
        """
        filepath = self.output_dir / f"{filename}.json"
        
        # Prepare data
        if isinstance(data, pd.DataFrame):
            if format_style == 'records':
                export_data = data.to_dict('records')
            elif format_style == 'values':
                export_data = data.values.tolist()
            elif format_style == 'index':
                export_data = data.to_dict('index')
            elif format_style == 'split':
                export_data = data.to_dict('split')
            else:
                export_data = data.to_dict('records')
        elif isinstance(data, list):
            export_data = data
        else:
            export_data = data
        
        # Create output structure
        output = {}
        if include_metadata:
            output['metadata'] = {
                'generator': 'FVS-Python',
                'generated_at': datetime.now().isoformat(),
                'format': format_style,
                'record_count': len(export_data) if isinstance(export_data, list) else 1
            }
        
        output['data'] = export_data
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=self._json_serializer)
        
        self.logger.info(f"Exported data to {filepath}")
        return filepath
    
    def export_to_xml(self, 
                     data: Union[pd.DataFrame, List[Dict]], 
                     filename: str,
                     root_element: str = 'fvs_data',
                     record_element: str = 'record') -> Path:
        """Export data to XML format.
        
        Args:
            data: Data to export
            filename: Output filename
            root_element: Name of root XML element
            record_element: Name of individual record elements
            
        Returns:
            Path to exported file
        """
        filepath = self.output_dir / f"{filename}.xml"
        
        # Convert to list of dicts if necessary
        if isinstance(data, pd.DataFrame):
            records = data.to_dict('records')
        else:
            records = data
        
        # Create XML structure
        root = ET.Element(root_element)
        
        # Add metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'generator').text = 'FVS-Python'
        ET.SubElement(metadata, 'generated_at').text = datetime.now().isoformat()
        ET.SubElement(metadata, 'record_count').text = str(len(records))
        
        # Add data
        data_element = ET.SubElement(root, 'data')
        
        for i, record in enumerate(records):
            record_elem = ET.SubElement(data_element, record_element)
            record_elem.set('id', str(i))
            
            for key, value in record.items():
                elem = ET.SubElement(record_elem, str(key))
                elem.text = str(value) if value is not None else ''\n        \n        # Write to file\n        tree = ET.ElementTree(root)\n        ET.indent(tree, space=\"  \", level=0)\n        tree.write(filepath, encoding='utf-8', xml_declaration=True)\n        \n        self.logger.info(f\"Exported {len(records)} records to {filepath}\")\n        return filepath\n    \n    def export_to_excel(self, \n                       data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], \n                       filename: str,\n                       include_charts: bool = False) -> Path:\n        \"\"\"Export data to Excel format.\n        \n        Args:\n            data: Data to export (single DataFrame or dict of DataFrames for multiple sheets)\n            filename: Output filename\n            include_charts: Whether to include basic charts (requires openpyxl)\n            \n        Returns:\n            Path to exported file\n        \"\"\"\n        filepath = self.output_dir / f\"{filename}.xlsx\"\n        \n        try:\n            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:\n                if isinstance(data, pd.DataFrame):\n                    # Single sheet\n                    data.to_excel(writer, sheet_name='Data', index=False)\n                    \n                    if include_charts:\n                        self._add_excel_charts(writer.book['Data'], data)\n                        \n                else:\n                    # Multiple sheets\n                    for sheet_name, df in data.items():\n                        df.to_excel(writer, sheet_name=sheet_name, index=False)\n                        \n                        if include_charts:\n                            self._add_excel_charts(writer.book[sheet_name], df)\n                \n            self.logger.info(f\"Exported data to Excel file {filepath}\")\n            return filepath\n            \n        except ImportError:\n            self.logger.warning(\"openpyxl not available, falling back to CSV export\")\n            if isinstance(data, pd.DataFrame):\n                return self.export_to_csv(data, filename)\n            else:\n                # Export first sheet to CSV\n                first_sheet = next(iter(data.values()))\n                return self.export_to_csv(first_sheet, filename)\n    \n    def export_yield_table(self, \n                          yield_table: pd.DataFrame,\n                          format: str = 'csv',\n                          filename: Optional[str] = None) -> Path:\n        \"\"\"Export yield table with proper formatting.\n        \n        Args:\n            yield_table: Yield table DataFrame\n            format: Export format ('csv', 'json', 'xml', 'excel')\n            filename: Custom filename (optional)\n            \n        Returns:\n            Path to exported file\n        \"\"\"\n        if filename is None:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            filename = f\"yield_table_{timestamp}\"\n        \n        # Round numeric columns for better presentation\n        display_table = yield_table.copy()\n        numeric_columns = ['mean_dbh', 'mean_height', 'basal_area', 'volume']\n        for col in numeric_columns:\n            if col in display_table.columns:\n                display_table[col] = display_table[col].round(2)\n        \n        # Sort by logical order\n        if all(col in display_table.columns for col in ['species', 'site_index', 'initial_tpa', 'age']):\n            display_table = display_table.sort_values(['species', 'site_index', 'initial_tpa', 'age'])\n        \n        if format.lower() == 'csv':\n            return self.export_to_csv(display_table, filename)\n        elif format.lower() == 'json':\n            return self.export_to_json(display_table, filename)\n        elif format.lower() == 'xml':\n            return self.export_to_xml(display_table, filename, 'yield_table', 'yield_entry')\n        elif format.lower() == 'excel':\n            return self.export_to_excel(display_table, filename)\n        else:\n            raise ValueError(f\"Unsupported format: {format}\")\n    \n    def export_scenario_comparison(self, \n                                 comparison_df: pd.DataFrame,\n                                 format: str = 'csv',\n                                 filename: Optional[str] = None) -> Path:\n        \"\"\"Export scenario comparison results.\n        \n        Args:\n            comparison_df: Scenario comparison DataFrame\n            format: Export format\n            filename: Custom filename (optional)\n            \n        Returns:\n            Path to exported file\n        \"\"\"\n        if filename is None:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            filename = f\"scenario_comparison_{timestamp}\"\n        \n        # Create summary statistics\n        if format.lower() == 'excel':\n            # Create multiple sheets for Excel\n            sheets = {\n                'Raw_Data': comparison_df,\n                'Summary': self._create_scenario_summary(comparison_df)\n            }\n            return self.export_to_excel(sheets, filename)\n        else:\n            return getattr(self, f'export_to_{format.lower()}')(comparison_df, filename)\n    \n    def export_stand_metrics(self, \n                           metrics_over_time: List[Dict],\n                           format: str = 'csv',\n                           filename: Optional[str] = None) -> Path:\n        \"\"\"Export stand metrics over time.\n        \n        Args:\n            metrics_over_time: List of metric dictionaries\n            format: Export format\n            filename: Custom filename (optional)\n            \n        Returns:\n            Path to exported file\n        \"\"\"\n        if filename is None:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            filename = f\"stand_metrics_{timestamp}\"\n        \n        df = pd.DataFrame(metrics_over_time)\n        \n        # Round numeric columns\n        numeric_columns = df.select_dtypes(include=[np.number]).columns\n        df[numeric_columns] = df[numeric_columns].round(2)\n        \n        if format.lower() == 'csv':\n            return self.export_to_csv(df, filename)\n        elif format.lower() == 'json':\n            return self.export_to_json(df, filename)\n        elif format.lower() == 'xml':\n            return self.export_to_xml(df, filename, 'stand_metrics', 'metric_record')\n        elif format.lower() == 'excel':\n            return self.export_to_excel(df, filename)\n        else:\n            raise ValueError(f\"Unsupported format: {format}\")\n    \n    def create_summary_report(self, \n                            simulation_results: Dict[str, Any],\n                            filename: Optional[str] = None) -> Path:\n        \"\"\"Create a comprehensive summary report.\n        \n        Args:\n            simulation_results: Dictionary containing all simulation results\n            filename: Custom filename (optional)\n            \n        Returns:\n            Path to summary report file\n        \"\"\"\n        if filename is None:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            filename = f\"simulation_summary_{timestamp}\"\n        \n        filepath = self.output_dir / f\"{filename}.txt\"\n        \n        with open(filepath, 'w') as f:\n            f.write(\"FVS-Python Simulation Summary Report\\n\")\n            f.write(\"=\" * 50 + \"\\n\\n\")\n            \n            f.write(f\"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\")\n            f.write(f\"Software: FVS-Python v1.0.0\\n\\n\")\n            \n            # Simulation parameters\n            if 'parameters' in simulation_results:\n                params = simulation_results['parameters']\n                f.write(\"Simulation Parameters:\\n\")\n                f.write(\"-\" * 25 + \"\\n\")\n                for key, value in params.items():\n                    f.write(f\"{key}: {value}\\n\")\n                f.write(\"\\n\")\n            \n            # Final metrics\n            if 'final_metrics' in simulation_results:\n                metrics = simulation_results['final_metrics']\n                f.write(\"Final Stand Metrics:\\n\")\n                f.write(\"-\" * 25 + \"\\n\")\n                f.write(f\"Age: {metrics.get('age', 'N/A')} years\\n\")\n                f.write(f\"Trees per Acre: {metrics.get('tpa', 'N/A'):.0f}\\n\")\n                f.write(f\"Mean DBH: {metrics.get('mean_dbh', 'N/A'):.1f} inches\\n\")\n                f.write(f\"Mean Height: {metrics.get('mean_height', 'N/A'):.1f} feet\\n\")\n                f.write(f\"Basal Area: {metrics.get('basal_area', 'N/A'):.1f} sq ft/acre\\n\")\n                f.write(f\"Volume: {metrics.get('volume', 'N/A'):.0f} cubic feet/acre\\n\")\n                f.write(\"\\n\")\n            \n            # Growth summary\n            if 'growth_summary' in simulation_results:\n                f.write(\"Growth Summary:\\n\")\n                f.write(\"-\" * 25 + \"\\n\")\n                summary = simulation_results['growth_summary']\n                f.write(f\"Total DBH Growth: {summary.get('total_dbh_growth', 'N/A'):.1f} inches\\n\")\n                f.write(f\"Total Height Growth: {summary.get('total_height_growth', 'N/A'):.1f} feet\\n\")\n                f.write(f\"Total Volume Growth: {summary.get('total_volume_growth', 'N/A'):.0f} cu ft/acre\\n\")\n                f.write(f\"Survival Rate: {summary.get('survival_rate', 'N/A'):.1%}\\n\")\n                f.write(\"\\n\")\n            \n            # File references\n            f.write(\"Associated Files:\\n\")\n            f.write(\"-\" * 25 + \"\\n\")\n            if 'output_files' in simulation_results:\n                for file_type, filepath in simulation_results['output_files'].items():\n                    f.write(f\"{file_type}: {filepath}\\n\")\n        \n        self.logger.info(f\"Created summary report: {filepath}\")\n        return filepath\n    \n    def _json_serializer(self, obj):\n        \"\"\"JSON serializer for numpy types.\"\"\"\n        if isinstance(obj, np.integer):\n            return int(obj)\n        elif isinstance(obj, np.floating):\n            return float(obj)\n        elif isinstance(obj, np.ndarray):\n            return obj.tolist()\n        elif isinstance(obj, pd.Timestamp):\n            return obj.isoformat()\n        return str(obj)\n    \n    def _add_excel_charts(self, worksheet, data: pd.DataFrame):\n        \"\"\"Add basic charts to Excel worksheet (placeholder for future implementation).\"\"\"\n        # This would require openpyxl chart functionality\n        # Implementation would depend on specific chart requirements\n        pass\n    \n    def _create_scenario_summary(self, comparison_df: pd.DataFrame) -> pd.DataFrame:\n        \"\"\"Create summary statistics for scenario comparison.\"\"\"\n        if 'scenario' not in comparison_df.columns:\n            return pd.DataFrame()\n        \n        # Get final metrics for each scenario\n        final_metrics = []\n        for scenario in comparison_df['scenario'].unique():\n            scenario_data = comparison_df[comparison_df['scenario'] == scenario]\n            final_row = scenario_data[scenario_data['age'] == scenario_data['age'].max()].iloc[0]\n            \n            summary = {\n                'scenario': scenario,\n                'final_age': final_row['age'],\n                'final_tpa': final_row.get('tpa', 0),\n                'final_volume': final_row.get('volume', 0),\n                'final_mean_dbh': final_row.get('mean_dbh', 0),\n                'final_mean_height': final_row.get('mean_height', 0)\n            }\n            final_metrics.append(summary)\n        \n        return pd.DataFrame(final_metrics)\n\n\ndef export_all_formats(data: Union[pd.DataFrame, List[Dict]],\n                      output_dir: Path,\n                      base_filename: str) -> Dict[str, Path]:\n    \"\"\"Export data to all supported formats.\n    \n    Args:\n        data: Data to export\n        output_dir: Output directory\n        base_filename: Base filename (without extension)\n        \n    Returns:\n        Dictionary mapping format names to file paths\n    \"\"\"\n    exporter = DataExporter(output_dir)\n    \n    exported_files = {}\n    \n    # CSV\n    try:\n        exported_files['csv'] = exporter.export_to_csv(data, base_filename)\n    except Exception as e:\n        print(f\"CSV export failed: {e}\")\n    \n    # JSON\n    try:\n        exported_files['json'] = exporter.export_to_json(data, base_filename)\n    except Exception as e:\n        print(f\"JSON export failed: {e}\")\n    \n    # XML\n    try:\n        exported_files['xml'] = exporter.export_to_xml(data, base_filename)\n    except Exception as e:\n        print(f\"XML export failed: {e}\")\n    \n    # Excel\n    try:\n        exported_files['excel'] = exporter.export_to_excel(data, base_filename)\n    except Exception as e:\n        print(f\"Excel export failed: {e}\")\n    \n    return exported_files
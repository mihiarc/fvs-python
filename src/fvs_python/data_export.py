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
                elem.text = str(value) if value is not None else ''
        
        # Write to file
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
        
        self.logger.info(f"Exported {len(records)} records to {filepath}")
        return filepath
    
    def export_to_excel(self, 
                       data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                       filename: str,
                       include_charts: bool = False) -> Path:
        """Export data to Excel format.
        
        Args:
            data: Data to export (single DataFrame or dict of DataFrames for multiple sheets)
            filename: Output filename
            include_charts: Whether to include basic charts (requires openpyxl)
            
        Returns:
            Path to exported file
        """
        filepath = self.output_dir / f"{filename}.xlsx"
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                if isinstance(data, pd.DataFrame):
                    # Single sheet
                    data.to_excel(writer, sheet_name='Data', index=False)
                    
                    if include_charts:
                        self._add_excel_charts(writer.book['Data'], data)
                        
                else:
                    # Multiple sheets
                    for sheet_name, df in data.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        if include_charts:
                            self._add_excel_charts(writer.book[sheet_name], df)
                
            self.logger.info(f"Exported data to Excel file {filepath}")
            return filepath
            
        except ImportError:
            self.logger.warning("openpyxl not available, falling back to CSV export")
            if isinstance(data, pd.DataFrame):
                return self.export_to_csv(data, filename)
            else:
                # Export first sheet to CSV
                first_sheet = next(iter(data.values()))
                return self.export_to_csv(first_sheet, filename)
    
    def export_yield_table(self, 
                          yield_table: pd.DataFrame,
                          format: str = 'csv',
                          filename: Optional[str] = None) -> Path:
        """Export yield table with proper formatting.
        
        Args:
            yield_table: Yield table DataFrame
            format: Export format ('csv', 'json', 'xml', 'excel')
            filename: Custom filename (optional)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yield_table_{timestamp}"
        
        # Round numeric columns for better presentation
        display_table = yield_table.copy()
        numeric_columns = ['mean_dbh', 'mean_height', 'basal_area', 'volume']
        for col in numeric_columns:
            if col in display_table.columns:
                display_table[col] = display_table[col].round(2)
        
        # Sort by logical order
        if all(col in display_table.columns for col in ['species', 'site_index', 'initial_tpa', 'age']):
            display_table = display_table.sort_values(['species', 'site_index', 'initial_tpa', 'age'])
        
        if format.lower() == 'csv':
            return self.export_to_csv(display_table, filename)
        elif format.lower() == 'json':
            return self.export_to_json(display_table, filename)
        elif format.lower() == 'xml':
            return self.export_to_xml(display_table, filename, 'yield_table', 'yield_entry')
        elif format.lower() == 'excel':
            return self.export_to_excel(display_table, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _json_serializer(self, obj):
        """JSON serializer for numpy types."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return str(obj)
    
    def _add_excel_charts(self, worksheet, data: pd.DataFrame):
        """Add basic charts to Excel worksheet (placeholder for future implementation)."""
        # This would require openpyxl chart functionality
        # Implementation would depend on specific chart requirements
        pass
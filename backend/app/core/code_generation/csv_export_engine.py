import csv
from io import StringIO
from typing import Dict, List
from datetime import datetime


class CSVExportEngine:
    """Export generated code to CSV format"""
    
    def export_project_code(self, project_data: Dict) -> str:
        """
        Export complete project code to CSV
        
        Args:
            project_data: Dict with project info and all generated codes
        
        Returns:
            CSV string with UTF-8 compatible encoding
        """
        output = StringIO(newline='')
        # Use standard CSV formatting with Windows CRLF line endings
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
        
        # Write header
        writer.writerow(['AI PLC Platform - Code Export'])
        writer.writerow(['Project:', project_data.get('project_name', 'Unknown')])
        writer.writerow(['Exported:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Export each stage
        for code in project_data.get('codes', []):
            self._export_stage_code(writer, code)
            writer.writerow([])  # Blank line between stages
        
        return output.getvalue()
    
    def export_stage_code(self, stage_code: Dict) -> str:
        """
        Export single stage code to CSV
        
        Args:
            stage_code: Dict with stage code data
        
        Returns:
            CSV string with UTF-8 compatible encoding
        """
        output = StringIO(newline='')
        # Use standard CSV formatting with Windows CRLF line endings
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
        
        # Write header
        writer.writerow(['AI PLC Platform - Stage Code Export'])
        writer.writerow(['Exported:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Export stage
        self._export_stage_code(writer, stage_code)
        
        return output.getvalue()
    
    def _export_stage_code(self, writer, code: Dict):
        """Export a single stage code to CSV writer"""
        # Stage header
        writer.writerow(['=== STAGE INFORMATION ==='])
        writer.writerow(['Program Name:', code.get('program_name', 'N/A')])
        writer.writerow(['Execution Type:', code.get('execution_type', 'N/A')])
        writer.writerow([])
        
        # Global Labels
        writer.writerow(['=== GLOBAL LABELS ==='])
        writer.writerow(['Label Name', 'Data Type', 'Class', 'Device Name', 'Initial Value', 'Constant', 'English', 'Remark'])
        
        for label in code.get('global_labels', []):
            writer.writerow([
                label.get('name', ''),
                label.get('data_type', ''),
                label.get('class', ''),
                label.get('device', ''),
                label.get('initial_value', ''),
                label.get('constant', ''),
                label.get('comment', ''),
                label.get('comment', '')
            ])
        
        writer.writerow([])
        
        # Local Labels
        writer.writerow(['=== LOCAL LABELS ==='])
        writer.writerow(['Label Name', 'Data Type', 'Class', 'Initial Value', 'Constant', 'English'])
        
        for label in code.get('local_labels', []):
            writer.writerow([
                label.get('name', ''),
                label.get('data_type', ''),
                label.get('class', ''),
                label.get('initial_value', ''),
                label.get('constant', ''),
                label.get('comment', '')
            ])
        
        writer.writerow([])
        
        # Program Body
        writer.writerow(['=== STRUCTURED TEXT PROGRAM BODY ==='])
        writer.writerow(['Program Name:', code.get('program_name', '')])
        writer.writerow(['Execution Type:', code.get('execution_type', '')])
        writer.writerow([])
        writer.writerow(['Code:'])
        
        # Split program body into lines for better CSV formatting
        program_body = code.get('program_body', '')
        for line in program_body.split('\n'):
            writer.writerow([line])


# Global instance
csv_export_engine = CSVExportEngine()
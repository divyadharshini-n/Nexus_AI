"""
Labels CSV Exporter
Export global and local labels to CSV format
"""
from io import BytesIO, StringIO
from typing import List, Dict
import csv


class LabelsCsvExporter:
    """Export labels to CSV format"""
    
    def _safe_str(self, value) -> str:
        """Convert None or any value to safe string for CSV export"""
        if value is None:
            return ""
        return str(value).strip()
    
    def export_labels(self, global_labels: List[Dict], local_labels: List[Dict], 
                     stage_name: str = "Stage") -> BytesIO:
        """
        Export global and local labels to CSV
        
        Args:
            global_labels: List of global label dictionaries
            local_labels: List of local label dictionaries
            stage_name: Name of the stage
            
        Returns:
            BytesIO: CSV file content in memory, UTF-8 encoded
        """
        output = StringIO()
        
        # Write Global Labels section
        output.write(f"# Global Labels - {stage_name}\n")
        output.write("\n")
        
        if global_labels:
            writer = csv.writer(output)
            # Write header
            writer.writerow([
                "Label Name", "Data Type", "Class", "Device", 
                "Initial Value", "Constant", "Comment", "Remark"
            ])
            
            # Write data
            for label in global_labels:
                writer.writerow([
                    self._safe_str(label.get('name', '')),
                    self._safe_str(label.get('data_type', '')),
                    self._safe_str(label.get('class', '')),
                    self._safe_str(label.get('device', '')),
                    self._safe_str(label.get('initial_value', '')),
                    'Yes' if label.get('constant', False) else 'No',
                    self._safe_str(label.get('comment', '')),
                    self._safe_str(label.get('remark', ''))
                ])
        else:
            output.write("No global labels\n")
        
        output.write("\n\n")
        
        # Write Local Labels section
        output.write(f"# Local Labels - {stage_name}\n")
        output.write("\n")
        
        if local_labels:
            writer = csv.writer(output)
            # Write header
            writer.writerow([
                "Label Name", "Data Type", "Class", 
                "Initial Value", "Constant", "Comment"
            ])
            
            # Write data
            for label in local_labels:
                writer.writerow([
                    self._safe_str(label.get('name', '')),
                    self._safe_str(label.get('data_type', '')),
                    self._safe_str(label.get('class', '')),
                    self._safe_str(label.get('initial_value', '')),
                    'Yes' if label.get('constant', False) else 'No',
                    self._safe_str(label.get('comment', ''))
                ])
        else:
            output.write("No local labels\n")
        
        # Convert to UTF-16 LE encoded bytes with BOM (required by GX Works3)
        text_content = output.getvalue()
        bytes_output = BytesIO(text_content.encode('utf-16-le'))
        # Add UTF-16 LE BOM at the beginning
        final_output = BytesIO(b'\xff\xfe' + bytes_output.getvalue())
        return final_output
    
    def export_all_stages_labels(self, stages_data: List[Dict]) -> BytesIO:
        """
        Export LOCAL labels from multiple stages to a single CSV file in GX Works 3 format
        
        Args:
            stages_data: List of dicts with stage_name, local_labels
            
        Returns:
            BytesIO: CSV file content with local labels from all stages, UTF-16 LE encoded
        """
        output = StringIO()
        # Use tab delimiter for TSV format with Windows CRLF line endings
        writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\', lineterminator='\r\n')
        
        # Write project name/title row
        writer.writerow(["(Untitled Project)"] + [""] * 26)
        writer.writerow([
            "Class", "Label Name", "Data Type", "Constant", "Initial Value",
            "Assign (Device/Label)", "Address", "Comment", "Comment 2", "Comment 3",
            "Comment 4", "Comment 5", "Japanese/日本語", "English", 
            "Chinese Simplified/简体中文", "Korean/한국어", "Chinese Traditional/繁體中文",
            "German/Deutsch", "Italian/Italiano", "Reserved1", "Reserved2", "Reserved3",
            "Reserved4", "Remark", "System Label Relation", "System Label Name",
            "Attribute"
        ])
        
        # Export local labels from all stages
        for i, stage_data in enumerate(stages_data):
            stage_number = stage_data.get('stage_number', i+1)
            stage_name = stage_data.get('stage_name', f'Stage {stage_number}')
            local_labels = stage_data.get('local_labels', [])
            
            # Write local labels for each stage
            if local_labels:
                for label in local_labels:
                    label_class = self._safe_str(label.get('class', 'VAR'))
                    writer.writerow([
                        label_class,  # Class
                        self._safe_str(label.get('name', '')),  # Label Name
                        self._safe_str(label.get('data_type', '')),  # Data Type
                        "",  # Constant
                        "",  # Initial Value
                        "",  # Assign (Device/Label)
                        "",  # Address
                        "",  # Comment
                        "",  # Comment 2
                        "",  # Comment 3
                        "",  # Comment 4
                        "",  # Comment 5
                        "",  # Japanese
                        "",  # English
                        "",  # Chinese Simplified
                        "",  # Korean
                        "",  # Chinese Traditional
                        "",  # German
                        "",  # Italian
                        "",  # Reserved1
                        "",  # Reserved2
                        "",  # Reserved3
                        "",  # Reserved4
                        "",  # Remark
                        "",  # System Label Relation
                        "",  # System Label Name
                        ""   # Attribute
                    ])
        
        # Convert to UTF-16 LE encoded bytes with BOM (required by GX Works3)
        text_content = output.getvalue()
        bytes_output = BytesIO(text_content.encode('utf-16-le'))
        # Add UTF-16 LE BOM at the beginning
        final_output = BytesIO(b'\xff\xfe' + bytes_output.getvalue())
        return final_output

    def export_global_labels_gx_format(self, global_labels: List[Dict]) -> BytesIO:
        """
        Export global labels in GX Works 3 format (tab-separated with UTF-16 LE encoding)
        
        Args:
            global_labels: List of global label dictionaries
            
        Returns:
            BytesIO: CSV file content in GX Works 3 format, UTF-16 LE encoded
        """
        output = StringIO()
        # Use tab delimiter with QUOTE_ALL for global labels (all fields quoted)
        writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
        
        # Write project name/title row (28 columns for global labels)
        writer.writerow(["(Untitled Project)"] + [""] * 27)
        
        # Write header row with all GX Works 3 columns (28 columns including Access from External Device)
        writer.writerow([
            "Class", "Label Name", "Data Type", "Constant", "Initial Value",
            "Assign (Device/Label)", "Address", "Comment", "Comment 2", "Comment 3",
            "Comment 4", "Comment 5", "Japanese/日本語", "English", 
            "Chinese Simplified/简体中文", "Korean/한국어", "Chinese Traditional/繁體中文",
            "German/Deutsch", "Italian/Italiano", "Reserved1", "Reserved2", "Reserved3",
            "Reserved4", "Remark", "System Label Relation", "System Label Name",
            "Attribute", "Access from External Device"
        ])
        
        # Write data rows
        for label in global_labels:
            writer.writerow([
                "VAR_GLOBAL",  # Class
                self._safe_str(label.get('name', '')),  # Label Name
                self._safe_str(label.get('data_type', '')),  # Data Type
                "",  # Constant
                "",  # Initial Value
                self._safe_str(label.get('device', '')),  # Assign (Device/Label)
                "",  # Address
                "",  # Comment
                "",  # Comment 2
                "",  # Comment 3
                "",  # Comment 4
                "",  # Comment 5
                "",  # Japanese
                "",  # English
                "",  # Chinese Simplified
                "",  # Korean
                "",  # Chinese Traditional
                "",  # German
                "",  # Italian
                "",  # Reserved1
                "",  # Reserved2
                "",  # Reserved3
                "",  # Reserved4
                "",  # Remark
                "",  # System Label Relation
                "",  # System Label Name
                "",  # Attribute
                self._safe_str(label.get('access_from_external', '0'))  # Access from External Device
            ])
        
        # Convert to UTF-16 LE encoded bytes with BOM (required by GX Works3)
        text_content = output.getvalue()
        bytes_output = BytesIO(text_content.encode('utf-16-le'))
        # Add UTF-16 LE BOM at the beginning
        final_output = BytesIO(b'\xff\xfe' + bytes_output.getvalue())
        return final_output

    def export_local_labels_gx_format(self, local_labels: List[Dict], stage_name: str = "Stage") -> BytesIO:
        """
        Export local labels in GX Works 3 format (tab-separated with proper UTF-8 encoding)
        
        Args:
            local_labels: List of local label dictionaries
            stage_name: Name of the stage for the title row
            
        Returns:
            BytesIO: CSV file content in GX Works 3 format, UTF-8 encoded
        """
        output = StringIO()
        # Use tab delimiter for TSV format with Windows CRLF line endings
        writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\', lineterminator='\r\n')
        
        # Write project name/title row
        writer.writerow(["(Untitled Project)"] + [""] * 26)
        
        # Write header row with all GX Works 3 columns (27 columns)
        writer.writerow([
            "Class", "Label Name", "Data Type", "Constant", "Initial Value",
            "Assign (Device/Label)", "Address", "Comment", "Comment 2", "Comment 3",
            "Comment 4", "Comment 5", "Japanese/日本語", "English", 
            "Chinese Simplified/简体中文", "Korean/한국어", "Chinese Traditional/繁體中文",
            "German/Deutsch", "Italian/Italiano", "Reserved1", "Reserved2", "Reserved3",
            "Reserved4", "Remark", "System Label Relation", "System Label Name",
            "Attribute"
        ])
        
        # Write data rows
        for label in local_labels:
            # Determine the class based on the label's class field (VAR_INPUT, VAR_OUTPUT, VAR, etc.)
            label_class = self._safe_str(label.get('class', 'VAR_INPUT'))
            
            writer.writerow([
                label_class,  # Class (VAR_INPUT, VAR_OUTPUT, etc.)
                self._safe_str(label.get('name', '')),  # Label Name
                self._safe_str(label.get('data_type', '')),  # Data Type
                "",  # Constant
                "",  # Initial Value
                "",  # Assign (Device/Label)
                "",  # Address
                "",  # Comment
                "",  # Comment 2
                "",  # Comment 3
                "",  # Comment 4
                "",  # Comment 5
                "",  # Japanese
                "",  # English
                "",  # Chinese Simplified
                "",  # Korean
                "",  # Chinese Traditional
                "",  # German
                "",  # Italian
                "",  # Reserved1
                "",  # Reserved2
                "",  # Reserved3
                "",  # Reserved4
                "",  # Remark
                "",  # System Label Relation
                "",  # System Label Name
                ""   # Attribute
            ])
        
        # Convert to UTF-16 LE encoded bytes with BOM (required by GX Works3)
        text_content = output.getvalue()
        bytes_output = BytesIO(text_content.encode('utf-16-le'))
        # Add UTF-16 LE BOM at the beginning
        final_output = BytesIO(b'\xff\xfe' + bytes_output.getvalue())
        return final_output


# Create singleton instance
labels_csv_exporter = LabelsCsvExporter()

"""
PDF Version History Generator
Generates comprehensive PDF reports for version history with employee tracking,
validation counts, change diffs, and timestamps.
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
import difflib
from app.config import settings


class PDFVersionHistoryGenerator:
    """Generate comprehensive PDF version history reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#7F8C8D'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            spaceBefore=6,
            spaceAfter=6,
            backColor=colors.HexColor('#F8F9FA')
        ))
        
        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495E')
        ))
        
        # Employee style
        self.styles.add(ParagraphStyle(
            name='EmployeeText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2980B9'),
            fontName='Helvetica-Bold'
        ))
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page"""
        canvas_obj.saveState()
        
        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor('#2C3E50'))
        canvas_obj.drawString(
            inch, 
            doc.height + doc.topMargin + 0.3*inch,
            "Version History Report"
        )
        
        # Footer
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.HexColor('#7F8C8D'))
        footer_text = f"Page {doc.page} | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        canvas_obj.drawRightString(
            doc.width + doc.leftMargin,
            0.5*inch,
            footer_text
        )
        
        canvas_obj.restoreState()
    
    def _create_info_table(self, data: List[tuple], col_widths=None) -> Table:
        """Create a styled information table"""
        if not col_widths:
            col_widths = [2*inch, 4*inch]
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table
    
    def _create_version_table(self, history: List[Dict], employee_names: Dict[int, str]) -> Table:
        """Create a styled table for version history"""
        # Headers
        data = [[
            Paragraph('<b>Version</b>', self.styles['Normal']),
            Paragraph('<b>Action</b>', self.styles['Normal']),
            Paragraph('<b>Employee</b>', self.styles['Normal']),
            Paragraph('<b>Timestamp</b>', self.styles['Normal']),
            Paragraph('<b>Validations</b>', self.styles['Normal'])
        ]]
        
        # Add version rows
        for v in history:
            metadata = v.get('version_metadata') or {}
            action = metadata.get('action', 'Unknown').replace('_', ' ').title()
            
            # Get employee name
            employee = employee_names.get(v.get('user_id'), 'Unknown')
            
            # Get timestamp
            timestamp = v.get('timestamp')
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    pass
            
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
            
            # Count validations
            validation_count = metadata.get('validation_count', 0)
            
            # Color code based on action
            action_color = '#27AE60' if action == 'Validate' else '#3498DB'
            
            data.append([
                Paragraph(f'<b>{v.get("version_number", "N/A")}</b>', self.styles['Normal']),
                Paragraph(f'<font color="{action_color}">{action}</font>', self.styles['Normal']),
                Paragraph(f'<font color="#2980B9"><b>{employee}</b></font>', self.styles['Normal']),
                Paragraph(timestamp_str, self.styles['Normal']),
                Paragraph(f'<b>{validation_count}</b>', self.styles['Normal'])
            ])
        
        # Create table
        table = Table(data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.7*inch, 1*inch])
        
        # Style table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternate row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        
        return table
    
    def _format_diff(self, old_text: str, new_text: str) -> str:
        """Generate a formatted diff between old and new text"""
        if not old_text and not new_text:
            return "No changes"
        
        if not old_text:
            return f"<font color='#27AE60'><b>New content added</b></font>"
        
        if not new_text:
            return f"<font color='#E74C3C'><b>Content removed</b></font>"
        
        # Split into lines
        old_lines = old_text.splitlines() if old_text else []
        new_lines = new_text.splitlines() if new_text else []
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=3  # Context lines
        ))
        
        if not diff:
            return "<i>No changes detected</i>"
        
        # Format diff with colors
        formatted_lines = []
        for line in diff[2:]:  # Skip header lines
            if line.startswith('+'):
                formatted_lines.append(f'<font color="#27AE60">+ {line[1:]}</font>')
            elif line.startswith('-'):
                formatted_lines.append(f'<font color="#E74C3C">- {line[1:]}</font>')
            elif line.startswith('@@'):
                formatted_lines.append(f'<font color="#3498DB"><b>{line}</b></font>')
            else:
                formatted_lines.append(f'  {line}')
        
        return '<br/>'.join(formatted_lines[:50])  # Limit to 50 lines
    
    def _add_change_comparison(self, story, version: Dict, employee_name: str):
        """Add a comparison section showing before/after changes"""
        metadata = version.get('version_metadata') or {}
        action = metadata.get('action', 'Unknown').replace('_', ' ').title()
        
        # Section header
        story.append(Paragraph(
            f'Version {version.get("version_number", "N/A")} - {action}',
            self.styles['SubsectionHeader']
        ))
        
        # Employee and timestamp info
        timestamp = version.get('timestamp')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                pass
        
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
        
        info_data = [
            ['Employee:', Paragraph(f'<font color="#2980B9"><b>{employee_name}</b></font>', self.styles['Normal'])],
            ['Timestamp:', timestamp_str],
            ['Action:', action],
            ['Validations:', str(metadata.get('validation_count', 0))]
        ]
        
        story.append(self._create_info_table(info_data, [1.5*inch, 4.5*inch]))
        story.append(Spacer(1, 0.2*inch))
        
        # Show old vs new logic/code
        old_code = version.get('old_code', '')
        new_code = version.get('new_code', '')
        
        if action in ['Edit Logic', 'Generate Code']:
            # Before section
            story.append(Paragraph('<b>Previous:</b>', self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            if old_code:
                # Truncate if too long
                display_old = old_code[:1000] + ('...' if len(old_code) > 1000 else '')
                story.append(Paragraph(
                    f'<font face="Courier" size="8">{display_old.replace("<", "&lt;").replace(">", "&gt;")}</font>',
                    self.styles['CodeBlock']
                ))
            else:
                story.append(Paragraph('<i>No previous content</i>', self.styles['Normal']))
            
            story.append(Spacer(1, 0.15*inch))
            
            # After section
            story.append(Paragraph('<b>Updated:</b>', self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            if new_code:
                # Truncate if too long
                display_new = new_code[:1000] + ('...' if len(new_code) > 1000 else '')
                story.append(Paragraph(
                    f'<font face="Courier" size="8">{display_new.replace("<", "&lt;").replace(">", "&gt;")}</font>',
                    self.styles['CodeBlock']
                ))
            else:
                story.append(Paragraph('<i>No new content</i>', self.styles['Normal']))
            
            story.append(Spacer(1, 0.15*inch))
            
            # Show diff
            story.append(Paragraph('<b>Changes:</b>', self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            diff_html = self._format_diff(old_code, new_code)
            story.append(Paragraph(
                f'<font face="Courier" size="8">{diff_html}</font>',
                self.styles['CodeBlock']
            ))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#BDC3C7')))
        story.append(Spacer(1, 0.2*inch))
    
    def generate_version_history_pdf(
        self,
        stage: Any,
        history: List[Dict],
        project_name: str,
        employee_names: Dict[int, str]
    ) -> str:
        """
        Generate comprehensive PDF version history report
        
        Args:
            stage: Stage object or dict
            history: List of version history dicts
            project_name: Name of the project
            employee_names: Dict mapping user_id to employee full name
            
        Returns:
            Path to generated PDF file
        """
        # Setup output path
        output_dir = Path(settings.BASE_DIR) / "data" / "reports" / "versions"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        stage_name = stage.get('stage_name') if isinstance(stage, dict) else stage.stage_name
        filename = f"version_history_{stage_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story
        story = []
        
        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph('Version History Report', self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f'<font size="14">{project_name}</font>',
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f'<font size="12" color="#7F8C8D">Stage: {stage_name}</font>',
            self.styles['Normal']
        ))
        story.append(PageBreak())
        
        # Stage information
        story.append(Paragraph('Stage Information', self.styles['SectionHeader']))
        
        stage_number = stage.get('stage_number') if isinstance(stage, dict) else stage.stage_number
        version_number = stage.get('version_number') if isinstance(stage, dict) else stage.version_number
        
        info_data = [
            ['Project:', project_name],
            ['Stage Number:', str(stage_number)],
            ['Stage Name:', stage_name],
            ['Current Version:', version_number or 'N/A'],
            ['Total Versions:', str(len(history))]
        ]
        
        story.append(self._create_info_table(info_data))
        story.append(Spacer(1, 0.4*inch))
        
        # Version summary table
        story.append(Paragraph('Version History Summary', self.styles['SectionHeader']))
        
        if history:
            story.append(self._create_version_table(history, employee_names))
        else:
            story.append(Paragraph('<i>No version history available</i>', self.styles['Normal']))
        
        story.append(Spacer(1, 0.4*inch))
        
        # Calculate statistics
        if history:
            total_validations = sum(
                (v.get('version_metadata') or {}).get('validation_count', 0)
                for v in history
            )
            edit_count = sum(
                1 for v in history
                if (v.get('version_metadata') or {}).get('action') == 'edit_logic'
            )
            
            stats_data = [
                ['Total Versions:', str(len(history))],
                ['Total Validations:', str(total_validations)],
                ['Logic Edits:', str(edit_count)],
                ['Contributors:', str(len(set(v.get('user_id') for v in history if v.get('user_id'))))]
            ]
            
            story.append(Paragraph('Statistics', self.styles['SectionHeader']))
            story.append(self._create_info_table(stats_data))
            story.append(Spacer(1, 0.4*inch))
        
        # Detailed change history
        if history:
            story.append(PageBreak())
            story.append(Paragraph('Detailed Change History', self.styles['SectionHeader']))
            story.append(Spacer(1, 0.2*inch))
            
            for version in history:
                user_id = version.get('user_id')
                employee_name = employee_names.get(user_id, 'Unknown')
                self._add_change_comparison(story, version, employee_name)
        
        # Build PDF with header/footer
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return str(output_path)

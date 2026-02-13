from pathlib import Path
from typing import Dict, List
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom styles"""
        # Title style
        if "CustomTitle" not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#003366'),
                spaceAfter=30,
                alignment=TA_CENTER
            ))
        
        # Subtitle
        if "CustomSubtitle" not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomSubtitle',
                parent=self.styles['Normal'],
                fontSize=16,
                textColor=colors.HexColor('#666666'),
                spaceAfter=12,
                alignment=TA_CENTER
            ))
        
        # Code style
        if "Code" not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Code',
                parent=self.styles['Normal'],
                fontName='Courier',
                fontSize=8,
                leftIndent=20,
                spaceAfter=12
            ))
    
    def generate_project_report(
        self,
        project: Dict,
        stages: List[Dict],
        codes: List[Dict],
        validations: Dict = None,
        safety_assessments: Dict = None
    ) -> str:
        """
        Generate complete project report in PDF format
        
        Returns:
            Path to generated PDF file
        """
        # Create output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{project['name'].replace(' ', '_')}_{timestamp}.pdf"
        output_path = Path("data/reports") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Cover page
        story.extend(self._build_cover_page(project))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._build_executive_summary(project, stages, codes))
        story.append(PageBreak())
        
        # Project overview
        story.extend(self._build_project_overview(project))
        story.append(Spacer(1, 0.2*inch))
        
        # Stages
        story.extend(self._build_stages_section(stages, codes))
        
        if validations:
            story.append(PageBreak())
            story.extend(self._build_validation_section(validations))
        
        if safety_assessments:
            story.append(PageBreak())
            story.extend(self._build_safety_section(safety_assessments))
        
        # Build PDF
        doc.build(story)
        
        return str(output_path)
    
    def _build_cover_page(self, project: Dict) -> List:
        """Build cover page"""
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("AI PLC Platform", self.styles['CustomTitle']))
        story.append(Paragraph("Project Report", self.styles['CustomSubtitle']))
        
        # Project name
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"<b>{project['name']}</b>", self.styles['CustomTitle']))
        
        # Date
        story.append(Spacer(1, 3*inch))
        date_text = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(date_text, self.styles['CustomSubtitle']))
        
        return story
    
    def _build_executive_summary(self, project: Dict, stages: List[Dict], codes: List[Dict]) -> List:
        """Build executive summary"""
        story = []
        
        story.append(Paragraph("<b>Executive Summary</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Project info
        story.append(Paragraph(f"<b>Project Name:</b> {project['name']}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Description:</b> {project.get('description', 'N/A')}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Statistics
        story.append(Paragraph("<b>Project Statistics</b>", self.styles['Heading2']))
        
        validated_count = sum(1 for s in stages if s.get('is_validated'))
        finalized_count = sum(1 for s in stages if s.get('is_finalized'))
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Stages', str(len(stages))],
            ['Code Modules', str(len(codes))],
            ['Validated Stages', f"{validated_count}/{len(stages)}"],
            ['Finalized Stages', f"{finalized_count}/{len(stages)}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        
        return story
    
    def _build_project_overview(self, project: Dict) -> List:
        """Build project overview"""
        story = []
        
        story.append(Paragraph("<b>1. Project Overview</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        overview_data = [
            ['Field', 'Value'],
            ['Project Name', project['name']],
            ['Description', project.get('description', 'N/A')],
            ['Created Date', str(project.get('created_at', 'N/A'))]
        ]
        
        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(overview_table)
        
        return story
    
    def _build_stages_section(self, stages: List[Dict], codes: List[Dict]) -> List:
        """Build stages section"""
        story = []
        
        story.append(Paragraph("<b>2. Stages & Logic</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        for stage in stages:
            # Stage header
            story.append(Paragraph(
                f"<b>Stage {stage['stage_number']}: {stage['stage_name']}</b>",
                self.styles['Heading2']
            ))
            
            # Stage info
            story.append(Paragraph(f"<b>Type:</b> {stage['stage_type']}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Description:</b> {stage['description']}", self.styles['Normal']))
            
            # Original logic
            story.append(Paragraph("<b>Original Logic:</b>", self.styles['Normal']))
            story.append(Paragraph(stage['original_logic'], self.styles['Code']))
            
            # Status
            status_text = f"Validated: {'Yes' if stage.get('is_validated') else 'No'} | "
            status_text += f"Finalized: {'Yes' if stage.get('is_finalized') else 'No'}"
            story.append(Paragraph(status_text, self.styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _build_validation_section(self, validations: Dict) -> List:
        """Build validation section"""
        story = []
        
        story.append(Paragraph("<b>4. Validation Results</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        for stage_id, validation in validations.items():
            story.append(Paragraph(f"<b>Stage {stage_id}</b>", self.styles['Heading2']))
            story.append(Paragraph(f"<b>Status:</b> {validation.get('status', 'N/A')}", self.styles['Normal']))
            
            if validation.get('issues'):
                story.append(Paragraph("<b>Issues:</b>", self.styles['Normal']))
                for issue in validation['issues']:
                    story.append(Paragraph(f"• {issue}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _build_safety_section(self, safety_assessments: Dict) -> List:
        """Build safety section"""
        story = []
        
        story.append(Paragraph("<b>5. Safety Assessments</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        for stage_id, assessment in safety_assessments.items():
            story.append(Paragraph(f"<b>Stage {stage_id}</b>", self.styles['Heading2']))
            story.append(Paragraph(f"<b>Status:</b> {assessment.get('status', 'N/A')}", self.styles['Normal']))
            
            if assessment.get('hazards'):
                story.append(Paragraph("<b>Hazards:</b>", self.styles['Normal']))
                for hazard in assessment['hazards']:
                    story.append(Paragraph(f"⚠️ {hazard}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        return story


# Global instance
pdf_report_generator = PDFReportGenerator()
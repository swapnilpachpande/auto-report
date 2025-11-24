"""
Module to generate comprehensive PDF reports with visualizations.
"""
from pathlib import Path
from datetime import datetime
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class PDFReportGenerator:
    """Generate PDF reports with data visualizations."""
    
    def __init__(self, title="AutoReport", author="AutoReport System"):
        """
        Initialize PDF Report Generator.
        
        :param title: Title of the report
        :param author: Author name
        """
        self.title = title
        self.author = author
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2e5c8a'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=14
        ))
    
    def generate_pdf_report(self, report_path, basic_text, ai_summary, visualization_paths=None):
        """
        Generate a comprehensive PDF report with text and visualizations.
        
        :param report_path: Path object for reports directory
        :param basic_text: JSON string or text of basic statistics
        :param ai_summary: AI-generated summary text
        :param visualization_paths: List of paths to visualization images (PNG/JPG)
        :return: Path to the generated PDF file
        """
        report_path.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"report_{timestamp}.pdf"
        pdf_file = report_path / pdf_filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_file),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            author=self.author,
            title=self.title
        )
        
        # Build story (content)
        story = []
        
        # Add title
        story.append(Paragraph(self.title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add generation timestamp
        timestamp_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}"
        story.append(Paragraph(timestamp_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add Basic Statistics section
        story.append(Paragraph("📊 Basic Statistics", self.styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Parse and format basic statistics
        try:
            if isinstance(basic_text, str):
                # Try to parse as JSON for better formatting
                try:
                    stats_dict = json.loads(basic_text)
                    stats_text = self._format_statistics_for_pdf(stats_dict)
                    story.append(Paragraph(stats_text, self.styles['CustomBody']))
                except json.JSONDecodeError:
                    # If not JSON, just add the text
                    story.append(Paragraph(basic_text.replace('\n', '<br/>'), self.styles['CustomBody']))
        except Exception as e:
            story.append(Paragraph(f"Error processing statistics: {str(e)}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Add AI Summary section
        story.append(Paragraph("🤖 AI-Generated Insights", self.styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        ai_text = ai_summary if isinstance(ai_summary, str) else str(ai_summary)
        # Handle AI summary that might be a response object
        if hasattr(ai_summary, 'choices'):
            ai_text = ai_summary.choices[0].message.content if hasattr(ai_summary.choices[0].message, 'content') else str(ai_summary)
        
        story.append(Paragraph(ai_text.replace('\n', '<br/>'), self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add visualizations if provided
        if visualization_paths:
            story.append(PageBreak())
            story.append(Paragraph("📈 Data Visualizations", self.styles['CustomHeading']))
            story.append(Spacer(1, 0.2*inch))
            
            for viz_path in visualization_paths:
                if isinstance(viz_path, str):
                    viz_path = Path(viz_path)
                
                if viz_path.exists() and viz_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    try:
                        # Add image with appropriate sizing
                        img = Image(str(viz_path), width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                    except Exception as e:
                        story.append(Paragraph(f"Error loading visualization: {viz_path}", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return pdf_file
    
    @staticmethod
    def _format_statistics_for_pdf(stats_dict):
        """
        Format statistics dictionary as readable HTML-like text for PDF.
        
        :param stats_dict: Dictionary of statistics
        :return: Formatted string
        """
        lines = []
        
        if 'basic_stats' in stats_dict:
            basic = stats_dict['basic_stats']
            lines.append(f"<b>Dataset Overview:</b><br/>")
            lines.append(f"Rows: {basic.get('rows', 'N/A')}<br/>")
            lines.append(f"Columns: {basic.get('columns', 'N/A')}<br/>")
            lines.append(f"Memory Usage: {basic.get('memory_usage', 'N/A'):.2f} MB<br/><br/>")
        
        if 'numeric_stats' in stats_dict:
            lines.append(f"<b>Numeric Columns Summary:</b><br/>")
            numeric = stats_dict['numeric_stats']
            if 'basic' in numeric:
                lines.append(f"Descriptive statistics available for numeric columns<br/><br/>")
        
        return ''.join(lines)


def generate_pdf_report(report_path, basic_stats, ai_summary, visualization_paths=None):
    """
    Standalone function to generate PDF report.
    
    :param report_path: Path to reports directory
    :param basic_stats: Basic statistics text/dict
    :param ai_summary: AI-generated summary
    :param visualization_paths: List of visualization image paths
    :return: Path to generated PDF
    """
    generator = PDFReportGenerator(title="Comprehensive Data Analysis Report")
    
    # Convert basic_stats to string if it's a dict
    if isinstance(basic_stats, dict):
        basic_text = json.dumps(basic_stats, indent=2, default=str)
    else:
        basic_text = str(basic_stats)
    
    pdf_path = generator.generate_pdf_report(
        report_path=report_path,
        basic_text=basic_text,
        ai_summary=ai_summary,
        visualization_paths=visualization_paths
    )
    
    return pdf_path
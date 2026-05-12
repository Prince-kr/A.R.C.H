import os
import json
from datetime import datetime
from utils.logger import Logger

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class ReportExporter:
    def __init__(self, repository):
        self.repo = repository
        self.export_dir = "data/exports"
        os.makedirs(self.export_dir, exist_ok=True)

    def export_all_to_txt(self):
        """Generates a consolidated plain text report of all experiments."""
        sessions = self.repo.get_all_sessions()
        if not sessions:
            return None, "No sessions found to export."

        filename = os.path.join(self.export_dir, f"full_narrative_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("A.R.C.H. FRAMEWORK - CONSOLIDATED NARRATIVE REPORT\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            for s in sessions:
                details = self.repo.get_session_details(s.id)
                if not details: continue

                f.write(f"SESSION ID: {details['id']}\n")
                f.write(f"Timestamp: {details['timestamp']}\n")
                f.write(f"Mode:      {details['mode']}\n")
                f.write("-" * 40 + "\n")
                
                f.write("RED TEAM ACTIVITY:\n")
                f.write(f"  Tool:   {details['attack']['tool']}\n")
                f.write(f"  Target: {details['attack']['target']}\n")
                f.write(f"  Status: {details['attack']['status']}\n")
                f.write("  Output Snippet:\n")
                f.write(f"    {details['attack']['stdout'][:500].replace('\n', '\n    ')}\n\n")

                f.write("BLUE TEAM ACTIVITY:\n")
                f.write(f"  Tool:     {details['defense']['tool']}\n")
                f.write("  Findings:\n")
                if isinstance(details['defense']['findings'], list):
                    for finding in details['defense']['findings']:
                        f.write(f"    - {json.dumps(finding)}\n")
                else:
                    f.write(f"    {str(details['defense']['findings'])[:500].replace('\n', '\n    ')}\n")
                
                f.write("\n" + "="*80 + "\n\n")

        return filename, "Success"

    def export_all_to_pdf(self):
        """Generates a consolidated PDF report using reportlab."""
        if not PDF_AVAILABLE:
            return None, "PDF library (reportlab) not installed. Run 'pip install reportlab' first."

        sessions = self.repo.get_all_sessions()
        if not sessions:
            return None, "No sessions found to export."

        filename = os.path.join(self.export_dir, f"full_narrative_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.cadetblue
        )
        
        session_header_style = ParagraphStyle(
            'SessionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            textColor=colors.darkred
        )

        story = []
        
        # Title Page
        story.append(Paragraph("A.R.C.H. Framework", header_style))
        story.append(Paragraph("Consolidated Research Narrative Report", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Total Sessions: {len(sessions)}", styles['Normal']))
        story.append(PageBreak())

        for s in sessions:
            details = self.repo.get_session_details(s.id)
            if not details: continue

            story.append(Paragraph(f"Session {details['id']} - {details['timestamp']}", session_header_style))
            story.append(Spacer(1, 6))
            
            # Metadata Table
            data = [
                ["Mode", details['mode']],
                ["Target", details['attack']['target']],
                ["Red Tool", details['attack']['tool']],
                ["Exit Status", str(details['attack']['status'])],
                ["Blue Tool", details['defense']['tool']]
            ]
            t = Table(data, colWidths=[100, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

            # Red Team Output
            story.append(Paragraph("Red Team Activity Output Snippet:", styles['Heading3']))
            clean_stdout = details['attack']['stdout'][:800].replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
            story.append(Paragraph(f"<font face='Courier' size='8'>{clean_stdout}</font>", styles['Normal']))
            story.append(Spacer(1, 12))

            # Blue Team Findings
            story.append(Paragraph("Blue Team Defense Findings:", styles['Heading3']))
            if isinstance(details['defense']['findings'], list):
                for finding in details['defense']['findings']:
                    txt = json.dumps(finding).replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(f"• {txt}", styles['Normal']))
            else:
                clean_findings = str(details['defense']['findings'])[:800].replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
                story.append(Paragraph(f"<font face='Courier' size='8'>{clean_findings}</font>", styles['Normal']))
            
            story.append(Spacer(1, 20))
            story.append(Paragraph("-" * 100, styles['Normal']))
            
        doc.build(story)
        return filename, "Success"

# app/modules/reporting/exporters/pdf_exporter.py
"""PDF format exporter."""

from typing import Any, Dict
from io import BytesIO

from .base import BaseExporter


class PDFExporter(BaseExporter):
    """Export reports to PDF format."""

    def export(self, data: Dict[str, Any], filename: str) -> bytes:
        """Export data as PDF."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
        except ImportError:
            raise ImportError("reportlab not installed. Install with: pip install reportlab")

        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        if "title" in data:
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f4788"),
                spaceAfter=30,
                alignment=1,
            )
            story.append(Paragraph(data["title"], title_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Summary
        if "summary" in data:
            story.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
            story.append(Paragraph(data["summary"], styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))
        
        # Metadata
        if "metadata" in data:
            story.append(Paragraph("<b>Metadata</b>", styles["Heading2"]))
            meta_data = []
            for key, value in data["metadata"].items():
                meta_data.append([key, str(value)])
            if meta_data:
                meta_table = Table(meta_data, colWidths=[2 * inch, 4 * inch])
                meta_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ]))
                story.append(meta_table)
                story.append(Spacer(1, 0.2 * inch))
        
        # Results
        if "results" in data:
            story.append(PageBreak())
            story.append(Paragraph("<b>Results</b>", styles["Heading2"]))
            results = data["results"]
            if isinstance(results, dict):
                for key, value in results.items():
                    story.append(Paragraph(f"<b>{key}</b>", styles["Heading3"]))
                    story.append(Paragraph(str(value), styles["Normal"]))
                    story.append(Spacer(1, 0.1 * inch))
            else:
                story.append(Paragraph(str(results), styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))
        
        # Chunks
        if "chunks" in data and data["chunks"]:
            story.append(PageBreak())
            story.append(Paragraph("<b>Source Chunks</b>", styles["Heading2"]))
            for i, chunk in enumerate(data["chunks"], 1):
                story.append(Paragraph(f"<b>Chunk {i}</b>", styles["Heading3"]))
                chunk_text = chunk.get("text", str(chunk)) if isinstance(chunk, dict) else str(chunk)
                # Limit chunk preview to 500 chars
                if len(chunk_text) > 500:
                    chunk_text = chunk_text[:500] + "..."
                story.append(Paragraph(chunk_text, styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))
        
        doc.build(story)
        return output.getvalue()

    def get_extension(self) -> str:
        return "pdf"

    def get_mime_type(self) -> str:
        return "application/pdf"

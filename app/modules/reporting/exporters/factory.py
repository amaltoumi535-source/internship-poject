# app/modules/reporting/exporters/factory.py
"""Factory for creating exporters."""

from typing import Optional
from app.modules.infrastructure.logger import get_logger

from .base import BaseExporter
from .json_exporter import JSONExporter
from .markdown_exporter import MarkdownExporter
from .pdf_exporter import PDFExporter
from .docx_exporter import DOCXExporter
from .excel_exporter import ExcelExporter

logger = get_logger(__name__)


class ExporterFactory:
    """Factory for creating report exporters."""
    
    _exporters = {
        "json": JSONExporter,
        "md": MarkdownExporter,
        "markdown": MarkdownExporter,
        "pdf": PDFExporter,
        "docx": DOCXExporter,
        "xlsx": ExcelExporter,
        "excel": ExcelExporter,
    }

    @classmethod
    def get_exporter(cls, format: str) -> Optional[BaseExporter]:
        """Get exporter for the specified format."""
        format_lower = format.lower().strip()
        exporter_class = cls._exporters.get(format_lower)
        
        if not exporter_class:
            logger.warning(f"Unknown export format: {format}. Defaulting to JSON.")
            return JSONExporter()
        
        try:
            return exporter_class()
        except Exception as e:
            logger.error(f"Failed to create exporter for {format}: {e}")
            return JSONExporter()  # Fallback to JSON

    @classmethod
    def get_supported_formats(cls) -> list:
        """Get list of supported export formats."""
        return list(cls._exporters.keys())

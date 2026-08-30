# app/modules/reporting/exporters/json_exporter.py
"""JSON format exporter."""

import json
from typing import Any, Dict

from .base import BaseExporter


class JSONExporter(BaseExporter):
    """Export reports to JSON format."""

    def export(self, data: Dict[str, Any], filename: str) -> bytes:
        """Export data as JSON."""
        return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

    def get_extension(self) -> str:
        return "json"

    def get_mime_type(self) -> str:
        return "application/json"

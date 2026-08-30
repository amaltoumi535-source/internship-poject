# app/modules/reporting/exporters/markdown_exporter.py
"""Markdown format exporter."""

from typing import Any, Dict, List

from .base import BaseExporter


class MarkdownExporter(BaseExporter):
    """Export reports to Markdown format."""

    def export(self, data: Dict[str, Any], filename: str) -> bytes:
        """Export data as Markdown."""
        lines = []
        
        # Title
        if "title" in data:
            lines.append(f"# {data['title']}\n")
        
        # Summary
        if "summary" in data:
            lines.append(f"{data['summary']}\n")
        
        # Metadata
        if "metadata" in data:
            lines.append("## Metadata\n")
            meta = data["metadata"]
            for key, value in meta.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")
        
        # Content/Analysis
        if "content" in data:
            lines.append("## Content\n")
            lines.append(data["content"])
            lines.append("")
        
        # Results
        if "results" in data:
            lines.append("## Results\n")
            results = data["results"]
            if isinstance(results, dict):
                for key, value in results.items():
                    lines.append(f"### {key}\n")
                    lines.append(str(value))
                    lines.append("")
            else:
                lines.append(str(results))
                lines.append("")
        
        # Chunks
        if "chunks" in data and data["chunks"]:
            lines.append("## Source Chunks\n")
            for i, chunk in enumerate(data["chunks"], 1):
                lines.append(f"### Chunk {i}\n")
                if isinstance(chunk, dict):
                    lines.append(chunk.get("text", str(chunk)))
                else:
                    lines.append(str(chunk))
                lines.append("")
        
        return "\n".join(lines).encode("utf-8")

    def get_extension(self) -> str:
        return "md"

    def get_mime_type(self) -> str:
        return "text/markdown"

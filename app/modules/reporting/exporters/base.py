# app/modules/reporting/exporters/base.py
"""Abstract base class for report exporters."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseExporter(ABC):
    """Base interface all format-specific exporters must implement."""

    @abstractmethod
    def export(self, data: Dict[str, Any], filename: str) -> bytes:
        """Convert report data into the target format, returned as bytes."""
        raise NotImplementedError

    @abstractmethod
    def get_extension(self) -> str:
        """File extension for this format, without a leading dot (e.g. 'pdf')."""
        raise NotImplementedError

    @abstractmethod
    def get_mime_type(self) -> str:
        """MIME type to use in the HTTP response for this format."""
        raise NotImplementedError
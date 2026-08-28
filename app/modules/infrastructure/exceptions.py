"""
Application-specific exceptions with HTTP metadata.

FastAPI exception handlers can convert these to JSON responses.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class BaseAppException(Exception):
    """
    Base application exception.
    - status_code: HTTP status code to return
    - detail: message or payload
    - extra: optional dict for additional info
    """
    status_code: int = 500
    detail: str | Dict[str, Any] = "An error occurred"
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"error": True, "detail": self.detail}
        if self.extra:
            d["extra"] = self.extra
        return d


class NotFoundError(BaseAppException):
    def __init__(self, detail: str | Dict[str, Any] = "Resource not found", extra: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, detail=detail, extra=extra)


class AlreadyExistsError(BaseAppException):
    def __init__(self, detail: str | Dict[str, Any] = "Resource already exists", extra: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=409, detail=detail, extra=extra)


class ValidationError(BaseAppException):
    def __init__(self, detail: str | Dict[str, Any] = "Validation failed", extra: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=422, detail=detail, extra=extra)


class StorageError(BaseAppException):
    def __init__(self, detail: str | Dict[str, Any] = "Storage failure", extra: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, detail=detail, extra=extra)


class VectorizationError(BaseAppException):
    def __init__(self, detail: str | Dict[str, Any] = "Vectorization failed", extra: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, detail=detail, extra=extra)


class ExternalServiceError(BaseAppException):
    def __init__(self, detail: str | Dict[str, Any] = "External service error", extra: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=502, detail=detail, extra=extra)
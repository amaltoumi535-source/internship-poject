"""Ingestion package public API.

Exports:
- IngestionService: orchestrator for parsing + chunking
- router: FastAPI router for the /ingest endpoints
- parsers: subpackage with PDF/OCR/DOCX/chunker implementations
- schemas: pydantic models used by the endpoints
"""

from .service import IngestionService
from .routes import router
from . import parsers
from . import schemas

__all__ = [
    "IngestionService",
    "router",
    "parsers",
    "schemas",
]

def register(app):
    """
    Helper to register the ingestion router on a FastAPI app.

    Usage:
        from fastapi import FastAPI
        from app.modules.ingestion import register as register_ingestion
        app = FastAPI()
        register_ingestion(app)
    """
    app.include_router(router)
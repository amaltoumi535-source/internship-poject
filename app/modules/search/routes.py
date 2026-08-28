# app/modules/search/routes.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from . import service, schemas

router = APIRouter(prefix="/search", tags=["search"])

# Try to import a standard get_db dependency from your project. Adjust if your project uses a different path.
try:
    # common locations
    from app.db import get_db  # noqa: E402,F401
except Exception:
    try:
        from app.database import get_db  # noqa: E402,F401
    except Exception:
        # Fallback: raise helpful error at runtime if dependency missing
        def get_db():
            raise RuntimeError("Database dependency 'get_db' not found. Please provide a dependency that yields a SQLAlchemy Session.")


@router.get("/", response_model=schemas.SearchResponse)
def search_all(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    """
    Search all chunks for a query string (case-insensitive).
    """
    try:
        results, total = service.search_chunks_like(db, q, limit=limit, offset=offset)
        return {"total": total, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/doc/{document_id}", response_model=schemas.SearchResponse)
def search_document(document_id: int, q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    """
    Search within a single document's chunks.
    """
    try:
        results, total = service.search_chunks_in_document(db, document_id, q, limit=limit, offset=offset)
        return {"total": total, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
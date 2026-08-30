# app/modules/search/routes.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from . import service, schemas
from app.modules.auth.dependencies import get_current_user_id
from app.db import get_db

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=schemas.SearchResponse)
def search_all(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Search all of the requesting user's own document chunks.
    """
    try:
        results, total = service.search_chunks_like(db, q, user_id, limit=limit, offset=offset)
        return {"total": total, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/doc/{document_id}", response_model=schemas.SearchResponse)
def search_document(
    document_id: int,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Search within a single document's chunks — only if the user owns it.
    """
    try:
        results, total = service.search_chunks_in_document(db, document_id, q, user_id, limit=limit, offset=offset)
        return {"total": total, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
# app/modules/search/service.py
"""
Search service: simple case-insensitive SQL LIKE fallback search.
Swap in FTS5 or vector search later as needed.
"""

from typing import Tuple, List, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session


def _normalize_q(q: str) -> str:
    return q.strip().lower()


def _make_snippet(full_text: str, match_idx: int, length: int = 200) -> str:
    if full_text is None:
        return ""
    start = max(0, match_idx - 50)
    end = start + length
    snippet = full_text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if len(full_text) > end:
        snippet = snippet + "..."
    return snippet


def _row_get(row, name: str, pos: int):
    """
    Safely get a column value from a SQLAlchemy Row/RowMapping.
    Prefers named access via row._mapping; falls back to positional index.
    """
    if hasattr(row, "_mapping"):
        mapping = row._mapping
        return mapping.get(name)
    try:
        if isinstance(row, dict):
            return row.get(name)
    except Exception:
        pass
    try:
        return row[pos]
    except Exception:
        return None


def search_chunks_like(db: Session, q: str, limit: int = 10, offset: int = 0) -> Tuple[List[Dict], int]:
    """
    Perform a case-insensitive LIKE search on chunks.text.

    Returns (results, total). Each result is a dict matching ChunkResult schema:
      {id, document_id, chunk_index, snippet, score}
    Note: 'chunk_index' in the API output maps to the model's 'chunk_num' column.
    """
    q_norm = _normalize_q(q)
    if q_norm == "":
        return [], 0

    like_param = f"%{q_norm}%"

    count_sql = text(
        "SELECT COUNT(1) as cnt FROM chunks WHERE lower(text) LIKE :like"
    )
    rows_sql = text(
        "SELECT id, document_id, chunk_num, text FROM chunks "
        "WHERE lower(text) LIKE :like "
        "ORDER BY id LIMIT :limit OFFSET :offset"
    )

    total = db.execute(count_sql, {"like": like_param}).scalar() or 0
    raw = db.execute(rows_sql, {"like": like_param, "limit": limit, "offset": offset}).fetchall()

    results = []
    for row in raw:
        row_id = _row_get(row, "id", 0)
        doc_id = _row_get(row, "document_id", 1)
        chunk_idx = _row_get(row, "chunk_num", 2)
        text_val = _row_get(row, "text", 3) or ""
        match_idx = (text_val or "").lower().find(q_norm)
        if match_idx >= 0:
            snippet = _make_snippet(text_val, match_idx)
        else:
            snippet = (text_val or "")[:200]
        score = (text_val or "").lower().count(q_norm)
        results.append({
            "id": int(row_id) if row_id is not None else None,
            "document_id": int(doc_id) if doc_id is not None else None,
            "chunk_index": int(chunk_idx) if chunk_idx is not None else None,
            "snippet": snippet,
            "score": float(score)
        })

    return results, int(total)


def search_chunks_in_document(db: Session, document_id: int, q: str, limit: int = 10, offset: int = 0) -> Tuple[List[Dict], int]:
    """
    Search within a single document's chunks.
    """
    q_norm = _normalize_q(q)
    if q_norm == "":
        return [], 0
    like_param = f"%{q_norm}%"

    count_sql = text(
        "SELECT COUNT(1) as cnt FROM chunks WHERE document_id = :doc_id AND lower(text) LIKE :like"
    )
    rows_sql = text(
        "SELECT id, document_id, chunk_num, text FROM chunks "
        "WHERE document_id = :doc_id AND lower(text) LIKE :like "
        "ORDER BY id LIMIT :limit OFFSET :offset"
    )

    total = db.execute(count_sql, {"doc_id": document_id, "like": like_param}).scalar() or 0
    raw = db.execute(rows_sql, {"doc_id": document_id, "like": like_param, "limit": limit, "offset": offset}).fetchall()

    results = []
    for row in raw:
        row_id = _row_get(row, "id", 0)
        doc_id = _row_get(row, "document_id", 1)
        chunk_idx = _row_get(row, "chunk_num", 2)
        text_val = _row_get(row, "text", 3) or ""
        match_idx = (text_val or "").lower().find(q_norm)
        if match_idx >= 0:
            snippet = _make_snippet(text_val, match_idx)
        else:
            snippet = (text_val or "")[:200]
        score = (text_val or "").lower().count(q_norm)
        results.append({
            "id": int(row_id) if row_id is not None else None,
            "document_id": int(doc_id) if doc_id is not None else None,
            "chunk_index": int(chunk_idx) if chunk_idx is not None else None,
            "snippet": snippet,
            "score": float(score)
        })

    return results, int(total)
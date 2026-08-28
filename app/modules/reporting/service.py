# app/modules/reporting/service.py
import logging
from typing import Tuple, List, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)


def _row_get(row, name: str, pos: int = 0):
    if hasattr(row, "_mapping"):
        return row._mapping.get(name)
    try:
        if isinstance(row, dict):
            return row.get(name)
    except Exception:
        pass
    try:
        return row[pos]
    except Exception:
        return None


def overview(db: Session) -> Dict:
    """
    Return site-wide metrics. Defensive about missing tables/columns.
    """
    total_docs = 0
    total_chunks = 0
    last_ingest = None

    try:
        total_docs = int(db.execute(text("SELECT COUNT(1) FROM documents")).scalar() or 0)
    except Exception:
        logger.exception("overview: failed to count documents")
        total_docs = 0

    try:
        total_chunks = int(db.execute(text("SELECT COUNT(1) FROM chunks")).scalar() or 0)
    except Exception:
        logger.exception("overview: failed to count chunks")
        total_chunks = 0

    avg_chunks = round((float(total_chunks) / float(total_docs)) if total_docs else 0.0, 3)

    try:
        val = db.execute(text("SELECT MAX(created_at) FROM documents")).scalar()
        if isinstance(val, datetime):
            last_ingest = val
        elif isinstance(val, str):
            try:
                last_ingest = datetime.fromisoformat(val)
            except ValueError:
                logger.warning("overview: could not parse last_ingest_at value: %s", val)
    except Exception:
        logger.exception("overview: failed to get last_ingest_at")
        last_ingest = None

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "avg_chunks_per_document": avg_chunks,
        "last_ingest_at": last_ingest,
    }

def doc_report(db: Session, document_id: int, sample_limit: int = 3) -> Dict:
    """
    Per-document stats and sample snippets. Defensive queries.
    """
    try:
        chunk_count = int(db.execute(
            text("SELECT COUNT(1) FROM chunks WHERE document_id = :doc_id"),
            {"doc_id": document_id}
        ).scalar() or 0)
    except Exception:
        logger.exception("doc_report: failed to count chunks for document_id=%s", document_id)
        chunk_count = 0

    try:
        avg_len = db.execute(
            text("SELECT AVG(LENGTH(text)) FROM chunks WHERE document_id = :doc_id"),
            {"doc_id": document_id}
        ).scalar() or 0
        avg_len = float(avg_len) if avg_len is not None else 0.0
    except Exception:
        logger.exception("doc_report: failed to compute avg_chunk_length for document_id=%s", document_id)
        avg_len = 0.0

    snippets: List[str] = []
    try:
        rows = db.execute(
            text("SELECT text FROM chunks WHERE document_id = :doc_id ORDER BY id LIMIT :limit"),
            {"doc_id": document_id, "limit": sample_limit}
        ).fetchall()

        for r in rows:
            txt = _row_get(r, "text", 0)
            if txt:
                snippets.append((txt[:300] + "...") if len(txt) > 300 else txt)
    except Exception:
        logger.exception("doc_report: failed to fetch sample snippets for document_id=%s", document_id)
        snippets = []

    title = None
    try:
        # Note: documents table has no 'title' column — 'filename' is the real
        # identifying field, so we surface that as the report's "title".
        title = db.execute(text("SELECT filename FROM documents WHERE id = :doc_id"), {"doc_id": document_id}).scalar()
    except Exception:
        logger.exception("doc_report: failed to fetch title for document_id=%s", document_id)
        title = None

    return {
        "document_id": int(document_id),
        "title": title,
        "chunk_count": chunk_count,
        "avg_chunk_length": float(avg_len),
        "sample_snippets": snippets,
    }


def export_documents(db: Session, limit: int = 1000, offset: int = 0) -> Tuple[List[Dict], int]:
    """
    Export documents table rows (defensive). Returns (rows, total).
    """
    total = 0
    results: List[Dict] = []

    try:
        total = int(db.execute(text("SELECT COUNT(1) FROM documents")).scalar() or 0)
    except Exception:
        logger.exception("export_documents: failed to count documents")
        total = 0

    try:
        # 'filename' is the real column; exposed as "title" in the output for
        # API consistency with doc_report().
        rows = db.execute(
            text("SELECT id, filename, created_at FROM documents ORDER BY id LIMIT :limit OFFSET :offset"),
            {"limit": limit, "offset": offset}
        ).fetchall()
        for r in rows:
            mapping = r._mapping if hasattr(r, "_mapping") else None
            rid = mapping.get("id") if mapping else (r[0] if len(r) > 0 else None)
            title = mapping.get("filename") if mapping else (r[1] if len(r) > 1 else None)
            created_at = mapping.get("created_at") if mapping else (r[2] if len(r) > 2 else None)
            results.append({"id": rid, "title": title, "created_at": created_at})
    except Exception:
        logger.exception("export_documents: full-column query failed, falling back to id-only")
        try:
            rows = db.execute(
                text("SELECT id FROM documents ORDER BY id LIMIT :limit OFFSET :offset"),
                {"limit": limit, "offset": offset}
            ).fetchall()
            for r in rows:
                rid = _row_get(r, "id", 0)
                results.append({"id": rid})
        except Exception:
            logger.exception("export_documents: id-only fallback query also failed")
            results = []

    return results, int(total)
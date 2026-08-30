# app/modules/reporting/routes.py
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

from . import service, schemas
from .exporters.factory import ExporterFactory
from app.modules.auth.dependencies import get_current_user_id
from app.db import get_db

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/overview", response_model=schemas.ReportOverview)
def get_overview(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    try:
        data = service.overview(db, user_id)
        return data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/doc/{document_id}", response_model=schemas.DocReport)
def get_doc_report(
    document_id: int,
    sample_limit: int = Query(3, ge=0, le=20),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        data = service.doc_report(db, document_id, user_id, sample_limit=sample_limit)
        return data
    except PermissionError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/export")
def export_documents(
    format: Optional[str] = Query("json", pattern="^(json|csv)$"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Export the requesting user's own documents as JSON or CSV.
    """
    try:
        rows, total = service.export_documents(db, user_id, limit=limit, offset=offset)
        if format == "json":
            return {"total": total, "rows": rows}
        import io, csv
        buf = io.StringIO()
        writer = csv.writer(buf)
        header = ["id"]
        if any("title" in (r or {}) for r in rows):
            header.append("title")
        if any("created_at" in (r or {}) for r in rows):
            header.append("created_at")
        writer.writerow(header)
        for r in rows:
            row = []
            for col in header:
                row.append(r.get(col))
            writer.writerow(row)
        content = buf.getvalue()
        return Response(content=content, media_type="text/csv")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _doc_report_to_export_payload(doc_data: dict) -> dict:
    return {
        "title": f"Document Report: {doc_data.get('title') or doc_data.get('document_id')}",
        "summary": f"{doc_data.get('chunk_count', 0)} chunks, "
                   f"average length {doc_data.get('avg_chunk_length', 0):.1f} characters.",
        "metadata": {
            "Document ID": doc_data.get("document_id"),
            "Chunk Count": doc_data.get("chunk_count"),
            "Avg Chunk Length": doc_data.get("avg_chunk_length"),
        },
        "chunks": [{"text": s} for s in doc_data.get("sample_snippets", [])],
    }


@router.get("/doc/{document_id}/export")
def export_doc_report(
    document_id: int,
    format: str = Query("pdf", pattern="^(json|md|markdown|pdf|docx|xlsx|excel)$"),
    sample_limit: int = Query(3, ge=0, le=20),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        doc_data = service.doc_report(db, document_id, user_id, sample_limit=sample_limit)
    except PermissionError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to build report: {exc}")

    payload = _doc_report_to_export_payload(doc_data)
    exporter = ExporterFactory.get_exporter(format)

    try:
        content = exporter.export(payload, filename=f"document_{document_id}_report")
    except ImportError as exc:
        raise HTTPException(status_code=501, detail=f"Export format '{format}' unavailable: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}")

    ext = exporter.get_extension()
    mime = exporter.get_mime_type()
    filename = f"document_{document_id}_report.{ext}"

    return Response(
        content=content,
        media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
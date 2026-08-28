# app/modules/reporting/routes.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from . import service, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

# reuse your project's get_db like in search module
try:
    from app.db import get_db  # noqa: E402,F401
except Exception:
    try:
        from app.database import get_db  # noqa: E402,F401
    except Exception:
        def get_db():
            raise RuntimeError("Database dependency 'get_db' not found. Please provide get_db.")


@router.get("/overview", response_model=schemas.ReportOverview)
def get_overview(db: Session = Depends(get_db)):
    try:
        data = service.overview(db)
        return data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/doc/{document_id}", response_model=schemas.DocReport)
def get_doc_report(document_id: int, sample_limit: int = Query(3, ge=0, le=20), db: Session = Depends(get_db)):
    try:
        data = service.doc_report(db, document_id, sample_limit=sample_limit)
        return data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/export")
def export_documents(format: Optional[str] = Query("json", pattern="^(json|csv)$"),
                      limit: int = Query(1000, ge=1, le=10000),
                      offset: int = Query(0, ge=0),
                      db: Session = Depends(get_db)):
    """
    Export documents as JSON or CSV. CSV is returned as text/csv.
    """
    try:
        rows, total = service.export_documents(db, limit=limit, offset=offset)
        if format == "json":
            return {"total": total, "rows": rows}
        # build CSV string
        import io, csv
        buf = io.StringIO()
        writer = csv.writer(buf)
        # write header based on available keys
        header = ["id"]
        # if any row has title or created_at, include them
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
        from fastapi.responses import Response
        return Response(content=content, media_type="text/csv")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
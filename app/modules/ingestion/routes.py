from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
import logging

from app.modules.ingestion.service import IngestionService
from app.modules.ingestion.schemas import IngestResponse, ExtractionResult, ExtractionMetadata, PageModel, ChunkModel
from app.modules.storage.repository import StorageRepository
from app.modules.search.indexing import index_document
from app.modules.auth.dependencies import get_current_user_id
from app.modules.auth.models import UserDocument
from app.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingestion"])
service = IngestionService()
repo = StorageRepository()


def _user_owns_document(db: Session, document_id: int, user_id: str) -> bool:
    return db.query(UserDocument).filter(
        UserDocument.document_id == document_id,
        UserDocument.user_id == user_id,
    ).first() is not None


@router.post("/", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    lang: str = Form("multi"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        result = service.ingest(file, lang=lang)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    extraction = result.get("extraction", {})
    pages = [PageModel(**p) for p in extraction.get("pages", [])]
    metadata = ExtractionMetadata(**extraction.get("metadata", {}))
    extraction_model = ExtractionResult(text=extraction.get("text", ""), metadata=metadata, pages=pages)
    chunks = [ChunkModel(**c) for c in result.get("chunks", [])]

    try:
        document_id = repo.create_document(file, ingestion_result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion OK mais storage a échoué: {e}")

    # Link this document to the uploading user
    ownership = UserDocument(user_id=user_id, document_id=document_id)
    db.add(ownership)
    db.commit()

    try:
        index_document(document_id, user_id=user_id)
    except Exception as e:
        logger.warning("Semantic indexing failed for document %d: %s", document_id, e)

    resp = IngestResponse(
        document_id=document_id,
        filename=result.get("filename"),
        parser=result.get("parser"),
        extraction=extraction_model,
        chunks=chunks,
        chunks_count=result.get("chunks_count", len(chunks))
    )
    return JSONResponse(status_code=200, content=resp.dict())


@router.delete("/{document_id}")
async def delete_ingested_document(
    document_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if not _user_owns_document(db, document_id, user_id):
        raise HTTPException(status_code=404, detail="Document not found")

    deleted = repo.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    db.query(UserDocument).filter(
        UserDocument.document_id == document_id,
        UserDocument.user_id == user_id,
    ).delete()
    db.commit()

    return {"deleted": True, "document_id": document_id}


@router.get("/{document_id}/file")
async def get_document_file(
    document_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if not _user_owns_document(db, document_id, user_id):
        raise HTTPException(status_code=404, detail="File not found")

    doc = repo.get_document(document_id)
    if not doc or not doc.stored_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(doc.stored_path, filename=doc.filename, content_disposition_type="inline")
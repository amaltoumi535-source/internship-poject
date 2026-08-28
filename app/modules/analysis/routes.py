"""FastAPI router for analysis endpoints."""

from fastapi import APIRouter, HTTPException
from typing import Any
from app.modules.analysis import schemas
from app.modules.infrastructure.logger import get_logger
from app.modules.analysis.service import AnalysisService

logger = get_logger(__name__)
router = APIRouter(prefix="/analyze", tags=["analysis"])

_service = AnalysisService()


@router.post("/text", response_model=schemas.AnalyzeTextResponse)
def analyze_text(req: schemas.AnalyzeTextRequest) -> Any:
    try:
        result = _service.analyze_text(
            text=req.text,
            summarize=req.summarize,
            summary_ratio=req.summary_ratio,
            detect_language=req.detect_language,
            extract_entities=req.extract_entities,
            readability=req.readability,
        )
        summary = None
        if result.get("summary"):
            summary = schemas.SummaryResult(summary=result["summary"]["summary"], method=result["summary"].get("method", "extractive"))
        language = None
        if result.get("language"):
            language = schemas.LanguageResult(language=result["language"].get("language"), confidence=result["language"].get("confidence"))
        entities = [schemas.EntityItem(**e) for e in (result.get("entities") or [])]
        readability = None
        if result.get("readability"):
            readability = schemas.ReadabilityResult(**result["readability"])
        return schemas.AnalyzeTextResponse(summary=summary, language=language, entities=entities, readability=readability)
    except Exception as exc:
        logger.exception("analyze_text failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/document/{document_id}", response_model=schemas.AnalyzeDocumentResponse)
def analyze_document(document_id: int, opts: schemas.AnalyzeDocumentRequest):
    try:
        # lazy import storage repository to avoid hard dependency on startup
        try:
            from app.modules.storage.repository import StorageRepository
        except Exception as e:
            raise HTTPException(status_code=500, detail="StorageRepository not available: " + str(e))

        repo = StorageRepository()
        try:
            out = _service.analyze_document(repo, document_id, opts.model_dump())
        except ValueError:
            raise HTTPException(status_code=404, detail="Document not found")
        except RuntimeError as rexc:
            # embedding model missing or other runtime issues
            raise HTTPException(status_code=503, detail=str(rexc))

        # Build chunk responses
        chunk_models = []
        for c in out["chunks"]:
            chunk_models.append(schemas.ChunkAnalysis(
                chunk_id=c.get("chunk_id"),
                chunk_num=c.get("chunk_num"),
                text_preview=c.get("text_preview"),
                summary=c.get("summary"),
                score=c.get("score"),
            ))

        language_model = None
        if out.get("language"):
            language_model = schemas.LanguageResult(language=out["language"].get("language"), confidence=out["language"].get("confidence"))

        entity_models = [schemas.EntityItem(**e) for e in (out.get("entities") or [])]

        return schemas.AnalyzeDocumentResponse(
            document_id=out["document_id"],
            document_filename=out.get("document_filename"),
            document_summary=out.get("document_summary"),
            chunks=chunk_models,
            language=language_model,
            entities=entity_models,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("analyze_document failed")
        raise HTTPException(status_code=500, detail=str(exc))
from pathlib import Path
import logging
from langchain_core.tools import tool
from .service import IngestionService
from app.modules.storage.repository import StorageRepository
from app.modules.search.indexing import index_document

logger = logging.getLogger(__name__)

_service = IngestionService()
_repo = StorageRepository()


class _PathUpload:
    """Wrapper minimal imitant UploadFile (filename + file), pour que IngestionService.ingest()
    accepte un chemin disque venant d'un tool LLM plutôt qu'un objet FastAPI UploadFile."""
    def __init__(self, path: str):
        p = Path(path)
        self.filename = p.name
        self.file = open(p, "rb")


@tool
def ingest_file_tool(file_path: str, lang: str = "multi") -> dict:
    """Ingère un fichier depuis un chemin disque (PDF, DOCX, image, texte),
    l'extrait, le découpe en chunks, le persiste, et retourne son document_id."""
    upload = _PathUpload(file_path)
    try:
        result = _service.ingest(upload, lang=lang)
    except Exception as e:
        return {"error": f"ingestion failed: {e}"}
    finally:
        upload.file.close()

    try:
        document_id = _repo.create_document(file_path, ingestion_result=result)
    except Exception as e:
        return {"error": f"ingestion OK mais storage a échoué: {e}"}

    try:
        index_document(document_id)
    except Exception as e:
        logger.warning("Semantic indexing failed for document %d: %s", document_id, e)

    return {
        "document_id": document_id,
        "filename": result.get("filename"),
        "parser": result.get("parser"),
        "chunks_count": result.get("chunks_count"),
    }


INGESTION_TOOLS = [ingest_file_tool]

from typing import Optional
from langchain_core.tools import tool
from .service import AnalysisService
from app.modules.storage.repository import StorageRepository

_service = AnalysisService()
_repo = StorageRepository()


@tool
def analyze_text_tool(text: str, extract_entities: bool = False, readability: bool = False) -> dict:
    """Analyse un texte brut fourni directement : résumé, langue, entités, lisibilité."""
    return _service.analyze_text(text, extract_entities=extract_entities, readability=readability)


@tool
def analyze_document_tool(
    document_id: int,
    extract_entities: bool = False,
    summarize_document: bool = True,
    detect_language: bool = True,
    query: Optional[str] = None,
    include_chunk_previews: bool = False,
) -> dict:
    """Analyse un document stocké par ID. Retourne un résumé, langue, entités, et le nombre
    de chunks (pas leur contenu détaillé, sauf si include_chunk_previews=True — à éviter
    pour les documents volumineux, ça alourdit fortement la réponse)."""
    opts = {
        "extract_entities": extract_entities,
        "summarize_document": summarize_document,
        "detect_language": detect_language,
        "query": query,
    }
    try:
        result = _service.analyze_document(_repo, document_id, opts)
    except ValueError as e:
        return {"error": str(e)}
    except RuntimeError as e:
        return {"error": f"embeddings indisponibles: {e}"}

    chunks = result.get("chunks", [])
    result["chunks_count"] = len(chunks)
    if not include_chunk_previews:
        result.pop("chunks", None)
    return result


ANALYSIS_TOOLS = [analyze_text_tool, analyze_document_tool]

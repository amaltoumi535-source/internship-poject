from langchain_core.tools import tool
from app.modules.storage.database import SessionLocal
from app.modules.analysis.service import AnalysisService
from app.modules.storage.vectorstore import VectorStoreAdapter
from . import service as search_service
from contextvars import ContextVar
import logging

logger = logging.getLogger(__name__)

_analysis = AnalysisService()
_vectorstore = VectorStoreAdapter()

MAX_CHUNK_PREVIEW_CHARS = 300

# Set by orchestrator/routes.py before invoking the agent for a given request,
# so every tool call in this request's chain knows which user is asking —
# without needing the LLM to pass user_id as an argument itself.
current_user_id: ContextVar[str] = ContextVar("current_user_id", default=None)


def _truncate(text: str, max_chars: int = MAX_CHUNK_PREVIEW_CHARS) -> str:
    if not text:
        return text
    return text if len(text) <= max_chars else text[:max_chars] + "..."


def _flatten_chroma_results(raw: dict) -> list:
    """ChromaDB's collection.query() returns parallel lists nested one level
    deep (one outer list per query embedding). We send a single query, so we
    unwrap index [0] from each list and zip them into a flat list of dicts."""
    ids = (raw.get("ids") or [[]])[0]
    documents = (raw.get("documents") or [[]])[0]
    metadatas = (raw.get("metadatas") or [[]])[0]
    distances = (raw.get("distances") or [[]])[0]

    flattened = []
    for i in range(len(ids)):
        flattened.append({
            "id": ids[i] if i < len(ids) else None,
            "document_text": documents[i] if i < len(documents) else "",
            "metadata": metadatas[i] if i < len(metadatas) else {},
            "distance": distances[i] if i < len(distances) else 1,
        })
    return flattened


@tool
def search_chunks_tool(query: str, limit: int = 10, offset: int = 0) -> dict:
    """Recherche des chunks contenant une requête textuelle, sur tous les documents.
    Recherche exacte insensible à la casse (LIKE), rapide et utile pour des termes exacts."""
    user_id = current_user_id.get()
    if not user_id:
        return {"error": "no authenticated user context", "results": [], "total": 0, "search_type": "literal"}

    session = SessionLocal()
    try:
        results, total = search_service.search_chunks_like(session, query, user_id, limit=limit, offset=offset)
        return {"results": results, "total": total, "search_type": "literal"}
    finally:
        session.close()


@tool
def search_chunks_in_document_tool(document_id: int, query: str, limit: int = 10, offset: int = 0) -> dict:
    """Recherche des chunks contenant une requête textuelle, à l'intérieur d'un document précis.
    Recherche exacte (LIKE), utile pour affiner dans un document connu."""
    user_id = current_user_id.get()
    if not user_id:
        return {"error": "no authenticated user context", "results": [], "total": 0, "search_type": "literal"}

    session = SessionLocal()
    try:
        results, total = search_service.search_chunks_in_document(session, document_id, query, user_id, limit=limit, offset=offset)
        return {"results": results, "total": total, "search_type": "literal"}
    finally:
        session.close()


@tool
def semantic_search_tool(query: str, top_k: int = 5) -> dict:
    """Recherche sémantique/vectorielle sur tous les documents.
    Utilise le sens/contexte de la requête, pas seulement les mots exacts.
    Idéal pour des questions ouvertes, paraphrases, ou chercher du contenu par thème."""
    user_id = current_user_id.get()
    if not user_id:
        return {"error": "no authenticated user context", "results": [], "total": 0, "search_type": "semantic"}

    try:
        query_embedding = _analysis.embed_texts([query])[0]
        # Fetch extra results before filtering by user_id, since ChromaDB's
        # top_k applies before our filter — filtering after could otherwise
        # return fewer than top_k results even when the user has enough matches.
        raw_results = _vectorstore.query("document_chunks", query_embedding, top_k=top_k * 3)
        flattened = _flatten_chroma_results(raw_results)

        user_results = [
            r for r in flattened
            if r.get("metadata", {}).get("user_id") == user_id
        ][:top_k]

        if not user_results:
            return {"results": [], "total": 0, "search_type": "semantic"}

        formatted_results = []
        for i, result in enumerate(user_results):
            formatted_results.append({
                "rank": i + 1,
                "id": result.get("id"),
                "text": _truncate(result.get("document_text", "")),
                "metadata": result.get("metadata", {}),
                "distance": result.get("distance", 0),
                "similarity_score": 1 - result.get("distance", 1),
            })

        return {"results": formatted_results, "total": len(formatted_results), "search_type": "semantic"}

    except Exception as e:
        logger.error("Semantic search failed: %s", e)
        return {"error": str(e), "results": [], "total": 0, "search_type": "semantic"}


@tool
def semantic_search_in_document_tool(document_id: int, query: str, top_k: int = 5) -> dict:
    """Recherche sémantique/vectorielle à l'intérieur d'un document précis.
    Comprend le contexte et le sens, utile pour explorer un document par thème."""
    user_id = current_user_id.get()
    if not user_id:
        return {"error": "no authenticated user context", "results": [], "total": 0, "search_type": "semantic"}

    try:
        query_embedding = _analysis.embed_texts([query])[0]
        raw_results = _vectorstore.query("document_chunks", query_embedding, top_k=top_k * 3)
        flattened = _flatten_chroma_results(raw_results)

        if not flattened:
            return {"results": [], "total": 0, "search_type": "semantic"}

        filtered_results = [
            r for r in flattened
            if r.get("metadata", {}).get("document_id") == document_id
            and r.get("metadata", {}).get("user_id") == user_id
        ][:top_k]

        formatted_results = []
        for i, result in enumerate(filtered_results):
            formatted_results.append({
                "rank": i + 1,
                "id": result.get("id"),
                "text": _truncate(result.get("document_text", "")),
                "metadata": result.get("metadata", {}),
                "distance": result.get("distance", 0),
                "similarity_score": 1 - result.get("distance", 1),
            })

        return {"results": formatted_results, "total": len(formatted_results), "search_type": "semantic"}

    except Exception as e:
        logger.error("Semantic search in document failed: %s", e)
        return {"error": str(e), "results": [], "total": 0, "search_type": "semantic"}


SEARCH_TOOLS = [
    search_chunks_tool,
    search_chunks_in_document_tool,
    semantic_search_tool,
    semantic_search_in_document_tool,
]
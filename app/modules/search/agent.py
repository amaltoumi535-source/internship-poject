from langchain_core.tools import tool
from app.modules.storage.database import SessionLocal
from app.modules.analysis.service import AnalysisService
from app.modules.storage.vectorstore import VectorStoreAdapter
from . import service as search_service
import logging

logger = logging.getLogger(__name__)

_analysis = AnalysisService()
_vectorstore = VectorStoreAdapter()


@tool
def search_chunks_tool(query: str, limit: int = 10, offset: int = 0) -> dict:
    """Recherche des chunks contenant une requête textuelle, sur tous les documents.
    Recherche exacte insensible à la casse (LIKE), rapide et utile pour des termes exacts."""
    session = SessionLocal()
    try:
        results, total = search_service.search_chunks_like(session, query, limit=limit, offset=offset)
        return {"results": results, "total": total, "search_type": "literal"}
    finally:
        session.close()


@tool
def search_chunks_in_document_tool(document_id: int, query: str, limit: int = 10, offset: int = 0) -> dict:
    """Recherche des chunks contenant une requête textuelle, à l'intérieur d'un document précis.
    Recherche exacte (LIKE), utile pour affiner dans un document connu."""
    session = SessionLocal()
    try:
        results, total = search_service.search_chunks_in_document(session, document_id, query, limit=limit, offset=offset)
        return {"results": results, "total": total, "search_type": "literal"}
    finally:
        session.close()


@tool
def semantic_search_tool(query: str, top_k: int = 5) -> dict:
    """Recherche sémantique/vectorielle sur tous les documents.
    Utilise le sens/contexte de la requête, pas seulement les mots exacts.
    Idéal pour des questions ouvertes, paraphrases, ou chercher du contenu par thème."""
    try:
        # Embed the query
        query_embedding = _analysis.embed_texts([query])[0]
        
        # Query ChromaDB across all documents
        raw_results = _vectorstore.query("document_chunks", query_embedding, top_k=top_k)
        
        if not raw_results:
            return {"results": [], "total": 0, "search_type": "semantic"}
        
        # Format results for consistency with LIKE search output
        formatted_results = []
        for i, result in enumerate(raw_results):
            formatted_results.append({
                "rank": i + 1,
                "id": result.get("id"),
                "text": result.get("document_text", ""),
                "metadata": result.get("metadata", {}),
                "distance": result.get("distance", 0),  # cosine distance (lower = more similar)
                "similarity_score": 1 - result.get("distance", 1),  # convert to similarity (0-1, higher = more similar)
            })
        
        return {"results": formatted_results, "total": len(formatted_results), "search_type": "semantic"}
    
    except Exception as e:
        logger.error("Semantic search failed: %s", e)
        return {"error": str(e), "results": [], "total": 0, "search_type": "semantic"}


@tool
def semantic_search_in_document_tool(document_id: int, query: str, top_k: int = 5) -> dict:
    """Recherche sémantique/vectorielle à l'intérieur d'un document précis.
    Comprend le contexte et le sens, utile pour explorer un document par thème."""
    try:
        # Embed the query
        query_embedding = _analysis.embed_texts([query])[0]
        
        # Query ChromaDB across all documents
        raw_results = _vectorstore.query("document_chunks", query_embedding, top_k=top_k * 2)  # fetch extra, filter after
        
        if not raw_results:
            return {"results": [], "total": 0, "search_type": "semantic"}
        
        # Filter by document_id
        filtered_results = [
            r for r in raw_results 
            if r.get("metadata", {}).get("document_id") == document_id
        ][:top_k]
        
        # Format results
        formatted_results = []
        for i, result in enumerate(filtered_results):
            formatted_results.append({
                "rank": i + 1,
                "id": result.get("id"),
                "text": result.get("document_text", ""),
                "metadata": result.get("metadata", {}),
                "distance": result.get("distance", 0),
                "similarity_score": 1 - result.get("distance", 1), # type: ignore
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
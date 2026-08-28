from langchain_core.tools import tool
from .repository import StorageRepository

_repo = StorageRepository()


@tool
def list_documents_tool(limit: int = 50, offset: int = 0) -> list[dict]:
    """Liste les documents stockés, avec pagination."""
    docs = _repo.list_documents(limit=limit, offset=offset)
    return [{"id": d.id, "filename": d.filename, "created_at": str(d.created_at)} for d in docs]


@tool
def get_document_tool(document_id: int) -> dict:
    """Récupère un document stocké par son ID, avec le nombre de chunks."""
    doc = _repo.get_document(document_id)
    if not doc:
        return {"error": f"document {document_id} not found"}
    return {
        "id": doc.id,
        "filename": doc.filename,
        "stored_path": doc.stored_path,
        "chunks_count": len(doc.chunks),
    }


@tool
def delete_document_tool(document_id: int, remove_file: bool = True) -> dict:
    """Supprime un document stocké et ses chunks associés."""
    ok = _repo.delete_document(document_id, remove_file=remove_file)
    return {"deleted": ok}


STORAGE_TOOLS = [list_documents_tool, get_document_tool, delete_document_tool]
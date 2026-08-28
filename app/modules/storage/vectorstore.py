"""Vector store adapter for storage module.

This module attempts to use chromadb if available. If chromadb is not installed
and you call vectorization functions, it raises a clear ImportError instructing
how to install the dependency.

The adapter expects you will pass embeddings as lists of floats and metadata
that includes document_id and chunk_id for traceability.

Note: If you plan to use LangChain vectorstore integrations later (Chroma/FAISS),
you can add helper methods to convert stored embeddings into LangChain wrappers.
"""

import os
from typing import List, Dict, Any, Optional

from app.config import get_settings
from app.modules.infrastructure.utils import ensure_dir

settings = get_settings()

# Try to import chromadb; provide clear message if missing
try:
    import chromadb
    _HAS_CHROMA = True
except Exception:
    chromadb = None
    _HAS_CHROMA = False


class VectorStoreAdapter:
    """
    Simple wrapper around chromadb collection. Uses persistent directory under DATA_DIR by default.
    Methods:
      - ensure_collection(name)
      - upsert(collection_name, records) where records are dicts:
          {'id': str, 'embedding': List[float], 'metadata': {...}, 'document_text': '...'}
      - query(collection_name, query_embedding, top_k=5, where=None)
    """

    def __init__(self, persist_directory: Optional[str] = None):
        if not _HAS_CHROMA:
            raise ImportError(
                "chromadb is not installed. Install with: pip install chromadb\n"
                "Or use an alternative vector store implementation."
            )

        # default persistence directory under configured DATA_DIR
        persist_dir = persist_directory or os.path.join(os.getcwd(), settings.data_dir or "data", "chromadb")
        ensure_dir(persist_dir)
        self.persist_dir = persist_dir

        # Create a persistent local client (chromadb >= 0.4 API)
        self.client = chromadb.PersistentClient(path=self.persist_dir) # pyright: ignore[reportOptionalMemberAccess]
        self._collections: Dict[str, Any] = {}

    def ensure_collection(self, name: str):
        if name in self._collections:
            return self._collections[name]
        col = self.client.get_or_create_collection(name=name)
        self._collections[name] = col
        return col

    def upsert(self, collection_name: str, records: List[Dict[str, Any]]):
        """
        Upsert records into collection. Each record must contain:
          - id: str
          - embedding: List[float]
          - metadata: dict (should include document_id, chunk_id)
          - document_text: str
        """
        col = self.ensure_collection(collection_name)
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        for r in records:
            ids.append(str(r["id"]))
            embeddings.append(r["embedding"])
            metadatas.append(r.get("metadata", {}))
            documents.append(r.get("document_text", ""))
        # Prefer upsert if available (avoids duplicate-id errors); fall back to add.
        if hasattr(col, "upsert"):
            col.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
        else:
            col.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

        # Note: PersistentClient auto-persists to disk; no manual .persist() call needed
        # or available in modern chromadb versions.

    def query(self, collection_name: str, query_embedding: List[float], top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        col = self.ensure_collection(collection_name)
        results = col.query(query_embeddings=[query_embedding], n_results=top_k, where=where)
        return results # pyright: ignore[reportReturnType]
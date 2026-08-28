"""Shared indexing logic: embeds a document's chunks and stores them in the vector store.
Used by ingestion (index new documents automatically) and by the one-time backfill
script (index documents that existed before semantic search was added).
"""

import logging

from app.modules.analysis.service import AnalysisService
from app.modules.storage.repository import StorageRepository
from app.modules.storage.vectorstore import VectorStoreAdapter

logger = logging.getLogger(__name__)

COLLECTION_NAME = "document_chunks"

_analysis = AnalysisService()
_vectorstore = VectorStoreAdapter()


def index_document(document_id: int) -> int:
    """Embed all chunks of a document and upsert them into the vector store.
    Returns the number of chunks indexed. Safe to call multiple times (upsert, not add)."""
    repo = StorageRepository()
    doc = repo.get_document(document_id)
    if not doc:
        raise ValueError(f"document {document_id} not found")

    chunks = list(doc.chunks or [])
    if not chunks:
        return 0

    texts = [c.text for c in chunks]
    embeddings = _analysis.embed_texts(texts)

    records = []
    for chunk, embedding in zip(chunks, embeddings):
        records.append({
            "id": f"{document_id}_{chunk.chunk_id}",
            "embedding": embedding,
            "metadata": {
                "document_id": document_id,
                "chunk_id": chunk.chunk_id,
                "filename": doc.filename,
            },
            "document_text": chunk.text,
        })

    _vectorstore.upsert(COLLECTION_NAME, records)
    logger.info("Indexed %d chunks for document %d", len(records), document_id)
    return len(records)

"""Shared indexing logic: embeds a document's chunks and stores them in the vector store.
Used by ingestion (index new documents automatically) and by the one-time backfill
script (index documents that existed before semantic search was added).
"""

import logging
from typing import Optional

from app.modules.analysis.service import AnalysisService
from app.modules.storage.repository import StorageRepository
from app.modules.storage.vectorstore import VectorStoreAdapter
from app.modules.storage.database import SessionLocal
from sqlalchemy import text

logger = logging.getLogger(__name__)

COLLECTION_NAME = "document_chunks"

_analysis = AnalysisService()
_vectorstore = VectorStoreAdapter()


def _get_owner_user_id(document_id: int) -> Optional[str]:
    """Look up the owning user_id for a document from user_documents."""
    session = SessionLocal()
    try:
        row = session.execute(
            text("SELECT user_id FROM user_documents WHERE document_id = :doc_id LIMIT 1"),
            {"doc_id": document_id}
        ).first()
        return row[0] if row else None
    finally:
        session.close()


def index_document(document_id: int, user_id: Optional[str] = None) -> int:
    """Embed all chunks of a document and upsert them into the vector store.
    Returns the number of chunks indexed. Safe to call multiple times (upsert, not add).

    user_id is stored in each chunk's metadata so semantic search can be scoped
    to the owning user. If not passed explicitly, it's looked up from
    user_documents (used by the backfill script for pre-existing documents)."""
    repo = StorageRepository()
    doc = repo.get_document(document_id)
    if not doc:
        raise ValueError(f"document {document_id} not found")

    if user_id is None:
        user_id = _get_owner_user_id(document_id)
        if user_id is None:
            logger.warning("No owner found for document %d — indexing without user_id filter", document_id)

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
                "user_id": user_id,
            },
            "document_text": chunk.text,
        })

    _vectorstore.upsert(COLLECTION_NAME, records)
    logger.info("Indexed %d chunks for document %d (user_id=%s)", len(records), document_id, user_id)
    return len(records)
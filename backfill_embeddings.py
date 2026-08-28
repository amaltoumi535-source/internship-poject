"""One-time backfill: embeds and indexes all existing documents into the vector store.
Safe to re-run.
"""
from app.modules.storage.repository import StorageRepository
from app.modules.search.indexing import index_document

repo = StorageRepository()
docs = repo.list_documents(limit=1000)
print(f"Found {len(docs)} documents to index.")

for doc in docs:
    try:
        count = index_document(doc.id)
        print(f"  Document {doc.id} ({doc.filename}): indexed {count} chunks")
    except Exception as e:
        print(f"  Document {doc.id} ({doc.filename}): FAILED - {e}")

print("Backfill complete.")

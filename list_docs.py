from app.modules.storage.repository import StorageRepository
repo = StorageRepository()
for doc in repo.list_documents(limit=1000):
    print(doc.id, doc.filename, doc.created_at)

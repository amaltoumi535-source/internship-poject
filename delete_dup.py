from app.modules.storage.repository import StorageRepository
repo = StorageRepository()
deleted = repo.delete_document(4, remove_file=True)
print(f"Document 4 deleted: {deleted}")

# tests/run_repository_smoke.py
"""
Repository smoke test for app.modules.storage.StorageRepository.

Run from project root (the folder that contains the app/ directory):
    python tests/run_repository_smoke.py

What it does:
- Creates a temporary sample file and a file-like object.
- Calls create_document() with both a file path and a file-like UploadFile-like object.
- Lists documents, fetches one, and deletes documents.
- Prints results for manual verification.
"""

import io
import os
import sys
from pathlib import Path
import tempfile
import json

# ensure project root is on sys.path if running from tests/ directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.storage.repository import StorageRepository

def make_sample_file(contents: str, suffix: str = ".txt") -> str:
    tmpdir = Path(tempfile.gettempdir()) / "it_gate_agent_tests"
    tmpdir.mkdir(parents=True, exist_ok=True)
    p = tmpdir / f"sample_{os.getpid()}{suffix}"
    p.write_text(contents, encoding="utf-8")
    return str(p)

class SimpleUploadLike:
    """Minimal UploadFile-like object with .filename and .file for repository tests."""
    def __init__(self, filename: str, bytes_data: bytes):
        self.filename = filename
        self.file = io.BytesIO(bytes_data)
        # give file a name attribute too for file-like handling
        try:
            self.file.name = filename
        except Exception:
            pass

def main():
    repo = StorageRepository()

    print("=== StorageRepository smoke test ===")

    # 1) Create document from path
    sample_path = make_sample_file("This is a sample document stored by path.\nLine 2.\n", suffix=".txt")
    ingestion_result = {
        "filename": "sample_path.txt",
        "parser": "smoke-test",
        "extraction": {"metadata": {"source": "test", "pages": 1}},
        "chunks": [
            {"chunk_id": "c1", "chunk_num": 1, "text": "This is a sample document stored by path.", "metadata": {}}
        ],
    }
    print("Creating document from path:", sample_path)
    doc_id_1 = repo.create_document(sample_path, ingestion_result=ingestion_result)
    print(" -> created document id:", doc_id_1)

    # 2) Create document from file-like (UploadFile-like)
    upload_obj = SimpleUploadLike("sample_stream.txt", b"This is uploaded as a file-like object.\nAnother line.")
    ingestion_result2 = {
        "filename": "sample_stream.txt",
        "parser": "smoke-test",
        "extraction": {"metadata": {"source": "stream", "pages": 1}},
        "chunks": [
            {"chunk_id": "s1", "chunk_num": 1, "text": "This is uploaded as a file-like object.", "metadata": {}}
        ],
    }
    print("Creating document from UploadFile-like object (in-memory)")
    doc_id_2 = repo.create_document(upload_obj, ingestion_result=ingestion_result2)
    print(" -> created document id:", doc_id_2)

    # 3) List documents
    docs = repo.list_documents(limit=10)
    print(f"Listed {len(docs)} documents (showing up to 10):")
    for d in docs:
        print(f"  id={d.id} filename={d.filename} stored_path={d.stored_path} created_at={d.created_at}")

    # 4) Get document and show chunks
    print(f"Fetching document {doc_id_1}")
    doc = repo.get_document(doc_id_1)
    if not doc:
        print("  ERROR: document not found")
    else:
        print(f"  Document id={doc.id} filename={doc.filename} stored_path={doc.stored_path}")
        chunks = getattr(doc, "chunks", []) or []
        print(f"  Chunks: {len(chunks)}")
        for c in chunks:
            print(f"    chunk id={c.chunk_id} num={c.chunk_num} text-preview={ (c.text[:80] + '...') if c.text and len(c.text)>80 else c.text }")

    # 5) Delete created documents
    print(f"Deleting document {doc_id_1}")
    ok1 = repo.delete_document(doc_id_1)
    print(" -> deleted:", ok1)
    print(f"Deleting document {doc_id_2}")
    ok2 = repo.delete_document(doc_id_2)
    print(" -> deleted:", ok2)

    print("=== Smoke test complete ===")

if __name__ == "__main__":
    main()
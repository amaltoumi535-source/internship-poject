# app/modules/storage/repository.py
"""StorageRepository: save files to disk and persist document + chunk rows."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, IO

from sqlalchemy.orm import Session, selectinload

from .database import SessionLocal, engine, Base
from .models import Document, Chunk

from app.config import get_settings
from app.modules.infrastructure.utils import ensure_dir, generate_id
from app.modules.infrastructure.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Ensure DB tables exist
Base.metadata.create_all(bind=engine) # type: ignore[arg-type]

# Default files directory under configured DATA_DIR
DEFAULT_FILES_DIR = os.path.join(os.getcwd(), settings.data_dir or "data", "files")
ensure_dir(DEFAULT_FILES_DIR)


class StorageRepository:
    def __init__(self, files_dir: Optional[str] = None):
        self.files_dir = files_dir or settings.files_dir or DEFAULT_FILES_DIR
        ensure_dir(self.files_dir)

    def _save_file_to_disk(self, upload_file: Union[str, Path, Any, IO]) -> Optional[str]:
        """
        Save a file path, FastAPI UploadFile, file-like object, or Path to disk under files_dir.
        Returns absolute stored path (string) or None if upload_file is None.
        """
        if upload_file is None:
            return None

        # 1) If a path string or Path given -> copy file
        if isinstance(upload_file, (str, Path)):
            src = Path(upload_file)
            if not src.exists():
                raise FileNotFoundError(f"{src} not found")
            # generate unique filename to avoid collisions
            dest_name = f"{generate_id('file')}-{src.name}"
            dest_path = Path(self.files_dir) / dest_name
            shutil.copy2(src, dest_path)
            return str(dest_path.resolve())

        # 2) If FastAPI UploadFile-like object (has .filename and .file)
        filename = getattr(upload_file, "filename", None)
        fileobj = getattr(upload_file, "file", None)

        if filename and fileobj:
            # make unique filename
            dest_name = f"{generate_id('file')}-{Path(filename).name}"
            dest_path = Path(self.files_dir) / dest_name
            # ensure pointer at start
            try:
                fileobj.seek(0)
            except Exception:
                pass
            # write bytes
            with open(dest_path, "wb") as out_f:
                shutil.copyfileobj(fileobj, out_f)
            return str(dest_path.resolve())

        # 3) If a raw file-like object (has read())
        if hasattr(upload_file, "read"):
            # attempt to name it sensibly
            name_hint = getattr(upload_file, "name", None) or f"upload-{generate_id('file')}.bin"
            dest_name = f"{generate_id('file')}-{Path(name_hint).name}"
            dest_path = Path(self.files_dir) / dest_name
            try:
                # ensure pointer at start
                try:
                    upload_file.seek(0)
                except Exception:
                    pass
                with open(dest_path, "wb") as out_f:
                    shutil.copyfileobj(upload_file, out_f)
                return str(dest_path.resolve())
            except Exception as e:
                logger.exception("Failed to save file-like object to disk: %s", e)
                raise

        raise ValueError("Unsupported upload_file type; expected path, Path, UploadFile-like, or file-like object")

    def create_document(self, upload_file: Union[str, Path, Any], ingestion_result: Optional[Dict[str, Any]] = None) -> int:
        """
        Persist a document record and its chunks.
        ingestion_result: optional dict with keys:
          - filename (optional)
          - parser (optional)
          - extraction: { metadata: {...} }
          - chunks: list of {chunk_id, chunk_num, text, metadata}
        Returns the new document id.
        """
        ingestion_result = ingestion_result or {}
        # Save file and collect metadata
        try:
            stored_path = self._save_file_to_disk(upload_file)
            filename = ingestion_result.get("filename") or (Path(stored_path).name if stored_path else "unknown")
        except Exception:
            logger.exception("Failed to save file to storage")
            raise

        parser = ingestion_result.get("parser")
        metadata = ingestion_result.get("extraction", {}).get("metadata", {}) or ingestion_result.get("metadata", {}) or {}

        session: Session = SessionLocal()
        try:
            doc = Document(
                filename=filename,
                stored_path=stored_path,
                parser=parser,
                mime=ingestion_result.get("mime"),
                meta=metadata,
            )
            session.add(doc)
            session.flush()  # assign doc.id

            chunks = ingestion_result.get("chunks") or []
            chunk_objs = []
            for c in chunks:
                chunk_obj = Chunk(
                    document_id=doc.id,
                    chunk_id=c.get("chunk_id"),
                    chunk_num=c.get("chunk_num"),
                    text=c.get("text", "") or "",
                    meta=c.get("metadata", {}) or {},
                )
                chunk_objs.append(chunk_obj)

            if chunk_objs:
                session.add_all(chunk_objs)

            session.commit()
            logger.info("Created document %s with %d chunks", doc.id, len(chunk_objs))
            return int(doc.id) # pyright: ignore[reportArgumentType]
        except Exception:
            session.rollback()
            logger.exception("Database error during create_document")
            raise
        finally:
            session.close()

    def list_documents(self, limit: int = 50, offset: int = 0) -> List[Document]:
        session: Session = SessionLocal()
        try:
            docs = session.query(Document).order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
            return docs
        finally:
            session.close()

    def get_document(self, document_id: int) -> Optional[Document]:
        """
        Return a Document with its chunks eagerly loaded so callers can access chunks
        after the session is closed (avoids DetachedInstanceError).
        """
        session: Session = SessionLocal()
        try:
            doc = (
                session.query(Document)
                .options(selectinload(Document.chunks))
                .filter(Document.id == int(document_id))
                .one_or_none()
            )
            return doc
        finally:
            session.close()

    def delete_document(self, document_id: int, remove_file: bool = True) -> bool:
        session: Session = SessionLocal()
        try:
            doc = session.query(Document).filter(Document.id == document_id).one_or_none()
            if not doc:
                return False
            stored_path = doc.stored_path
            session.delete(doc)
            session.commit()
            # delete file on disk
            if remove_file and stored_path: # pyright: ignore[reportGeneralTypeIssues]
                try:
                    if os.path.exists(stored_path): # pyright: ignore[reportArgumentType]
                        os.remove(stored_path) # pyright: ignore[reportArgumentType]
                except Exception:
                    logger.warning("Failed to remove stored file: %s", stored_path, exc_info=True)
            return True
        except Exception:
            session.rollback()
            logger.exception("Database error during delete_document")
            raise
        finally:
            session.close()
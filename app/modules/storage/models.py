# app/modules/storage/models.py
"""ORM models for documents and chunks used by the storage repository."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy import JSON as SA_JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=True)  # filesystem path
    parser = Column(String, nullable=True)
    mime = Column(String, nullable=True)
    # map DB column "metadata" to attribute 'meta' (avoid reserved name)
    meta = Column("metadata", SA_JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_id = Column(String, nullable=True)
    chunk_num = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    # map DB column "metadata" to attribute 'meta' (avoid reserved name)
    meta = Column("metadata", SA_JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
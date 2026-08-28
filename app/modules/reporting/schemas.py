# app/modules/reporting/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReportOverview(BaseModel):
    total_documents: int
    total_chunks: int
    avg_chunks_per_document: float
    last_ingest_at: Optional[datetime] = None


class DocReport(BaseModel):
    document_id: int
    title: Optional[str] = None
    chunk_count: int
    avg_chunk_length: float
    sample_snippets: List[str] = []


class ExportResult(BaseModel):
    rows: List[dict]
    total: int
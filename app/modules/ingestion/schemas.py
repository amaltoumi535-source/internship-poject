from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class PageModel(BaseModel):
    page_num: int
    text: str
    confidence: Optional[float] = None


class ExtractionMetadata(BaseModel):
    total_pages: Optional[int] = None
    language: Optional[str] = None
    confidence_score: Optional[float] = None
    parser: Optional[str] = None


class ExtractionResult(BaseModel):
    text: str
    metadata: ExtractionMetadata
    pages: List[PageModel] = []


class ChunkModel(BaseModel):
    chunk_id: str
    text: str
    chunk_num: int
    total_chunks: int
    metadata: Dict[str, Any] = {}


class IngestResponse(BaseModel):
    document_id: int
    filename: str
    parser: Optional[str]
    extraction: ExtractionResult
    chunks: List[ChunkModel]
    chunks_count: int

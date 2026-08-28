# app/modules/search/schemas.py
from pydantic import BaseModel
from typing import Optional, List


class ChunkResult(BaseModel):
    id: int
    document_id: int
    chunk_index: Optional[int] = None
    snippet: str
    score: Optional[float] = None


class SearchResponse(BaseModel):
    total: int
    results: List[ChunkResult]
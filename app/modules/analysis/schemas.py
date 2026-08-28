"""Pydantic schemas for analysis endpoints."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    summarize: bool = Field(True, description="Run summarization")
    summary_ratio: float = Field(0.2, description="Ratio for extractive summarization (0-1)")
    detect_language: bool = Field(True, description="Detect language")
    extract_entities: bool = Field(False, description="Run entity extraction (spaCy required)")
    readability: bool = Field(False, description="Compute readability metrics (textstat optional)")


class SummaryResult(BaseModel):
    summary: Optional[str]
    method: str


class LanguageResult(BaseModel):
    language: Optional[str]
    confidence: Optional[float] = None


class EntityItem(BaseModel):
    text: str
    label: str
    start: Optional[int] = None
    end: Optional[int] = None
    extra: Optional[Dict[str, Any]] = None


class ReadabilityResult(BaseModel):
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    gunning_fog: Optional[float] = None
    smog_index: Optional[float] = None


class AnalyzeTextResponse(BaseModel):
    summary: Optional[SummaryResult]
    language: Optional[LanguageResult]
    entities: List[EntityItem] = []
    readability: Optional[ReadabilityResult]


class AnalyzeDocumentRequest(BaseModel):
    summarize_chunks: bool = Field(False, description="Summarize each chunk")
    summarize_document: bool = Field(True, description="Summarize full document by concatenating chunks and summarizing")
    top_k_by_query: Optional[int] = Field(None, description="If query provided, return top-k chunks by similarity")
    query: Optional[str] = Field(None, description="Query to rank chunks by semantic similarity")
    detect_language: bool = Field(True)
    extract_entities: bool = Field(False)


class ChunkAnalysis(BaseModel):
    chunk_id: Optional[str]
    chunk_num: Optional[int]
    text_preview: Optional[str]
    summary: Optional[str]
    score: Optional[float]


class AnalyzeDocumentResponse(BaseModel):
    document_id: int
    document_filename: Optional[str]
    document_summary: Optional[str]
    chunks: List[ChunkAnalysis] = []
    language: Optional[LanguageResult]
    entities: List[EntityItem] = []
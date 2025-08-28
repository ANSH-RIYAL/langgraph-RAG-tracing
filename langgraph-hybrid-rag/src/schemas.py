from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Citation(BaseModel):
    claim: Optional[str] = None
    quote: Optional[str] = None
    source_doc: Optional[str] = None
    chunk_id: str
    page_number: Optional[int] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class Chunk(BaseModel):
    document_id: str
    chunk_id: str
    text: str
    chunk_index: int
    page_number: Optional[int] = None
    score: Optional[float] = None
    fused_score: Optional[float] = None
    retrieval: Optional[str] = None
    source_doc: Optional[str] = None
    source_path: Optional[str] = None
    row_range: Optional[str] = None
    graph_paths: Optional[List[str]] = None


class QueryRequest(BaseModel):
    question: str
    max_chunks: Optional[int] = None


class QueryData(BaseModel):
    answer: str
    citations: List[Citation]
    chunks_retrieved: Dict[str, int]
    chunks_used: List[Chunk]
    reasoning_summary: Optional[str] = None


class Envelope(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None



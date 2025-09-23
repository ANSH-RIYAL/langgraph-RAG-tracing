from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import numpy as np

from ..retrieval.backends.faiss_store import store as faiss_store


router = APIRouter(prefix="/chunk", tags=["chunks"])


class ChunkDetailResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None


@router.get("/{chunk_id}")
async def get_chunk_detail(chunk_id: str) -> ChunkDetailResponse:
    try:
        # Try to find in FAISS metadata
        meta_list = faiss_store.metadata or []
        for ch in meta_list:
            if ch.get("chunk_id") == chunk_id:
                # Build response
                doc_info = {
                    "filename": ch.get("source_doc", "unknown"),
                    "indexed_at": ch.get("indexed_at", "unknown")
                }
                source_lines = ch.get("source_lines") or []
                return ChunkDetailResponse(success=True, data={
                    "chunk": ch,
                    "document": doc_info,
                    "source_lines": source_lines
                })
        return ChunkDetailResponse(success=False, error="Chunk not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





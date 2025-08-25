from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
import os
import json
from ..retrieval.backends.bm25_store import store as bm25_store


router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentsResponse(BaseModel):
    success: bool
    data: Dict | None = None
    error: str | None = None


@router.get("")
async def list_documents() -> DocumentsResponse:
    meta_path = os.path.join("data", "indices", "documents.json")
    meta: Dict[str, Dict] = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    counts: Dict[str, int] = {}
    for doc in getattr(bm25_store, "_docs", []) or []:
        doc_id = doc.get("document_id")
        if not doc_id:
            continue
        counts[doc_id] = counts.get(doc_id, 0) + 1

    documents: List[Dict] = []
    for doc_id, count in counts.items():
        info = meta.get(doc_id, {})
        documents.append({
            "id": doc_id,
            "filename": info.get("filename"),
            "chunks": count,
            "indexed_at": info.get("indexed_at"),
        })

    return DocumentsResponse(success=True, data={"documents": documents})


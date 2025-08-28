from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json


router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentsResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None


@router.get("")
async def list_documents() -> DocumentsResponse:
    try:
        meta_path_legacy = os.path.join("data", "indices", "documents.json")
        meta_path = os.path.join("data", "generated_indices", "documents.json")
        path = meta_path if os.path.exists(meta_path) else meta_path_legacy
        documents = []
        total_chunks = 0
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                documents = data.get("documents", [])
                total_chunks = sum(d.get("chunks", 0) for d in documents)
        return DocumentsResponse(success=True, data={
            "documents": documents,
            "total_documents": len(documents),
            "total_chunks": total_chunks
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



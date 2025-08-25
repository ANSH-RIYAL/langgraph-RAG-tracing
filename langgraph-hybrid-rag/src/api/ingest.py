from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import os
import uuid
from ..config import config
import json
from datetime import datetime
from ..ingestion.loader import load_file_to_text
from ..ingestion.chunker import chunk_text
from ..ingestion.indexer import index_chunks

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None


@router.post("")
async def ingest(file: UploadFile = File(...)) -> IngestResponse:
    try:
        os.makedirs("data/documents", exist_ok=True)
        saved_path = os.path.join("data/documents", file.filename)
        with open(saved_path, "wb") as f:
            f.write(await file.read())

        document_id = f"doc_{uuid.uuid4().hex[:8]}"
        text = load_file_to_text(saved_path)
        chunks = chunk_text(text, doc_id=document_id)
        chunks_indexed = index_chunks(chunks)
        # Record document metadata
        os.makedirs("data/indices", exist_ok=True)
        meta_path = os.path.join("data", "indices", "documents.json")
        meta = {}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}
        meta[document_id] = {
            "filename": file.filename,
            "indexed_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f)
        return IngestResponse(success=True, data={
            "document_id": document_id,
            "chunks_created": chunks_indexed,
            "status": "indexed"
        })
    except Exception as e:
        return IngestResponse(success=False, data=None, error=str(e))

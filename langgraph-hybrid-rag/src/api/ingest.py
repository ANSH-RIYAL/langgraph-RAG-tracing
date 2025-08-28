from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import uuid
from ..config import config
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
        return IngestResponse(success=True, data={
            "document_id": document_id,
            "chunks_created": chunks_indexed,
            "status": "indexed"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import glob
from ..ingestion.csv_parser import load_csv, profile_csv
from ..ingestion.json_parser import load_json
from ..ingestion.corpus_builder import build_from_csv, build_from_companyfacts
from ..ingestion.graph_generator import save_timeseries_plot
from ..ingestion.indexer import index_chunks
from ..ingestion.chunker import chunk_text
from ..telemetry import log_step
from ..ingestion.web_search import web_search_news


router = APIRouter(prefix="/init", tags=["init"])


class InitRequest(BaseModel):
    data_dir: str


class InitResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None


@router.post("")
async def initialize(req: InitRequest) -> InitResponse:
    try:
        data_dir = req.data_dir
        if not os.path.exists(data_dir):
            raise HTTPException(status_code=400, detail="data_dir does not exist")

        total_chunks = 0
        processed_files = []

        # CSV files
        with log_step("init_csv_scan", data_dir=data_dir):
            for path in glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True):
                chunks = build_from_csv(path)
                # chunk the large description text
                final_chunks = []
                for ch in chunks:
                    doc_id = ch["document_id"]
                    for seg in chunk_text(ch["text"], doc_id=doc_id):
                        seg["source_doc"] = ch["source_doc"]
                        seg["source_path"] = ch["source_path"]
                        final_chunks.append(seg)
                total_chunks += index_chunks(final_chunks)
                processed_files.append(path)

        # JSON files (SEC-like)
        with log_step("init_json_scan", data_dir=data_dir):
            for path in glob.glob(os.path.join(data_dir, "**", "*.json"), recursive=True):
                data = load_json(path)
                chunks = build_from_companyfacts(path, data)
                # Optional enrichment: recent news per entity
                try:
                    entity_name = data.get("entityName") or None
                    if entity_name:
                        news = web_search_news(f"latest {entity_name} earnings 2023 site:investor.apple.com OR site:ir.tesla.com OR site:sec.gov", max_results=5)
                        if news:
                            lines = []
                            for n in news:
                                title = n.get("title") or n.get("source") or ""
                                body = n.get("body") or n.get("snippet") or ""
                                url = n.get("link") or n.get("url") or ""
                                lines.append(f"- {title}: {body} ({url})")
                            chunks.append({
                                "document_id": f"doc_{abs(hash('web_'+entity_name)) % (10**8):08d}",
                                "text": f"Web search enrichment for {entity_name}:\n" + "\n".join(lines),
                                "source_doc": f"web_search_{entity_name}.md",
                                "source_path": f"ddg:latest {entity_name} earnings 2023",
                                "chunk_index": 0,
                                "page_number": None,
                            })
                except Exception:
                    pass
                final_chunks = []
                for ch in chunks:
                    doc_id = ch["document_id"]
                    for seg in chunk_text(ch["text"], doc_id=doc_id):
                        seg["source_doc"] = ch["source_doc"]
                        seg["source_path"] = ch["source_path"]
                        final_chunks.append(seg)
                total_chunks += index_chunks(final_chunks)
                processed_files.append(path)

        return InitResponse(success=True, data={
            "processed_files": processed_files,
            "chunks_indexed": total_chunks
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



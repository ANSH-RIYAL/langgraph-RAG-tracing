from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import glob
from ..ingestion.csv_parser import load_csv, profile_csv
from ..ingestion.json_parser import load_json, flatten_companyfacts
from ..ingestion.graph_generator import save_timeseries_plot
from ..ingestion.indexer import index_chunks
from ..ingestion.chunker import chunk_text
from ..telemetry import log_step


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
                df = load_csv(path)
                prof = profile_csv(df)
                # Build a deterministic description text
                head = df.head(3).to_csv(index=False)
                desc = (
                    f"Source: {path}\n"
                    f"Rows: {prof['rows']}, Cols: {prof['cols']}\n"
                    f"Columns: {', '.join(prof['columns'])}\n"
                    f"Sample:\n{head}\n"
                )
                doc_id = f"doc_{abs(hash(path)) % (10**8):08d}"
                chunks = chunk_text(desc, doc_id=doc_id)
                for ch in chunks:
                    ch["source_doc"] = os.path.basename(path)
                    ch["source_path"] = path
                total_chunks += index_chunks(chunks)
                processed_files.append(path)

        # JSON files (SEC-like)
        with log_step("init_json_scan", data_dir=data_dir):
            for path in glob.glob(os.path.join(data_dir, "**", "*.json"), recursive=True):
                data = load_json(path)
                df = flatten_companyfacts(data)
                if df.empty:
                    continue
                head = df.head(5).to_csv(index=False)
                cols = ", ".join([str(c) for c in df.columns])
                desc = (
                    f"Source: {path}\n"
                    f"Columns: {cols}\n"
                    f"Sample:\n{head}\n"
                )
                doc_id = f"doc_{abs(hash(path)) % (10**8):08d}"
                chunks = chunk_text(desc, doc_id=doc_id)
                for ch in chunks:
                    ch["source_doc"] = os.path.basename(path)
                    ch["source_path"] = path
                total_chunks += index_chunks(chunks)
                processed_files.append(path)

        return InitResponse(success=True, data={
            "processed_files": processed_files,
            "chunks_indexed": total_chunks
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



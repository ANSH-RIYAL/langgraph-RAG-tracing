from typing import List, Dict
from ..retrieval.backends.faiss_store import store as faiss_store
from ..retrieval.backends.bm25_store import store as bm25_store
from ..config import config
import os
import json


def index_chunks(chunks: List[Dict]) -> int:
    if not chunks:
        return 0
    # Add to both stores
    faiss_store.add(chunks)
    bm25_store.add(chunks)
    # Update documents metadata
    meta_dir_legacy = os.path.join("data", "indices")
    meta_dir = os.path.join("data", "generated_indices")
    os.makedirs(meta_dir, exist_ok=True)
    path = os.path.join(meta_dir, "documents.json")
    legacy_path = os.path.join(meta_dir_legacy, "documents.json")
    doc_counts = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for d in data.get("documents", []):
                doc_counts[d.get("id")] = d.get("chunks", 0)
    # Count new chunks
    for ch in chunks:
        doc_id = ch.get("document_id")
        if doc_id:
            doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1
    documents = [{"id": k, "filename": ch.get("source_doc", "unknown"), "chunks": v} for k, v in doc_counts.items()]
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"documents": documents}, f, ensure_ascii=False, indent=2)
    return len(chunks)

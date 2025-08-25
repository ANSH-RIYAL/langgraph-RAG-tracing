from typing import List, Dict
from ..retrieval.backends.faiss_store import store as faiss_store
from ..retrieval.backends.bm25_store import store as bm25_store
from ..config import config


def index_chunks(chunks: List[Dict]) -> int:
    if not chunks:
        return 0
    # Add to both stores
    faiss_store.add(chunks)
    bm25_store.add(chunks)
    return len(chunks)

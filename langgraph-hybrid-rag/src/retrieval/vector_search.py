from typing import List, Dict
from .backends.faiss_store import store as faiss_store
from ..config import config


def vector_search(query: str, top_k: int | None = None) -> List[Dict]:
    k = top_k or config.VECTOR_TOP_K
    return faiss_store.search(query, k)

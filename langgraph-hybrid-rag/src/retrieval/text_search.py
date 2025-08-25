from typing import List, Dict
from .backends.bm25_store import store as bm25_store
from ..config import config


def keyword_search(query: str, top_k: int | None = None) -> List[Dict]:
    k = top_k or config.KEYWORD_TOP_K
    return bm25_store.search(query, k)

from typing import List, Dict
import os
import json
from rank_bm25 import BM25Okapi
from ...config import config


class BM25Store:
    def __init__(self, index_dir: str | None = None):
        self.index_dir = index_dir or config.BM25_INDEX_DIR
        os.makedirs(self.index_dir, exist_ok=True)
        self.corpus_path = os.path.join(self.index_dir, "corpus.jsonl")
        self._bm25: BM25Okapi | None = None
        self._docs: List[Dict] = []
        self._tokens: List[List[str]] = []
        if os.path.exists(self.corpus_path):
            self._load()

    def _save(self):
        with open(self.corpus_path, "w", encoding="utf-8") as f:
            for doc in self._docs:
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    def _load(self):
        self._docs = []
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                self._docs.append(json.loads(line))
        self._tokens = [doc["text"].split() for doc in self._docs]
        self._bm25 = BM25Okapi(self._tokens)

    def add(self, chunks: List[Dict]):
        self._docs.extend(chunks)
        self._tokens = [doc["text"].split() for doc in self._docs]
        self._bm25 = BM25Okapi(self._tokens)
        self._save()

    def search(self, query: str, top_k: int) -> List[Dict]:
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(query.split())
        # Pair scores with docs
        scored = sorted(zip(scores, self._docs), key=lambda x: x[0], reverse=True)[:top_k]
        results: List[Dict] = []
        for score, doc in scored:
            results.append({
                **doc,
                "score": float(score),
                "retrieval": "keyword"
            })
        return results


store = BM25Store()

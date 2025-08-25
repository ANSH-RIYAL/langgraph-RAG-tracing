from typing import List, Dict
import os
import numpy as np
import faiss
from ...config import config
from openai import OpenAI


class FaissStore:
    def __init__(self, index_path: str | None = None):
        self.index_path = index_path or config.FAISS_INDEX_PATH
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.index: faiss.IndexFlatIP | None = None
        self.metadata: List[Dict] = []
        if os.path.exists(self.index_path) and os.path.exists(self.index_path + ".meta.npy"):
            self._load()

    def _save(self):
        if self.index is None:
            return
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        np.save(self.index_path + ".meta.npy", np.array(self.metadata, dtype=object), allow_pickle=True)

    def _load(self):
        self.index = faiss.read_index(self.index_path)
        self.metadata = list(np.load(self.index_path + ".meta.npy", allow_pickle=True))

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        # Batch to respect token/size limits
        vectors: List[List[float]] = []
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            resp = self.client.embeddings.create(model=config.EMBEDDING_MODEL, input=batch)
            vectors.extend([d.embedding for d in resp.data])
        return np.array(vectors, dtype="float32")

    def _embed_query(self, query: str) -> np.ndarray:
        resp = self.client.embeddings.create(model=config.EMBEDDING_MODEL, input=[query])
        return np.array([resp.data[0].embedding], dtype="float32")

    def add(self, chunks: List[Dict]):
        texts = [c["text"] for c in chunks]
        vecs = self._embed_texts(texts)
        # Normalize for cosine similarity using inner product
        faiss.normalize_L2(vecs)
        if self.index is None:
            self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(vecs)
        self.metadata.extend(chunks)
        self._save()

    def search(self, query: str, top_k: int) -> List[Dict]:
        if self.index is None or self.index.ntotal == 0:
            return []
        q = self._embed_query(query)
        faiss.normalize_L2(q)
        scores, ids = self.index.search(q, top_k)
        results: List[Dict] = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:
                continue
            meta = self.metadata[idx]
            results.append({
                **meta,
                "score": float(score),
                "retrieval": "vector"
            })
        return results


store = FaissStore()

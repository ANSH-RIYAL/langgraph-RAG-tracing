from typing import List, Dict
from ..config import config


def chunk_text(text: str, doc_id: str) -> List[Dict]:
    words = text.split()
    chunk_size_words = max(50, int(config.CHUNK_SIZE * 0.75))
    overlap_words = int(config.CHUNK_OVERLAP * 0.75)

    chunks: List[Dict] = []
    start = 0
    index = 0
    while start < len(words):
        end = min(len(words), start + chunk_size_words)
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "document_id": doc_id,
            "chunk_id": f"{doc_id}_chunk_{index}",
            "text": chunk_text,
            "chunk_index": index,
            "page_number": None,
        })
        if end == len(words):
            break
        start = end - overlap_words
        index += 1
    return chunks

from typing import List, Dict


def merge_results(vector_chunks: List[Dict], keyword_chunks: List[Dict], top_k: int) -> List[Dict]:
    merged: Dict[str, Dict] = {}

    def add_with_score(chunk: Dict, weight: float):
        key = chunk["chunk_id"]
        if key not in merged:
            merged[key] = {**chunk}
            merged[key]["combined_score"] = 0.0
        merged[key]["combined_score"] += weight * float(chunk.get("score", 0.0))

    for ch in vector_chunks:
        add_with_score(ch, weight=0.5)
    for ch in keyword_chunks:
        add_with_score(ch, weight=0.5)

    sorted_chunks = sorted(merged.values(), key=lambda c: c.get("combined_score", 0.0), reverse=True)
    return sorted_chunks[:top_k]

from typing import TypedDict, List, Dict


class RAGState(TypedDict):
    question: str
    vector_chunks: List[Dict]
    keyword_chunks: List[Dict]
    merged_chunks: List[Dict]
    answer: str
    citations: List[Dict]

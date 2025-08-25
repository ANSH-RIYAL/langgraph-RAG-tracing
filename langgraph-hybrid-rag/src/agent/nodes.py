from typing import Dict, List
from ..retrieval.vector_search import vector_search
from ..retrieval.text_search import keyword_search
from ..retrieval.merger import merge_results
from ..config import config
from ..prompts import ANSWER_PROMPT, CITATION_PROMPT, NO_RESULTS_TEMPLATE
from openai import OpenAI


def retrieve_vector(state: Dict) -> Dict:
    return {"vector_chunks": vector_search(state["question"], top_k=config.VECTOR_TOP_K)}


def retrieve_keyword(state: Dict) -> Dict:
    return {"keyword_chunks": keyword_search(state["question"], top_k=config.KEYWORD_TOP_K)}


def merge(state: Dict) -> Dict:
    return {"merged_chunks": merge_results(state.get("vector_chunks", []), state.get("keyword_chunks", []), top_k=config.MERGED_TOP_K)}


def generate_answer(state: Dict) -> Dict:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    merged = state.get("merged_chunks", [])
    if not merged:
        available_docs = sorted({c.get("document_id") for c in state.get("keyword_chunks", []) + state.get("vector_chunks", []) if c.get("document_id")})
        available_docs_str = "\n".join(available_docs) if available_docs else "(no documents indexed)"
        answer = NO_RESULTS_TEMPLATE.format(question=state["question"], available_docs=available_docs_str)
        return {"answer": answer}

    chunks_formatted = "\n\n".join(
        [f"chunk_id={c['chunk_id']}\n{text}" for c in merged for text in [c.get("text", "")]]
    )
    prompt = ANSWER_PROMPT.format(chunks=chunks_formatted, question=state["question"])
    resp = client.chat.completions.create(model=config.LLM_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0)
    answer = (resp.choices[0].message.content or "").strip()
    return {"answer": answer}


def extract_citations(state: Dict) -> Dict:
    merged = state.get("merged_chunks", [])
    if not merged:
        return {"citations": []}

    # Map to required schema with source_doc and confidence using document metadata
    import os, json as _json
    meta_path = os.path.join("data", "indices", "documents.json")
    doc_meta = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                doc_meta = _json.load(f)
        except Exception:
            doc_meta = {}

    citations = []
    for chunk in merged[: max(1, min(5, len(merged)) )]:
        document_id = chunk.get("document_id")
        filename = (doc_meta.get(document_id) or {}).get("filename") if document_id else None
        citations.append({
            "claim": None,
            "quote": (chunk.get("text") or "")[:200],
            "source_doc": filename or document_id,
            "chunk_id": chunk.get("chunk_id"),
            "page_number": chunk.get("page_number"),
            "confidence": float(chunk.get("combined_score") or chunk.get("score") or 0.5),
        })

    return {"citations": citations}

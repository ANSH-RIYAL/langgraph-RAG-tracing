from typing import Dict
from .nodes import (
    retrieve_vector,
    retrieve_keyword,
    merge as merge_nodes,
    generate_answer,
    extract_citations,
    summarize_reasoning,
)


def run_workflow(question: str, merged_chunks, vector_chunks, keyword_chunks, api_key: str | None = None) -> Dict:
    # Simple deterministic orchestration to avoid graph merge conflicts
    state: Dict = {
        "question": question,
        "vector_chunks": vector_chunks,
        "keyword_chunks": keyword_chunks,
        "merged_chunks": merged_chunks,
        "api_key": api_key or "",
    }
    # Generate answer
    state.update(generate_answer(state))
    # Extract citations
    state.update(extract_citations(state))
    # Reasoning summary
    state.update(summarize_reasoning(state))

    return {
        "answer": state.get("answer", ""),
        "citations": state.get("citations", []),
        "chunks_retrieved": {
            "vector": len(vector_chunks or []),
            "keyword": len(keyword_chunks or []),
            "merged": len(merged_chunks or []),
        },
        "chunks_used": merged_chunks,
        "reasoning_summary": state.get("reasoning_summary"),
    }

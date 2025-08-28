from typing import Dict
from langgraph.graph import StateGraph, START, END
from .state import RAGState
from .nodes import retrieve_vector, retrieve_keyword, merge, generate_answer, extract_citations, summarize_reasoning


def compile_workflow():
    workflow = StateGraph(RAGState)
    workflow.add_node("vector_search", retrieve_vector)
    workflow.add_node("keyword_search", retrieve_keyword)
    workflow.add_node("merge", merge)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("cite", extract_citations)
    workflow.add_node("reason", summarize_reasoning)

    workflow.add_edge(START, "vector_search")
    workflow.add_edge(START, "keyword_search")
    workflow.add_edge("vector_search", "merge")
    workflow.add_edge("keyword_search", "merge")
    workflow.add_edge("merge", "generate")
    workflow.add_edge("generate", "cite")
    workflow.add_edge("cite", "reason")
    workflow.add_edge("reason", END)

    return workflow.compile()


def run_workflow(question: str, merged_chunks, vector_chunks, keyword_chunks) -> Dict:
    app = compile_workflow()
    initial: RAGState = {
        "question": question,
        "vector_chunks": vector_chunks,
        "keyword_chunks": keyword_chunks,
        "merged_chunks": merged_chunks,
        "answer": "",
        "citations": [],
    }
    result = app.invoke(initial)
    return {
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "chunks_retrieved": {
            "vector": len(vector_chunks or []),
            "keyword": len(keyword_chunks or []),
            "merged": len(merged_chunks or []),
        },
        "chunks_used": merged_chunks,
        "reasoning_summary": result.get("reasoning_summary"),
    }

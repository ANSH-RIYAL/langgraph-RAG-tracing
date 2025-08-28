from typing import Dict, List
from ..retrieval.vector_search import vector_search
from ..retrieval.text_search import keyword_search
from ..retrieval.merger import merge_results
from ..config import config
from ..prompts import ANSWER_PROMPT, CITATION_PROMPT, REASONING_SUMMARY_PROMPT
from langchain_openai import ChatOpenAI


def retrieve_vector(state: Dict) -> Dict:
    state["vector_chunks"] = vector_search(state["question"], top_k=config.VECTOR_TOP_K)
    return state


def retrieve_keyword(state: Dict) -> Dict:
    state["keyword_chunks"] = keyword_search(state["question"], top_k=config.KEYWORD_TOP_K)
    return state


def merge(state: Dict) -> Dict:
    state["merged_chunks"] = merge_results(state.get("vector_chunks", []), state.get("keyword_chunks", []), top_k=config.MERGED_TOP_K)
    return state


def generate_answer(state: Dict) -> Dict:
    llm = ChatOpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY, temperature=0)
    chunks_formatted = "\n\n".join([f"chunk_id={c['chunk_id']}\n{c.get('text','')}" for c in state.get("merged_chunks", [])])
    prompt = ANSWER_PROMPT.format(chunks=chunks_formatted, question=state["question"])
    result = llm.invoke(prompt)
    state["answer"] = result.content.strip()
    return state


def extract_citations(state: Dict) -> Dict:
    llm = ChatOpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY, temperature=0)
    chunks_formatted = "\n\n".join([f"chunk_id={c['chunk_id']}\n{c.get('text','')}" for c in state.get("merged_chunks", [])])
    prompt = CITATION_PROMPT.format(answer=state["answer"], chunks=chunks_formatted)
    result = llm.invoke(prompt)
    try:
        import json
        citations = json.loads(result.content)
    except Exception:
        citations = []
    # Attach default confidence if missing
    for c in citations:
        c.setdefault("confidence", 0.5)
    state["citations"] = citations
    return state


def summarize_reasoning(state: Dict) -> Dict:
    llm = ChatOpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY, temperature=0)
    chunks_formatted = ", ".join([c['chunk_id'] for c in state.get("merged_chunks", [])])
    prompt = REASONING_SUMMARY_PROMPT.format(question=state["question"], answer=state.get("answer",""), chunks=chunks_formatted)
    result = llm.invoke(prompt)
    state["reasoning_summary"] = result.content.strip()
    return state

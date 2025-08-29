from typing import Dict, List, Tuple, Optional
from ..retrieval.vector_search import vector_search
from ..retrieval.text_search import keyword_search
from ..retrieval.merger import merge_results
from ..config import config
from ..prompts import ANSWER_PROMPT, CITATION_PROMPT, REASONING_SUMMARY_PROMPT
from langchain_openai import ChatOpenAI
from ..telemetry import log_step
import re


def retrieve_vector(state: Dict) -> Dict:
    return {
        "vector_chunks": vector_search(state["question"], top_k=config.VECTOR_TOP_K)
    }


def retrieve_keyword(state: Dict) -> Dict:
    return {
        "keyword_chunks": keyword_search(state["question"], top_k=config.KEYWORD_TOP_K)
    }


def merge(state: Dict) -> Dict:
    return {
        "merged_chunks": merge_results(state.get("vector_chunks", []), state.get("keyword_chunks", []), top_k=config.MERGED_TOP_K)
    }


def generate_answer(state: Dict) -> Dict:
    api_key = state.get("api_key") or config.OPENAI_API_KEY
    merged = state.get("merged_chunks", [])
    if not api_key:
        # Fallback for local testing only
        top_texts = "\n\n".join([c.get("text", "")[:300] for c in merged[:2]])
        answer = (top_texts[:800] or "No chunks available.").strip()
        return {"answer": answer}
    llm = ChatOpenAI(model=config.LLM_MODEL, api_key=api_key, temperature=0)
    # Limit context size roughly
    joined = []
    total = 0
    for c in merged:
        t = c.get('text','')
        if total + len(t) > 6000:
            break
        joined.append(f"chunk_id={c['chunk_id']}\n{t}")
        total += len(t)
    chunks_formatted = "\n\n".join(joined)

    # Optional: pre-compute direct comparison facts from chunks for 2-entity queries
    facts_block = _compute_basic_comparison_block(state.get("question", ""), merged)
    with log_step("answer_prep", has_facts=bool(facts_block)):
        if facts_block:
            chunks_for_prompt = f"{chunks_formatted}\n\nAdditional computed facts (grounded in retrieved chunks):\n{facts_block}"
        else:
            chunks_for_prompt = chunks_formatted

    prompt = ANSWER_PROMPT.format(chunks=chunks_for_prompt, question=state["question"])
    result = llm.invoke(prompt)
    return {"answer": result.content.strip()}


def extract_citations(state: Dict) -> Dict:
    api_key = state.get("api_key") or config.OPENAI_API_KEY
    merged = state.get("merged_chunks", [])
    if not api_key:
        citations = []
        for c in merged[:3]:
            citations.append({
                "claim": None,
                "quote": c.get("text", "")[:180],
                "source_doc": c.get("source_doc"),
                "chunk_id": c.get("chunk_id"),
                "page_number": c.get("page_number"),
                "confidence": float(c.get("fused_score", 0.5))
            })
        return {"citations": citations}
    llm = ChatOpenAI(model=config.LLM_MODEL, api_key=api_key, temperature=0)
    joined = []
    total = 0
    for c in merged:
        t = c.get('text','')
        if total + len(t) > 6000:
            break
        joined.append(f"chunk_id={c['chunk_id']}\n{t}")
        total += len(t)
    chunks_formatted = "\n\n".join(joined)
    # Avoid Python .format interpreting JSON braces; perform safe replacements
    prompt = (
        CITATION_PROMPT
        .replace("{answer}", state.get("answer", ""))
        .replace("{chunks}", chunks_formatted)
    )
    result = llm.invoke(prompt)
    try:
        import json
        citations = json.loads(result.content)
    except Exception:
        citations = []
    for c in citations:
        c.setdefault("confidence", 0.5)
    return {"citations": citations}


def summarize_reasoning(state: Dict) -> Dict:
    api_key = state.get("api_key") or config.OPENAI_API_KEY
    merged = state.get("merged_chunks", [])
    if not api_key:
        return {"reasoning_summary": f"Answer derived from {', '.join([c['chunk_id'] for c in merged[:3]])}."}
    llm = ChatOpenAI(model=config.LLM_MODEL, api_key=api_key, temperature=0)
    chunks_formatted = ", ".join([c['chunk_id'] for c in merged])
    prompt = REASONING_SUMMARY_PROMPT.format(question=state["question"], answer=state.get("answer",""), chunks=chunks_formatted)
    result = llm.invoke(prompt)
    return {"reasoning_summary": result.content.strip()}


# --- Helpers ---

def _compute_basic_comparison_block(question: str, chunks: List[Dict]) -> Optional[str]:
    """Extract simple EPS/NetIncome/Revenue numbers for two entities from retrieved chunks.
    Returns a small facts text block grounded in chunk_ids for the answer prompt.
    """
    entities = _detect_entities_from_chunks(question, chunks)
    if len(entities) < 2:
        return None
    target_entities = set(entities[:2])
    # Collect per-entity facts: metric -> (value, chunk_id)
    facts: Dict[str, Dict[str, Tuple[str, str]]] = {}
    metric_patterns = {
        "EPS": re.compile(r"(?:EPS|Earnings\s*Per\s*Share|EarningsPerShare)(?:\s*(?:Diluted|Basic))?\s*[:=]?\s*\$?(-?\d+(?:\.\d+)?)", re.I),
        "NetIncome": re.compile(r"(?:Net\s*Income|NetIncomeLoss)\s*[:=]?\s*\$?(-?\d+(?:[,\d]+)?(?:\.\d+)?)", re.I),
        "Revenue": re.compile(r"(Revenue|Revenues|Sales\s*Revenue\s*Net)\s*[:=]?\s*\$?(-?\d+(?:[,\d]+)?(?:\.\d+)?)", re.I),
    }
    for c in chunks:
        text = c.get("text", "")
        chunk_id = c.get("chunk_id", "")
        for ent in list(target_entities):
            if ent.lower() in text.lower():
                ent_facts = facts.setdefault(ent, {})
                # Extract metrics
                m = metric_patterns["EPS"].search(text)
                if m and "EPS" not in ent_facts:
                    ent_facts["EPS"] = (m.group(1), chunk_id)
                m = metric_patterns["NetIncome"].search(text)
                if m and "NetIncome" not in ent_facts:
                    ent_facts["NetIncome"] = (m.group(1), chunk_id)
                m = metric_patterns["Revenue"].search(text)
                if m and "Revenue" not in ent_facts:
                    # second capture group is the number
                    ent_facts["Revenue"] = (m.group(2), chunk_id)
    if len(facts) < 2:
        return None
    # Build a compact block
    lines: List[str] = []
    for ent, met in facts.items():
        parts = []
        for k in ("EPS", "NetIncome", "Revenue"):
            if k in met:
                val, cid = met[k]
                parts.append(f"{k}={val} (from {cid})")
        if parts:
            lines.append(f"{ent}: " + ", ".join(parts))
    return "\n".join(lines) if lines else None


def _detect_entities_from_chunks(question: str, chunks: List[Dict]) -> List[str]:
    q_tokens = set(t.lower() for t in re.findall(r"[A-Za-z][A-Za-z\.&'-]+", question))
    # Extract entity names from chunk headers like "Entity: Apple Inc. Columns: ..."
    found = []
    for c in chunks:
        text = c.get("text", "")
        m = re.search(r"Entity:\s*([^\n]+?)\s+Columns:\s*", text)
        if m:
            ent = m.group(1).strip()
            # match if any token from question appears in the entity
            if any(tok in ent.lower() for tok in q_tokens):
                found.append(ent)
    # Deduplicate preserving order
    dedup: List[str] = []
    for f in found:
        if f not in dedup:
            dedup.append(f)
    if len(dedup) >= 2:
        return dedup[:2]
    # Fallback to capitalized tokens
    tokens = [t for t in re.findall(r"[A-Z][a-zA-Z]+", question) if t.lower() not in {"compare", "vs"}]
    preferred = [t for t in tokens if t.lower() in {"apple", "amazon", "google", "microsoft", "meta", "tesla", "nvidia", "pfizer"}]
    if len(preferred) >= 2:
        return preferred[:2]
    return tokens[:2]

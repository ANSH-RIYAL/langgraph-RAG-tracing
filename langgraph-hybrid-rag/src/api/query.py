from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
from ..config import config
from ..retrieval.vector_search import vector_search
from ..retrieval.text_search import keyword_search
from ..retrieval.merger import merge_results
from ..agent.workflow import run_workflow
from ..schemas import Citation as CitationModel, Chunk as ChunkModel, QueryData as QueryDataModel
import traceback
import re

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    max_chunks: int | None = None


class QueryResponse(BaseModel):
    success: bool
    data: Dict | None = None
    error: str | None = None


@router.post("")
async def query(req: QueryRequest, request: Request) -> QueryResponse:
    try:
        header_api_key = request.headers.get("x-openai-api-key")
        # Augment query with entity aliases to improve retrieval recall
        effective_question = _augment_query_with_aliases(req.question)
        # Retrieval (hybrid)
        top_k = req.max_chunks or 20
        vector_chunks = vector_search(effective_question, top_k=config.VECTOR_TOP_K)
        keyword_chunks = keyword_search(effective_question, top_k=config.KEYWORD_TOP_K)
        merged_chunks = merge_results(vector_chunks, keyword_chunks, top_k=top_k)

        # Full LLM path enabled
        result = run_workflow(
            question=req.question,
            merged_chunks=merged_chunks,
            vector_chunks=vector_chunks,
            keyword_chunks=keyword_chunks,
            api_key=header_api_key or config.OPENAI_API_KEY,
        )

        # Normalize citations to Pydantic model
        norm_citations = []
        for c in result.get("citations", []) or []:
            chunk_id = c.get("chunk_id") or c.get("source_chunk_id")
            try:
                norm_citations.append(CitationModel(
                    claim=c.get("claim"),
                    quote=c.get("quote"),
                    source_doc=c.get("source_doc"),
                    chunk_id=chunk_id,
                    page_number=c.get("page_number"),
                    confidence=float(c.get("confidence", 0.5)),
                ).model_dump())
            except Exception:
                # skip malformed
                continue

        # Normalize chunks used
        norm_chunks = []
        for ch in result.get("chunks_used", []) or []:
            try:
                norm_chunks.append(ChunkModel(
                    document_id=ch.get("document_id") or "",
                    chunk_id=ch.get("chunk_id") or "",
                    text=ch.get("text") or "",
                    chunk_index=int(ch.get("chunk_index") or 0),
                    page_number=ch.get("page_number"),
                    score=ch.get("score"),
                    fused_score=ch.get("fused_score"),
                    retrieval=ch.get("retrieval"),
                    source_doc=ch.get("source_doc"),
                    source_path=ch.get("source_path"),
                    row_range=ch.get("row_range"),
                    graph_paths=ch.get("graph_paths"),
                ).model_dump())
            except Exception:
                continue

        data_model = QueryDataModel(
            answer=result.get("answer", ""),
            citations=[CitationModel(**c) for c in norm_citations],
            chunks_retrieved=result.get("chunks_retrieved", {}),
            chunks_used=[ChunkModel(**c) for c in norm_chunks],
            reasoning_summary=result.get("reasoning_summary"),
        )

        return QueryResponse(success=True, data=data_model.model_dump())
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _augment_query_with_aliases(question: str) -> str:
    aliases = {
        "amazon": ["Amazon.com, Inc.", "AMAZON COM INC", "AMZN"],
        "apple": ["Apple Inc.", "AAPL"],
        "google": ["Alphabet Inc.", "GOOGL", "GOOG"],
        "alphabet": ["Alphabet Inc.", "GOOGL", "GOOG"],
        "facebook": ["Meta Platforms, Inc.", "META"],
        "meta": ["Meta Platforms, Inc.", "META"],
        "microsoft": ["Microsoft Corporation", "MSFT"],
        "tesla": ["Tesla, Inc.", "TSLA"],
        "pfizer": ["PFIZER INC", "PFE"],
        "nvidia": ["NVIDIA CORP", "NVDA"],
        "visa": ["Visa Inc.", "V"],
        "mastercard": ["Mastercard Incorporated", "MA"],
        "broadcom": ["Broadcom Inc.", "AVGO"],
        "exxon": ["Exxon Mobil Corporation", "XOM"],
        "jpmorgan": ["JPMorgan Chase & Co.", "JPM"],
        "berkshire": ["Berkshire Hathaway Inc.", "BRK.B", "BRK-B"],
    }
    tokens = set(t.lower() for t in re.findall(r"[A-Za-z][A-Za-z\.&'-]+", question))
    extra: list[str] = []
    for k, vals in aliases.items():
        if k in tokens:
            if isinstance(vals, list):
                extra.extend(vals)
            else:
                extra.append(vals)
    # Add metric hints when comparison is requested
    if any(w in tokens for w in {"compare", "vs", "versus"}):
        extra.extend(["EarningsPerShareDiluted", "NetIncomeLoss", "Revenues", "2023"])
    if not extra:
        return question
    return question + " " + " ".join(extra)

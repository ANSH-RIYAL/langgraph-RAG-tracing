from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from ..config import config
from ..retrieval.vector_search import vector_search
from ..retrieval.text_search import keyword_search
from ..retrieval.merger import merge_results
from ..agent.workflow import run_workflow

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    max_chunks: int | None = None


class QueryResponse(BaseModel):
    success: bool
    data: Dict | None = None
    error: str | None = None


@router.post("")
async def query(req: QueryRequest) -> QueryResponse:
    try:
        top_k = req.max_chunks or config.MERGED_TOP_K
        vector_chunks = vector_search(req.question, top_k=config.VECTOR_TOP_K)
        keyword_chunks = keyword_search(req.question, top_k=config.KEYWORD_TOP_K)
        merged_chunks = merge_results(vector_chunks, keyword_chunks, top_k=top_k)

        result = run_workflow(question=req.question, merged_chunks=merged_chunks,
                              vector_chunks=vector_chunks, keyword_chunks=keyword_chunks)
        return QueryResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

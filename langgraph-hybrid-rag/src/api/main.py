from fastapi import FastAPI
from .ingest import router as ingest_router
from .query import router as query_router
from .documents import router as documents_router
from .chunks import router as chunks_router
from .init import router as init_router

app = FastAPI(title="LangGraph Hybrid RAG (Local-First)")


@app.get("/health")
async def health():
    return {"success": True}


app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(documents_router)
app.include_router(chunks_router)
app.include_router(init_router)

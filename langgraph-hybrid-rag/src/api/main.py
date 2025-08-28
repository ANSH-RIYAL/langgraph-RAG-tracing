from fastapi import FastAPI
from .ingest import router as ingest_router
from .query import router as query_router

app = FastAPI(title="LangGraph Hybrid RAG (Local-First)")


@app.get("/health")
async def health():
    return {"success": True}


app.include_router(ingest_router)
app.include_router(query_router)

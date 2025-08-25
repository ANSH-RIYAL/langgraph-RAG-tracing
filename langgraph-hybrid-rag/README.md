# LangGraph Hybrid RAG (Local-First)

Hybrid retrieval (FAISS + BM25) with mandatory citations. Pluggable adapters for Qdrant/Elasticsearch post-MVP.

## Run
1. Create `.env` (or edit existing):
```
OPENAI_API_KEY=...
```
2. Install deps:
```
pip install -r requirements.txt
```
3. Start API:
```
uvicorn src.api.main:app --reload --app-dir .
```

## Endpoints
- POST /ingest (multipart file)
- POST /query { question, max_chunks? }
- GET /health

## Indices
- Vector: FAISS at `data/indices/vector.faiss`
- Keyword: BM25 at `data/indices/bm25/`

## Notes
- Large public PDFs via `scripts/download_test_docs.sh`
- See `rag-structure.md` for architecture
- See `CHANGELOG.md` for decisions and progress

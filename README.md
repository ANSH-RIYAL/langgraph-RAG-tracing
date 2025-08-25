# LangGraph Hybrid RAG with Citations (Tracing-First)

RAG tracing ensures every answer is backed by specific source chunks, solving the "where did this come from?" problem. This repo implements a hybrid retriever (FAISS vectors + BM25 keywords) plus mandatory citations. The goal is a debuggable, production-friendly RAG baseline with clear provenance.

## Quick Examples (curl)

- Health:
```bash
curl -s http://localhost:8050/health
```
Response:
```json
{"success": true}
```

- Ingest (faq.txt):
```bash
curl -s -X POST -F "file=@langgraph-hybrid-rag/test_documents/faq.txt" http://localhost:8050/ingest
```
Response (real):
```json
{"success":true,"data":{"document_id":"doc_aac2bc3f","chunks_created":1,"status":"indexed"},"error":null}
```

- Query:
```bash
curl -s -X POST http://localhost:8050/query -H "Content-Type: application/json" -d "{\"question\":\"What is a staging environment?\"}"
```
Response (real):
```json
{"success":true,"data":{"answer":"A staging environment mirrors production for final testing before release (doc_03af2805_chunk_0).","citations":[{"claim":null,"quote":"Q: What is a staging environment? A: A staging environment mirrors production for final testing before release. Q: What is a rollback? A: Reverting a deployment to a previous stable version. Q: What i","source_doc":"faq.txt","chunk_id":"doc_03af2805_chunk_0","page_number":null,"confidence":-1.6499156246081077},{"claim":null,"quote":"Q: What is a staging environment? A: A staging environment mirrors production for final testing before release. Q: What is a rollback? A: Reverting a deployment to a previous stable version. Q: What i","source_doc":"faq.txt","chunk_id":"doc_aac2bc3f_chunk_0","page_number":null,"confidence":-1.6499491820231162},{"claim":null,"quote":"Q: What is a staging environment? A: A staging environment mirrors production for final testing before release. Q: What is a rollback? A: Reverting a deployment to a previous stable version. Q: What i","source_doc":"faq.txt","chunk_id":"doc_80ca949f_chunk_0","page_number":null,"confidence":-1.6499491820231162}],"chunks_retrieved":{"vector":3,"keyword":3,"merged":3}},"error":null}
```

## Setup

1) .env
Copy `langgraph-hybrid-rag/.env.example` to `.env` (already created in this repo) and set:
```bash
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_BACKEND=faiss
KEYWORD_BACKEND=bm25
FAISS_INDEX_PATH=data/indices/vector.faiss
BM25_INDEX_DIR=data/indices/bm25
API_HOST=0.0.0.0
API_PORT=8050
```

2) Install & run API
```bash
cd langgraph-hybrid-rag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/download_test_docs.sh
uvicorn src.api.main:app --host 0.0.0.0 --port 8050
```

3) Ingest & query
- Ingest: `curl -s -X POST -F "file=@langgraph-hybrid-rag/test_documents/faq.txt" http://localhost:8050/ingest`
- Query: `curl -s -X POST http://localhost:8050/query -H "Content-Type: application/json" -d {question:What is a staging environment?}`

## Routes

- GET `/health`: service health
- POST `/ingest`: multipart file upload; indexes chunks into FAISS + BM25; returns `{document_id, chunks_created}`
- POST `/query`: body `{question, max_chunks?}`; returns `{answer, citations[], chunks_retrieved}`
- GET `/documents`: lists indexed documents with chunk counts and timestamps

See `rag-structure.md` for the complete project layout and invariants.

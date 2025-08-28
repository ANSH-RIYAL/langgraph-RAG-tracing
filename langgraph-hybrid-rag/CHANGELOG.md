# CHANGELOG

## 2025-01-XX
- Initialize project: Local-first Hybrid RAG (FAISS + BM25) with pluggable Qdrant/Elasticsearch adapters planned for later.
- Invariants: citations required; hybrid retrieval mandatory; 400/50 chunking; 3000 token context; response = { success, data, error }.
- Models: embeddings=text-embedding-3-small, llm=gpt-4o-mini (overridable via .env).
- Updated knowledge docs: foundation, plan (no Docker in MVP), prompts (strict JSON citations + confidence), reality checks (large public PDFs + FAQ + download script), runbooks (local indices), structure (adapters, scripts, .env).
- Scaffolded codebase per structure; created .env and .env.example.
- Implemented ingestion (loader/chunker/indexer), retrieval (FAISS/BM25), LangGraph workflow, API (/health, /ingest, /query).
- Next: download test docs script, test pipeline, README, refine prompts/citation parsing, add error handling.

## 2025-08-25
- Switched to local-first embeddings/LLM via OpenAI SDK; removed LangChain to avoid proxies issue.
- Implemented deterministic citation fallback (uses top merged chunks) to guarantee citations even if LLM JSON fails.
- Added /documents endpoint and document metadata tracking.
- Verified end-to-end on port 8050; sample ingest and query outputs captured in README.

## 2025-08-28
- Enforced always-on hybrid retrieval (vector + keyword) for validation; no degraded modes.
- Introduced Pydantic-first schemas for chunks, citations, queries; standardized response envelope.
- Standardized generated artifacts under `data/generated_indices/` and added `real_data/` for curated corpora.
- Added structured, step-scoped logging requirements (noise-free terminal output).
- Updated prompts to include safe reasoning summary (no raw chain-of-thought).
- Planned frontend proxy integration for `/api/*` to backend endpoints.
 - Added root `.gitignore` to exclude virtualenv, caches, and generated artifacts.

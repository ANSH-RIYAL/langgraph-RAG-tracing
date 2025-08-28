# FOUNDATION - LangGraph Hybrid RAG with Citations

## What This Is
A straightforward RAG system that actually works in production. It retrieves documents using both vector and keyword search, then tracks exactly which document each answer comes from. No magic, no complex abstractions.

## Core Problem It Solves
"Our chatbot gave wrong information and we can't figure out why" - Every team with a RAG system

This template ensures:
- You can trace every answer back to its source document
- Both semantic and keyword queries work well
- You know exactly which chunk the LLM used for each claim

## Build Philosophy
- **Hybrid by Default (Always-On)**: Vector and keyword retrieval both run on every query. No degraded-mode validation.
- **Citation Required**: Every factual claim must reference a specific document chunk.
- **Local-First, Pluggable**: Default to local FAISS + BM25 for zero external deps; allow swap-in of Qdrant/Elasticsearch later.
- **Traceable by Design**: Every step emits precise, structured logs (no noisy prints) for input/output and timings.
- **Schema-Centric**: Pydantic models define and validate all data flows (chunks, citations, answers, traces).

## Technical Stack (Local-first, pluggable)
- **LangGraph**: Orchestrates RAG workflow and state.
- **FAISS**: Local vector index for semantic search (default).
- **Rank-BM25**: Local keyword search (default) with in-memory corpus preload.
- **FastAPI**: REST API with strict Pydantic schemas; structured logging.
- **OpenAI**: Embeddings (text-embedding-3-small) and generation (gpt-4o-mini).
- **Optional Production Backends**: Qdrant (vectors) and Elasticsearch (BM25) can be enabled later.
- **Telemetry**: Structured, step-scoped logs (inputs elided where sensitive; shapes and counts always logged).

## Invariants (Do Not Change)
- Every response includes `citations[]` with `source_doc`, `chunk_id`, `confidence`.
- Hybrid search always runs both vector and keyword, then merges (no single-retriever validation).
- Retrieval backends are pluggable; defaults are FAISS (vector) and BM25 (keyword).
- Chunks are 400 tokens with 50 token overlap.
- Maximum context window is 3000 tokens.
- Response format is always `{ success, data, error }`.
- Pydantic models are the single source of truth for API contracts and internal state.
- Logs are precise and comprehensive for intermediates (inputs/outputs, sizes, ids, timings) with no extraneous noise.
- Generated artifacts use fixed names and locations: indices under `data/generated_indices/`, documents under `data/documents/` and curated corpora under `real_data/`.
- Traceability is JSON-exportable; context is provided as raw strings for copy/paste.

## Decision Log
`2025-01 | Hybrid search mandatory | Single search type fails too often | Immutable`
`2025-01 | 400 token chunks | Balance between context and precision | Tentative`
`2025-01 | LangGraph for workflow | Clearer than chain abstractions | Immutable`
`2025-01 | Citations in response | Legal/compliance requirement | Immutable`
`2025-01 | Local FAISS/BM25 for MVP | Zero external dependencies | Immutable for MVP`
`2025-01 | Pluggable retrieval adapters | Swap to Qdrant/Elasticsearch later | Immutable`
`2025-08 | Pydantic-first contracts | Reliability via typed, validated IO | Immutable`
`2025-08 | Structured logs only | Step-scoped, noise-free debugging | Immutable`
`2025-08 | Fixed artifact names | Stable paths for indices and docs | Immutable`

## What We're NOT Building
- No observability platform (just structured logs).
- No fine-tuning.
- No multi-tenancy.
- No streaming responses.
- No authentication (add your own).
- No fancy reranking (just score fusion).
- No raw chain-of-thought exposure (internal summaries only).

## Success Metrics
A query should:
1. Return relevant chunks from both search methods on every query.
2. Generate an answer using only those chunks.
3. Cite the specific source for each claim (non-empty citations).
4. Complete in under 3 seconds.
5. Emit step-by-step, structured logs (inputs/outputs, counts, ids, timings) with no garbage prints.
6. Provide JSON-exportable traceability and plain-string context for copy/paste.
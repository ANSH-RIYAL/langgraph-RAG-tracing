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
- **Hybrid by Default**: Vector search fails on acronyms and exact matches. BM25 fails on semantic queries. Use both.
- **Citation Required**: Every factual claim must reference a specific document chunk
- **Local-First, Pluggable**: Default to local FAISS + BM25 for zero external deps; allow swap-in of Qdrant/Elasticsearch later.
- **Debug First**: You can see exactly what's happening at each step

## Technical Stack (Local-first, pluggable)
- **LangGraph**: Controls the RAG workflow with clear state management
- **FAISS**: Local vector index for semantic search (default)
- **Rank-BM25**: Local keyword search (default)
- **FastAPI**: Simple REST API
- **OpenAI**: Embeddings (text-embedding-3-small) and generation (gpt-4o-mini)
- **Optional Production Backends**: Qdrant (vectors) and Elasticsearch (BM25) can be enabled later

## Invariants (Do Not Change)
- Every response includes `citations[]` with `source_doc`, `chunk_id`, `confidence`
- Hybrid search always runs both vector and keyword, then merges
- Retrieval backends are pluggable; defaults are FAISS (vector) and BM25 (keyword)
- Chunks are 400 tokens with 50 token overlap
- Maximum context window is 3000 tokens
- Response format is always `{ success, data, error }`

## Decision Log
`2025-01 | Hybrid search mandatory | Single search type fails too often | Immutable`
`2025-01 | 400 token chunks | Balance between context and precision | Tentative`
`2025-01 | LangGraph for workflow | Clearer than chain abstractions | Immutable`
`2025-01 | Citations in response | Legal/compliance requirement | Immutable`
`2025-01 | Local FAISS/BM25 for MVP | Zero external dependencies | Immutable for MVP`
`2025-01 | Pluggable retrieval adapters | Swap to Qdrant/Elasticsearch later | Immutable`

## What We're NOT Building
- No observability platform (just logs)
- No fine-tuning
- No multi-tenancy
- No streaming
- No authentication (add your own)
- No fancy reranking (just score fusion)

## Success Metrics
A query should:
1. Return relevant chunks from both search methods
2. Generate an answer using only those chunks
3. Cite the specific source for each claim
4. Complete in under 3 seconds
5. Show exactly what happened in logs
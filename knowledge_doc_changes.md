I'll outline the actionable plan, but first I'll create a concise task list to track the work items we’ll drive next.

[1 tool called]

I'll quickly scan the backend API files and retrieval code to align routes, schemas, and capabilities before proposing concrete doc changes and the frontend wiring.

[5 tools called]

I reviewed the backend API (`/src/api/main.py`, `/src/api/ingest.py`, `/src/api/query.py`), agent nodes, and FAISS store to align with your goals. I’ll propose concrete doc updates, backend/FE wiring, and API changes to get you to a production-grade, streamlined hybrid RAG with traceability.

### How I’ll modify the knowledge docs

- rag-foundation.md
  - Clarify invariants and scope for production:
    - Hybrid retrieval: FAISS vectors + BM25 keywords, always both.
    - Citations required with deterministic fallback if LLM JSON extraction fails.
    - Reasoning: Store a concise “reasoning_summary”; never return raw chain-of-thought.
    - Traceability: Every claim links to `document_id`, `chunk_id`, `page_number?`, `quote`, `confidence`.
    - Performance SLOs: ingest <2s/page, P50 query <2s, P95 <3s on local indices.
    - Observability: step timings; retrieval counts; fused scores per chunk in logs.
    - Scalability: streaming ingestion; batch embeddings; memory-mapped FAISS; BM25 corpus preloading.
  - Update “Technical Stack”: note OpenAI SDK (no LangChain), CORS, and pluggable adapters kept simple.
  - Expand “What We’re NOT Building”: still no streaming responses; add “no raw CoT logging”.

- rag-plan.md
  - Reframe into near-term deliverables:
    - Week 1: Hybrid retrieval correctness, deterministic citations, FE proxy wiring, `/documents` and `/chunk/{id}`, CORS, preloading indices, simple reasoning_summary.
    - Week 2: Latency optimizations (batching, caching, async I/O), scalable ingestion, bigger test corpora and validation scripts, confidence calibration, doc updates.
  - Add acceptance criteria: schema stability, end-to-end tests, P95 latency targets.
  - Replace prompt tasks to use OpenAI SDK and JSON parsing with strict schema/fallback.

- rag-structure.md
  - Bring directory layout in sync with code:
    - `src/api/` includes `main.py`, `ingest.py`, `query.py`, `documents.py` (re-add) and `chunks.py`.
    - `src/retrieval/backends/` includes `faiss_store.py`, `bm25_store.py` (ensure it’s wired) and optional adapters.
    - `src/agent/` includes `workflow.py`, `nodes.py`, `state.py`.
    - Add `src/schemas.py` for Pydantic response models and `src/telemetry.py` for tracing/timings.
  - Update API endpoints:
    - GET `/health`, GET `/documents`, GET `/chunk/{chunk_id}`
    - POST `/ingest` (multipart), POST `/query` (JSON)
  - Add config keys: ports, CORS origins, batch sizes, RRF weights, confidence thresholds.
  - Include the “Reasoning Summary” field in response model (text, short).

- rag-prompts.md
  - Answer prompt: instruct “think step by step internally; do not reveal steps; cite chunk_ids inline when natural.”
  - Citation prompt: keep strict JSON schema; add guard rails (max 512 tokens; limit to provided chunk_ids; no new facts).
  - Relevance scoring: keep numeric-only output; cap runtime.
  - Add a “Reasoning Summary” prompt producing a 1–2 sentence summary (no chain-of-thought).
  - Note fallback policy: if JSON invalid → deterministic top-k merged chunks with derived confidence.

- rag-reality-checks.md
  - Replace datasets and scripts with runnable, larger tests:
    - Update `scripts/download_test_docs.sh` to fetch 5–10 public PDFs and larger FAQs.
    - Add volume and concurrency tests (e.g., 50 queries with concurrency 5).
  - Explicit validation:
    - Must return both vector and keyword chunks for >80% queries.
    - Citations array always present; fallback verified when LLM fails.
    - Confidence distribution sane (0.6–0.95 typical).
    - Latency budgets met.
  - Update `test_pipeline.py` to assert new response schema (citations, chunks_used, chunks_retrieved, reasoning_summary).

- rag-runbooks.md
  - Add sections:
    - “Frontend/Backend connectivity”: 5000→8050 proxy or CORS config; common pitfalls.
    - “Index warmup and reload”: preloading FAISS and BM25 on startup.
    - “Deterministic citation fallback debug”: how to verify and tune.
    - “Confidence calibration”: mapping fused retrieval scores to [0,1].
    - “High-volume ingestion”: batching, background ingestion, memory headroom.
  - Update troubleshooting to match new endpoints and logs.

- README.md (root)
  - Clear run instructions:
    - Start backend on 8050, start frontend on 5000.
    - Option A: frontend proxies to backend; Option B: FE JS uses `BACKEND_URL` env.
  - Curl examples for `/ingest`, `/query`, `/documents`, `/chunk/{id}` and expected JSON.
  - Add env table (LLM model, embedding model, CORS origins, batch sizes).
  - Performance tips.

- langgraph-hybrid-rag/CHANGELOG.md
  - New entry: re-introduced `/documents` and `/chunk/{id}`, OpenAI SDK for LLM/embeddings, deterministic citation fallback, confidence calibration, proxy integration, CORS, preloading indices, updated prompts.

- langgraph-hybrid-rag/README.md
  - Align with above: endpoints list, port 8050, how to preload indices, minimal example, testing steps, note reasoning_summary.

### How I’ll connect the frontend with the backend

- Recommended (no CORS changes in JS): Keep existing FE routes and proxy them in Flask to the FastAPI backend at `http://localhost:8050`.
  - In `frontend/app.py`, set `BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8050")`.
  - For each FE route:
    - `/api/health` → forward to `GET {BACKEND_URL}/health`
    - `/api/documents` → forward to `GET {BACKEND_URL}/documents`
    - `/api/query` → forward to `POST {BACKEND_URL}/query`
    - `/api/chunk/<chunk_id>` → forward to `GET {BACKEND_URL}/chunk/{chunk_id}`
    - `/api/upload` → forward to `POST {BACKEND_URL}/ingest` (multipart form)
  - Keep `frontend/static/js/app.js` URLs unchanged (they hit the Flask proxy), so no browser CORS issues.

- Alternative (if preferred): enable CORS in FastAPI (`CORSMiddleware`) and change FE JS fetch URLs to hit `http://localhost:8050/...`. I’ll keep it simple with the Flask proxy.

### Backend API changes to meet your goals

- Routes and schemas
  - Add `src/api/documents.py`:
    - GET `/documents` → `{ success, data: { documents[], total_documents, total_chunks }, error }`
    - Build documents list from stored metadata (persist on ingest) or fold FAISS/BM25 metadata to aggregate by `document_id`.
  - Add `src/api/chunks.py`:
    - GET `/chunk/{chunk_id}` → `{ success, data: { chunk, document, source_lines? }, error }`
    - `source_lines` optional; return chunk text and surrounding lines when available.
  - Ensure uniform response envelope `{ success, data, error }` across all endpoints.

- Hybrid retrieval and fusion
  - Ensure `src/retrieval/text_search.py` uses rank-bm25 corpus preloaded into memory.
  - Implement score fusion (Reciprocal Rank Fusion or weighted sum) and dedup by `(document_id, chunk_id)`.
  - Normalize fused score to [0,1] and include on each chunk as `fused_score`.

- Confidence and citations
  - Confidence = combine `fused_score` and citation match quality:
    - Base `retrieval_confidence = fused_score`.
    - If citation JSON parses and matches, bump confidence; else fallback to `retrieval_confidence`.
  - Deterministic fallback if JSON invalid or empty:
    - Select top `k` merged chunks; construct citations with quotes clipped to relevant lines; fill `confidence = retrieval_confidence`.
  - Update `/query` response:
    - `answer`, `citations[]`, `chunks_retrieved: { vector, keyword, merged }`, `chunks_used[]` (the merged chunks with id/text/score), `reasoning_summary` (1–2 sentences).

- Reasoning module (safe)
  - Use an internal prompt to produce a short `reasoning_summary`. Do not log or return raw chain-of-thought.
  - Add `REASONING_SUMMARY_PROMPT` in `rag-prompts.md` and implement in `agent/nodes.py`.
  - Gate by `config.ENABLE_REASONING_SUMMARY`.

- Performance and reliability
  - Preload indices on startup: load FAISS and BM25 once in `app lifespan` or module-level singletons.
  - Batch embeddings in ingestion; cap batch size; reuse HTTP session for OpenAI.
  - Add CORS middleware with allowed origins (for dev, `http://localhost:5000` if you choose direct JS).
  - Introduce `schemas.py` for Pydantic models: request/response schemas for `/ingest`, `/query`, `/documents`, `/chunk/{id}`.
  - Fix `agent/nodes.py`:
    - Replace `langchain_openai` with OpenAI SDK.
    - Stop importing `..prompts` if deleted; centralize prompts in `src/config.py` or re-add `src/prompts.py` per `rag-prompts.md`.
    - Fix incorrect f-string in chunk formatting: use `c["chunk_id"]`, not `c[chunk_id]`.
  - Logging/tracing:
    - Log timings for vector, keyword, merge, generation, citations.
    - Log `chunks_retrieved` counts and top fused scores.

- Data persistence
  - On ingest, write/update `data/indices/documents.json` with document metadata (id, filename, chunks, indexed_at).
  - Ensure FAISS `.meta.npy` contains per-chunk metadata: `document_id`, `chunk_id`, `text`, `page_number?`, `chunk_index`.
  - Ensure BM25 corpus mirrors the same ids for traceability.

### Frontend updates to support traceability UX

- Keep UI and structure; switch data to real backend via proxy:
  - Replace sample data usage with proxy calls (already wired via `/api/...`).
  - In chunk list, compute confidence from `responseData.citations` by `chunk_id`; if missing, display `fused_score`-based percentage.
  - When a chat response is clicked, populate column 2 with `data.chunks_used[]` and use `data.citations[]` to annotate confidence.
  - When a chunk is clicked, call `/api/chunk/{chunk_id}` and display `chunk`, `document`, `source_lines`.
- Minor JS tweaks:
  - If `reasoning_summary` is present, show it under the assistant message in a subtle “Why this answer” block (optional).
  - Better empty states and error messaging for network errors.
- Flask proxy handlers:
  - Forward headers and payloads faithfully; handle multipart for `/api/upload` → backend `/ingest`.
  - Read `BACKEND_URL` from env to switch easily.

### Status
I reviewed the key backend modules and confirmed current routes; next I’ll start by drafting concrete doc edits and a thin Flask proxy to the backend so the FE works end-to-end without CORS complexity.

- I’ll update the docs (foundation, plan, prompts, reality-checks, runbooks, structure, READMEs, changelog).
- I’ll add backend endpoints: `/documents`, `/chunk/{id}`, deterministic citations, confidence normalization, and a safe `reasoning_summary`.
- I’ll wire the frontend to the backend via Flask proxy and adjust the UI to use real data.

- Key changes to highlight:
  - Reintroduce `documents` and `chunks` APIs with consistent envelopes.
  - Deterministic citation fallback ensures citations always present.
  - Confidence derived from fused retrieval score with optional citation boost.
  - FE remains simple; backend does the heavy lifting; proxy avoids CORS.
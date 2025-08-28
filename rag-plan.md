# PLAN - LangGraph Hybrid RAG with Citations

## Overview
Build a production-grade hybrid RAG system with citation tracking in 2 weeks. All capabilities (vector + keyword retrieval, merge, generation, citation, reasoning summary) run on every query; validation never accepts degraded modes.

## Phase 1: Basic Infrastructure (Days 1-3)
**Goal**: Scaffold app, local indices, and basic document storage (no Docker)

### Day 1: Setup
- [ ] Create project structure from STRUCTURE.md
- [ ] Create `.env` and `.env.example`
- [ ] Install Python dependencies
- [ ] Create FastAPI skeleton with `/health`
- [ ] Add config with backend selection (FAISS/BM25 default)
- [ ] Add structured logs (step, timings, sizes, ids) — no noisy prints
- [ ] Define Pydantic schemas for chunks, citations, query/ingest I/O

**Validation**: 
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8050 --reload
curl localhost:8050/health  # returns {"success": true}
```

### Day 2-3: Document Ingestion
- [ ] Build document loader (PDF, TXT)
- [ ] Implement chunking (400 tokens, 50 overlap)
- [ ] Create embeddings with OpenAI (batching)
- [ ] Store vectors in FAISS and text in BM25 (local)
- [ ] Persist document metadata in `data/generated_indices/documents.json`
- [ ] Add /ingest endpoint
- [ ] Standardize artifacts under `data/generated_indices/` and inputs in `data/documents/` or `real_data/`

**Validation**:
```bash
curl -X POST -F "file=@test.pdf" localhost:8050/ingest
# Should return: {"success": true, "data": {"chunks_created": 10}}
```

## Phase 2: Dual Retrieval System (Days 4-6)
**Goal**: Implement both search methods (FAISS + BM25) and merge results

### Day 4: Vector Search
- [ ] Implement FAISS search (in-memory warmup)
- [ ] Add similarity scoring
- [ ] Return top-k chunks with metadata (`document_id`, `chunk_id`, `text`, `score`)
- [ ] Test with semantic queries

### Day 5: Keyword Search
- [ ] Implement rank-bm25 search (preload corpus in memory)
- [ ] Add relevance scoring
- [ ] Return top-k chunks with aligned metadata
- [ ] Test with exact matches

### Day 6: Merge Strategy
- [ ] Combine results from both searches (RRF or weighted fusion)
- [ ] Deduplicate by `(document_id, chunk_id)`
- [ ] Normalize to `fused_score` ∈ [0,1]
- [ ] Keep top-k merged results
- [ ] Produce `chunks_retrieved` counts {vector, keyword, merged}

**Validation**:
```python
# Both searches should return results
vector_results = vector_search("deployment process")
keyword_results = keyword_search("deployment process")
merged = merge_results(vector_results, keyword_results)
assert len(merged) > 0
```

## Phase 3: LangGraph Workflow (Days 7-10)
**Goal**: Build the agent that orchestrates RAG and generates answers

### Day 7-8: Graph Setup
- [ ] Define RAGState schema (Pydantic)
- [ ] Create nodes (retrieve, merge, generate, cite, reasoning_summary)
- [ ] Connect nodes with edges
- [ ] Add workflow compilation
- [ ] Test with mock data

### Day 9: Answer Generation
- [ ] Implement generate_answer node (OpenAI SDK; no raw CoT)
- [ ] Add prompts from PROMPTS.md (cap tokens; never reveal reasoning)
- [ ] Handle no-results case
- [ ] Test answer quality

### Day 10: Citation & Reasoning
- [ ] Implement citation extraction with strict JSON parsing
- [ ] Map claims to chunks by `chunk_id`
- [ ] Add confidence scores derived from `fused_score` (+matching boost)
- [ ] Include `reasoning_summary` (1–2 sentences, safe)
- [ ] Include in response

**Validation**:
```bash
curl -X POST localhost:8050/query -H "Content-Type: application/json" -d '{"question":"What is deployment?"}'
# Response must include citations[], chunks_used[], reasoning_summary, and chunks_retrieved
```

## Phase 4: Polish and Testing (Days 11-14)
**Goal**: Make it production-ready (local-first)

### Day 11-12: Error Handling & Logging
- [ ] Add try-catch blocks with structured errors
- [ ] Handle missing documents
- [ ] Add input validation via Pydantic
- [ ] Improve error messages
- [ ] Structured logs for each step (inputs/outputs/timings)

### Day 13: Performance
- [ ] Add basic caching
- [ ] Batch embeddings
- [ ] Optimize chunk size
- [ ] Preload indices (FAISS/BM25)
- [ ] Profile slow queries

### Day 14: Documentation & Testing
- [ ] Write README with examples
- [ ] Create test_pipeline.py
- [ ] Add example documents (download script)
- [ ] Record demo video

### Optional: Production Backends & Dockerization (Post-MVP)
- [ ] Add Qdrant/Elasticsearch adapters
- [ ] Add docker-compose for services
- [ ] Update README for production mode

**Final Validation**:
```bash
python test_pipeline.py
# All tests should pass
```

## Daily Debug Pattern (Structured)
Each day, use structured step logs:
```python
def log_step(name: str, **fields):
    # Structured logging placeholder; replace with proper logger
    print({"step": name, **fields})
```

## What to Skip (Not MVP)
- Reranking models
- Query expansion
- Semantic chunking
- Multi-language support
- User feedback loop
- A/B testing
- Streaming responses

## Success Criteria
The system is ready when:
1. Can ingest PDF/TXT documents.
2. Both vector and keyword search return results on every query.
3. Answers include proper citations and reasoning_summary.
4. End-to-end logs are structured and noise-free.
5. Works on realistic test corpora from `real_data/`.
6. Another engineer can run it with README and see precise step logs.
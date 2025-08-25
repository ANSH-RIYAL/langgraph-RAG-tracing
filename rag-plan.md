# PLAN - LangGraph Hybrid RAG with Citations

## Overview
Build a working hybrid RAG system with citation tracking in 2 weeks. Focus on getting the core pipeline working before adding refinements.

## Phase 1: Basic Infrastructure (Days 1-3)
**Goal**: Scaffold app, local indices, and basic document storage (no Docker)

### Day 1: Setup
- [ ] Create project structure from STRUCTURE.md
- [ ] Create `.env` and `.env.example`
- [ ] Install Python dependencies
- [ ] Create FastAPI skeleton with `/health`
- [ ] Add config with backend selection (FAISS/BM25 default)

**Validation**: 
```bash
uvicorn src.api.main:app --reload
curl localhost:8000/health  # returns {"success": true}
```

### Day 2-3: Document Ingestion
- [ ] Build document loader (PDF, TXT)
- [ ] Implement chunking (400 tokens, 50 overlap)
- [ ] Create embeddings with OpenAI
- [ ] Store vectors in FAISS and text in BM25 (local)
- [ ] Add /ingest endpoint

**Validation**:
```bash
curl -X POST -F "file=@test.pdf" localhost:8000/ingest
# Should return: {"success": true, "data": {"chunks_created": 10}}
```

## Phase 2: Dual Retrieval System (Days 4-6)
**Goal**: Implement both search methods (FAISS + BM25) and merge results

### Day 4: Vector Search
- [ ] Implement FAISS search
- [ ] Add similarity scoring
- [ ] Return top-k chunks
- [ ] Test with simple queries

### Day 5: Keyword Search
- [ ] Implement rank-bm25 search
- [ ] Add relevance scoring
- [ ] Return top-k chunks
- [ ] Test with exact matches

### Day 6: Merge Strategy
- [ ] Combine results from both searches
- [ ] Deduplicate chunks
- [ ] Sort by combined score
- [ ] Keep top-k merged results

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
- [ ] Define RAGState schema
- [ ] Create nodes (retrieve, generate, cite)
- [ ] Connect nodes with edges
- [ ] Add workflow compilation
- [ ] Test with mock data

### Day 9: Answer Generation
- [ ] Implement generate_answer node
- [ ] Add prompts from PROMPTS.md
- [ ] Handle no-results case
- [ ] Test answer quality

### Day 10: Citation Extraction
- [ ] Implement citation extraction
- [ ] Map claims to chunks
- [ ] Add confidence scores
- [ ] Include in response

**Validation**:
```bash
curl -X POST localhost:8000/query -d '{"question":"What is deployment?"}'
# Response must include citations array with source_doc and chunk_id
```

## Phase 4: Polish and Testing (Days 11-14)
**Goal**: Make it production-ready (local-first)

### Day 11-12: Error Handling
- [ ] Add try-catch blocks
- [ ] Handle missing documents
- [ ] Add input validation
- [ ] Improve error messages

### Day 13: Performance
- [ ] Add basic caching
- [ ] Batch embeddings
- [ ] Optimize chunk size
- [ ] Profile slow queries

### Day 14: Documentation & Testing
- [ ] Write README with examples
- [ ] Create test_pipeline.py
- [ ] Add example documents
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

## Daily Debug Pattern
Each day, use this debug approach:
```python
# Add to code temporarily
def debug_state(state, step_name):
    print(f"\n=== {step_name} ===")
    print(f"State keys: {state.keys()}")
    for key, value in state.items():
        if isinstance(value, list):
            print(f"{key}: {len(value)} items")
        elif isinstance(value, str):
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {value}")
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
1. Can ingest PDF/TXT documents
2. Both vector and keyword search return results
3. Answers include proper citations
4. Works on a test document consistently
5. Another engineer can run it with README
# RUNBOOKS - LangGraph Hybrid RAG with Citations

## Common Issues and Fixes

### "Wrong/Irrelevant Answer"
**Symptoms**: Answer doesn't match the question or uses wrong information

**Debug Steps**:
1. Check retrieved chunks with structured logs:
```python
log_step("retrieval", vector=len(state["vector_chunks"]), keyword=len(state["keyword_chunks"]), merged=len(state["merged_chunks"]))
```

2. Verify chunk relevance:
- Are the right chunks being retrieved?
- Is the merge strategy keeping the best chunks?
- Is the context truncation cutting important info?

**Common Fixes**:
- Adjust chunk size (smaller = more precise)
- Increase retrieval top_k
- Tune merge weights between vector/keyword
 - Verify FAISS and BM25 indices exist and are current

### "No Documents Found"
**Symptoms**: Query returns no results despite relevant docs existing

**Debug Steps**:
1. Check if document is indexed:
```bash
curl localhost:8050/documents
# Verify document appears
```

2. Test searches directly (local backends):
```python
from src.retrieval.vector_search import vector_search
from src.retrieval.text_search import keyword_search
print({"vector": vector_search("test query")[:3]})
print({"keyword": keyword_search("test query")[:3]})
```

**Common Fixes**:
- Reindex the document
- Check for typos/special characters
- Verify embeddings were created
 - Delete `data/generated_indices/*` and re-ingest

### "Citations Don't Match Answer"
**Symptoms**: Citations reference wrong chunks or don't support claims

**Debug Steps**:
1. Print the citation extraction input/output:
```python
print(f"Answer: {answer}")
print(f"Chunks provided: {chunks}")
print(f"Extracted citations: {citations}")
```

2. Verify chunk IDs are consistent

**Common Fix**:
- Ensure chunk_id is preserved through entire pipeline
- Check citation prompt is clear enough

## Performance Issues

### Slow Ingestion
**Target**: <2 seconds per PDF page

**Debug**:
```python
import time
start = time.time()
chunks = chunker.chunk_document(doc)
print(f"Chunking: {time.time() - start}s")

start = time.time()
embeddings = embed_chunks(chunks)
print(f"Embedding: {time.time() - start}s")
```

**Fixes**:
- Batch embeddings (up to 20 at once)
- Use async for database operations
 - Use memory-mapped FAISS indices

### Slow Queries
**Target**: <3 seconds total

**Debug**:
```python
# Add timing to each node
def timed_node(name, func):
    def wrapper(state):
        start = time.time()
        result = func(state)
        print(f"{name}: {time.time() - start:.2f}s")
        return result
    return wrapper
```

**Fixes**:
- Reduce chunks retrieved
- Cache embeddings for common queries
- Use connection pooling for databases
 - Preload BM25 corpus in memory

## Index/Adapter Issues

### FAISS/BM25 Not Found or Out-of-Date
```bash
ls -lah data/generated_indices/
# Expect vector.faiss (+ .meta.npy) and bm25/ directory, documents.json
```
```bash
# Reset indices
rm -rf data/generated_indices/*
python -m scripts.test_pipeline  # re-ingest during tests
```

### Switching to Qdrant/Elasticsearch (Optional, Post-MVP)
1. Set env: `VECTOR_BACKEND=qdrant`, `KEYWORD_BACKEND=elasticsearch`
2. Set `QDRANT_URL` and `ELASTICSEARCH_URL`
3. Run migration script to push local indices (to be added later)

## Frontend/Backend Connectivity

- Default dev: Backend at http://localhost:8050, Frontend at http://localhost:5000
- Use Flask proxy routes `/api/*` to forward to backend; or enable CORS in FastAPI.
- Common issue: CORS. Prefer proxy to avoid browser CORS in dev.

## Validation Checklist

After any changes, verify:
```bash
# 1. Upload test document
curl -X POST -F "file=@test.pdf" localhost:8050/ingest

# 2. Simple query
curl -X POST localhost:8050/query \
  -d '{"question":"What is this document about?"}'

# 3. Check citations exist
# Response should have citations array with source_doc and chunk_id

# 4. Verify both search methods work (FAISS + BM25)
# Check logs for "Vector chunks: X, Keyword chunks: Y"
```
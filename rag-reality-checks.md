# REALITY_CHECKS - LangGraph Hybrid RAG with Citations

## Test Documents
Store these in `test_documents/` (use the download script `scripts/download_test_docs.sh`):

### aws_well_architected_framework.pdf
- Public AWS whitepaper (~100+ pages)
- Expected chunks: 200-300
- Key terms: "reliability", "operational excellence", "security", "cost optimization", "performance efficiency"

### nist_sp_800_53r5.pdf
- NIST security controls (very large)
- Expected chunks: 500+
- Key terms: "access control", "audit", "risk management"

### faq.txt
- 20+ Q&A pairs simulating internal SRE/DevOps FAQ
- Format: "Q: ... A: ..."

## Test Queries and Expected Results

### Test 1: Exact Keyword Match
```json
{
  "question": "What is staging?",
  "expected": {
    "keyword_chunks": ">0",
    "vector_chunks": ">=0",
    "answer_contains": ["staging environment", "testing"],
    "citations_count": ">=1"
  }
}
```

### Test 2: Semantic Query
```json
{
  "question": "How do we test before going live?",
  "expected": {
    "vector_chunks": ">0",
    "keyword_chunks": ">=0",
    "answer_contains": ["staging", "testing"],
    "citations_count": ">=1"
  }
}
```

### Test 3: No Results Query
```json
{
  "question": "What is the recipe for pizza?",
  "expected": {
    "chunks_retrieved": 0,
    "answer": "I cannot find that information in the documents"
  }
}
```

## Quick Validation Script
```python
# test_pipeline.py
import requests
import json

def test_rag_pipeline():
    base_url = "http://localhost:8000"
    
    # 1. Upload document
    print("Uploading test document...")
    with open("test_documents/aws_well_architected_framework.pdf", "rb") as f:
        response = requests.post(
            f"{base_url}/ingest",
            files={"file": f}
        )
    assert response.json()["success"]
    chunks = response.json()["data"]["chunks_created"]
    assert chunks >= 100, f"Unexpected chunks: {chunks}"
    
    # 2. Test keyword query
    print("Testing keyword search...")
    response = requests.post(
        f"{base_url}/query",
        json={"question": "What is the purpose of a staging environment?"}
    )
    result = response.json()
    assert result["success"]
    assert len(result["data"]["citations"]) > 0
    assert "staging" in result["data"]["answer"].lower()
    
    # 3. Test semantic query
    print("Testing semantic search...")
    response = requests.post(
        f"{base_url}/query",
        json={"question": "How do we test changes before going live?"}
    )
    result = response.json()
    assert result["success"]
    assert len(result["data"]["citations"]) > 0
    
    # 4. Test no results
    print("Testing no results case...")
    response = requests.post(
        f"{base_url}/query",
        json={"question": "Recipe for pizza?"}
    )
    result = response.json()
    assert result["success"]
    assert "cannot find" in result["data"]["answer"].lower()
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_rag_pipeline()
```

## Expected Performance
- Document ingestion: <2s per page
- Simple query: <2s
- Complex query: <3s
- Both search methods return results: >80% of queries

## Debug Output Format
When debugging is enabled, you should see:
```
=== RETRIEVAL DEBUG ===
Vector search: 3 chunks (scores: [0.89, 0.76, 0.72])
Keyword search: 4 chunks (scores: [0.95, 0.88, 0.75, 0.71])
Merged: 5 unique chunks
=== GENERATION DEBUG ===
Context tokens: 1247
Answer tokens: 156
Citations extracted: 3
```
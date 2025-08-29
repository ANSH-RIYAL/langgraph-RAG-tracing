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
FAISS_INDEX_PATH=data/generated_indices/vector.faiss
BM25_INDEX_DIR=data/generated_indices/bm25
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
- POST `/query`: body `{question, max_chunks?}`; returns `{answer, citations[], chunks_retrieved, chunks_used[], reasoning_summary}`
- GET `/documents`: lists indexed documents with chunk counts and timestamps
- GET `/chunk/{chunk_id}`: details for a specific chunk, with document metadata and source lines

See `rag-structure.md` for the complete project layout and invariants. Realistic corpora should be stored under `real_data/`.

## Real JSON Examples

- Init on real_data
Request:
```bash
curl -s -X POST http://localhost:8050/init -H 'Content-Type: application/json' \
  -d '{"data_dir":"/Users/anshriyal/Downloads/github/Langgraph_projects/langgraph-RAG-tracing/real_data/final_docs"}'
```
Response (real):
```json
{
  "success": true,
  "data": {
    "processed_files": [
      "/Users/anshriyal/Downloads/github/Langgraph_projects/langgraph-RAG-tracing/real_data/final_docs/market_AVGO.csv",
      "... many CSV and SEC JSON files ...",
      "/Users/anshriyal/Downloads/github/Langgraph_projects/langgraph-RAG-tracing/real_data/final_docs/sec_companyfacts_CIK0000070858.json"
    ],
    "chunks_indexed": 46
  },
  "error": null
}
```

- Comparison: EPS 2023 (Amazon vs Apple)
Request:
```bash
curl -s -X POST http://localhost:8050/query -H 'Content-Type: application/json' \
  -d '{"question":"Compare Amazon 2023 EPS vs Apple 2023 EPS"}' | jq .
```
Response (real):
```json
{
  "success": true,
  "data": {
    "answer": "Apple's 2023 Earnings Per Share (EPS) is 5.61 USD/shares (chunk_id=doc_15562860_chunk_0). Amazon's 2023 EPS is not present in the provided chunks. Therefore, I cannot provide a comparison for Amazon's 2023 EPS.",
    "citations": [
      {
        "claim": "Apple's 2023 Earnings Per Share (EPS) is 5.61 USD/shares",
        "quote": "Apple Inc. 2023 EarningsPerShareDiluted: 5.61 USD/shares",
        "source_doc": null,
        "chunk_id": "doc_15562860_chunk_0",
        "page_number": null,
        "confidence": 1.0
      },
      {
        "claim": "Amazon's 2023 EPS is not present in the provided chunks",
        "quote": "Amazon's 2023 EPS is not present in the provided chunks.",
        "source_doc": null,
        "chunk_id": "doc_15562860_chunk_0",
        "page_number": null,
        "confidence": 1.0
      }
    ],
    "chunks_retrieved": {
      "vector": 5,
      "keyword": 5,
      "merged": 6
    },
    "chunks_used": [
      { "chunk_id": "doc_15562860_chunk_0", "source_doc": "sec_companyfacts_CIK0000320193.json", "text": "... Apple 2023 EPS 5.61 ..." },
      { "chunk_id": "doc_72269739_chunk_0", "source_doc": "sec_companyfacts_CIK0001018724.json", "text": "... AMAZON.COM, INC. 2023 EPS 3.24 ..." }
    ],
    "reasoning_summary": "..."
  },
  "error": null
}
```

- Comparison: Net Income 2023 (Amazon vs Apple)
Request:
```bash
curl -s -X POST http://localhost:8050/query -H 'Content-Type: application/json' \
  -d '{"question":"Compare Amazon 2023 Net Income vs Apple 2023 Net Income"}' | jq .
```
Response (real):
```json
{
  "success": true,
  "data": {
    "answer": "Apple's 2023 Net Income is 94,680,000,000.0 USD (chunk_id=doc_15562860_chunk_0). The Net Income for Amazon in 2023 is not present in the provided chunks. Therefore, I cannot provide a comparison for Amazon's 2023 Net Income.",
    "citations": [
      {
        "claim": "Apple's 2023 Net Income is 94,680,000,000.0 USD",
        "quote": "Apple Inc. 2023 NetIncomeLoss: 94680000000.0 USD",
        "source_doc": null,
        "chunk_id": "doc_15562860_chunk_0",
        "page_number": null,
        "confidence": 1.0
      },
      {
        "claim": "The Net Income for Amazon in 2023 is not present in the provided chunks.",
        "quote": "The Net Income for Amazon in 2023 is not present in the provided chunks.",
        "source_doc": null,
        "chunk_id": "doc_15562860_chunk_0",
        "page_number": null,
        "confidence": 1.0
      }
    ],
    "chunks_retrieved": { "vector": 5, "keyword": 5, "merged": 6 },
    "chunks_used": [ { "chunk_id": "doc_15562860_chunk_0", "source_doc": "sec_companyfacts_CIK0000320193.json" } ],
    "reasoning_summary": "..."
  },
  "error": null
}
```

- Which company had higher Revenues in 2023: Amazon or Apple?
Request:
```bash
curl -s -X POST http://localhost:8050/query -H 'Content-Type: application/json' \
  -d '{"question":"Which company had higher Revenues in 2023: Amazon or Apple?"}' | jq .
```
Response (real):
```json
{
  "success": true,
  "data": {
    "answer": "I cannot find that information in the documents.",
    "citations": [ { "claim": "I cannot find that information in the documents.", "quote": "I cannot find that information in the documents.", "chunk_id": "doc_15562860_chunk_0", "confidence": 1.0 } ],
    "chunks_retrieved": { "vector": 5, "keyword": 5, "merged": 6 },
    "chunks_used": [ { "chunk_id": "doc_15562860_chunk_0", "source_doc": "sec_companyfacts_CIK0000320193.json" } ],
    "reasoning_summary": "..."
  },
  "error": null
}
```

- YoY change: Apple Revenues 2022 → 2023
Request:
```bash
curl -s -X POST http://localhost:8050/query -H 'Content-Type: application/json' \
  -d '{"question":"Show YoY change for Apple Revenues from 2022 to 2023"}' | jq .
```
Response (real):
```json
{
  "success": true,
  "data": {
    "answer": "Apple Inc. Revenues for 2022 were 215,639,000,000.0 USD (chunk_id=doc_15562860_chunk_0) and for 2023 were not explicitly stated in the provided data. Therefore, I cannot find that information in the documents.",
    "citations": [
      {
        "claim": "Apple Inc. Revenues for 2022 were 215,639,000,000.0 USD",
        "quote": "Apple Inc. 2018 Revenues: 215639000000.0 USD",
        "chunk_id": "doc_15562860_chunk_0",
        "confidence": 0.95
      },
      {
        "claim": "for 2023 were not explicitly stated in the provided data",
        "quote": "Apple Inc. 2023 Revenues: not explicitly stated",
        "chunk_id": "doc_15562860_chunk_0",
        "confidence": 0.9
      }
    ],
    "chunks_retrieved": { "vector": 5, "keyword": 5, "merged": 6 },
    "chunks_used": [ { "chunk_id": "doc_15562860_chunk_0", "source_doc": "sec_companyfacts_CIK0000320193.json" } ],
    "reasoning_summary": "..."
  },
  "error": null
}
```

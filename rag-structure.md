# STRUCTURE - LangGraph Hybrid RAG with Citations

## Directory Layout
```
langgraph-hybrid-rag/
├── src/
│   ├── ingestion/
│   │   ├── loader.py          # Load PDFs, DOCX, TXT
│   │   ├── chunker.py         # Split into 400-token chunks
│   │   └── indexer.py         # Store embeddings/text in local indices
│   │
│   ├── retrieval/
│   │   ├── backends/
│   │   │   ├── faiss_store.py  # Local FAISS vector store
│   │   │   ├── bm25_store.py   # Local BM25 keyword store
│   │   │   ├── qdrant_store.py # Optional (stub)
│   │   │   └── es_store.py     # Optional (stub)
│   │   ├── vector_search.py    # Vector retrieval via configured backend
│   │   ├── text_search.py      # Keyword retrieval via configured backend
│   │   └── merger.py          # Combine and dedupe results
│   │
│   ├── agent/
│   │   ├── workflow.py        # LangGraph definition
│   │   ├── nodes.py           # Retrieve, Generate, Cite
│   │   └── state.py           # Workflow state schema
│   │
│   ├── api/
│   │   ├── main.py           # FastAPI app
│   │   ├── ingest.py         # POST /ingest endpoint
│   │   └── query.py          # POST /query endpoint
│   │
│   └── config.py             # Settings, prompts, backend selection
│
├── data/
│   ├── documents/            # Uploaded files
│   └── indices/              # Vector/text indices (vector.faiss, bm25/)
│
├── scripts/
│   ├── download_test_docs.sh # Fetch large public PDFs and build FAQ
│   └── test_pipeline.py      # Basic validation
│
├── CHANGELOG.md             # Decisions, results, progress
├── docker-compose.yml       # Qdrant + Elasticsearch (post-MVP)
├── requirements.txt        
├── .env.example
├── .env                     # Local secrets (do not commit externally)
├── README.md
├── rag-foundation.md        # Knowledge doc
├── rag-plan.md              # Knowledge doc
├── rag-prompts.md           # Knowledge doc
├── rag-reality-checks.md    # Knowledge doc
├── rag-runbooks.md          # Knowledge doc
├── rag-structure.md         # Knowledge doc
└── original_chat_context.md # Source intent
```

## API Endpoints

### POST /ingest
Upload a document and index it.

**Request:**
```bash
curl -X POST -F "file=@document.pdf" \
  -F "metadata={\"source\":\"manual\"}" \
  localhost:8000/ingest
```

**Response:**
```json
{
  "success": true,
  "data": {
    "document_id": "doc_abc123",
    "chunks_created": 15,
    "status": "indexed"
  }
}
```

### POST /query
Ask a question and get cited answer.

**Request:**
```json
{
  "question": "What is our deployment process?",
  "max_chunks": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": "The deployment process involves three stages...",
    "citations": [
      {
        "text": "First, code is pushed to staging",
        "source_doc": "deployment_guide.pdf",
        "chunk_id": "chunk_123",
        "page_number": 5,
        "confidence": 0.89
      }
    ],
    "chunks_retrieved": {
      "vector": 3,
      "keyword": 4,
      "merged": 5
    }
  }
}
```

### GET /documents
List indexed documents.

**Response:**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "doc_abc123",
        "filename": "deployment_guide.pdf",
        "chunks": 15,
        "indexed_at": "2025-01-20T10:00:00Z"
      }
    ]
  }
}
```

## LangGraph Workflow Structure

```python
# State definition
class RAGState(TypedDict):
    question: str
    vector_chunks: List[Dict]
    keyword_chunks: List[Dict]
    merged_chunks: List[Dict]
    answer: str
    citations: List[Dict]

# Node functions
def retrieve_vector(state): ...
def retrieve_keyword(state): ...
def merge_results(state): ...
def generate_answer(state): ...
def extract_citations(state): ...

# Graph construction
workflow = StateGraph(RAGState)
workflow.add_node("vector_search", retrieve_vector)
workflow.add_node("keyword_search", retrieve_keyword)
workflow.add_node("merge", merge_results)
workflow.add_node("generate", generate_answer)
workflow.add_node("cite", extract_citations)

# Edges
workflow.add_edge(START, "vector_search")
workflow.add_edge(START, "keyword_search")
workflow.add_edge("vector_search", "merge")
workflow.add_edge("keyword_search", "merge")
workflow.add_edge("merge", "generate")
workflow.add_edge("generate", "cite")
workflow.add_edge("cite", END)
```

## Database Schemas

### Qdrant Collection
```yaml
collection_name: documents
vector_size: 1536  # OpenAI ada-002
distance: Cosine

payload_schema:
  document_id: string
  chunk_id: string
  text: string
  page_number: integer
  chunk_index: integer
```

### Elasticsearch Index
```json
{
  "mappings": {
    "properties": {
      "document_id": {"type": "keyword"},
      "chunk_id": {"type": "keyword"},
      "text": {"type": "text"},
      "page_number": {"type": "integer"},
      "chunk_index": {"type": "integer"}
    }
  }
}
```

## Configuration Structure
```python
# config.py
class Config:
    # Models
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o-mini"
    
    # Chunking
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50
    
    # Retrieval
    VECTOR_TOP_K = 5
    KEYWORD_TOP_K = 5
    MERGED_TOP_K = 5
    VECTOR_BACKEND = "faiss"          # or "qdrant"
    KEYWORD_BACKEND = "bm25"          # or "elasticsearch"
    FAISS_INDEX_PATH = "data/indices/vector.faiss"
    BM25_INDEX_DIR = "data/indices/bm25"
    QDRANT_URL = "http://localhost:6333"
    ELASTICSEARCH_URL = "http://localhost:9200"
    
    # Context
    MAX_CONTEXT_TOKENS = 3000
```
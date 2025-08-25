import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Models
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 400))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))

    # Retrieval
    VECTOR_TOP_K: int = int(os.getenv("VECTOR_TOP_K", 5))
    KEYWORD_TOP_K: int = int(os.getenv("KEYWORD_TOP_K", 5))
    MERGED_TOP_K: int = int(os.getenv("MERGED_TOP_K", 5))

    VECTOR_BACKEND: str = os.getenv("VECTOR_BACKEND", "faiss")  # or qdrant
    KEYWORD_BACKEND: str = os.getenv("KEYWORD_BACKEND", "bm25")  # or elasticsearch

    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "data/indices/vector.faiss")
    BM25_INDEX_DIR: str = os.getenv("BM25_INDEX_DIR", "data/indices/bm25")

    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))


config = Config()

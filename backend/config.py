import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    QDRANT_URL = os.getenv("QDRANT_URL", "").strip() or None
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip() or None
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "sanjivani_docs")
    # When QDRANT_URL is not set, we run Qdrant embedded on disk here — no server, no cost.
    QDRANT_LOCAL_PATH = os.getenv("QDRANT_LOCAL_PATH", "./qdrant_data")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sanjivani.db")

    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "../documents")
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
    ALLOWED_EXTENSIONS = {"pdf"}

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # local, free
    EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))       # characters
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))  # characters
    TOP_K = int(os.getenv("TOP_K", "5"))

    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # cheapest capable tier

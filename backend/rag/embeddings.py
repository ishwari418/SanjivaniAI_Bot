"""
Local, free embeddings via sentence-transformers — no per-call API cost.
The model is loaded once and reused (singleton) to keep memory/startup cost low.
"""
from sentence_transformers import SentenceTransformer

from config import Config

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(Config.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]

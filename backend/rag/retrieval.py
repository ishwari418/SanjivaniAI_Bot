"""
Vector store layer over Qdrant. Runs embedded (on-disk, in-process) by default — zero
infra cost, no Docker required. Set QDRANT_URL in .env to point at a hosted cluster instead;
nothing else in this file needs to change, which is the whole point of isolating it here.
"""
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

from config import Config

_client = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        if Config.QDRANT_URL:
            _client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)
        else:
            _client = QdrantClient(path=Config.QDRANT_LOCAL_PATH)
        _ensure_collection(_client)
    return _client


def _ensure_collection(client: QdrantClient):
    collections = [c.name for c in client.get_collections().collections]
    if Config.QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=Config.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=Config.EMBEDDING_DIM, distance=Distance.COSINE),
        )


def upsert_chunks(chunks: list[dict], vectors: list[list[float]], document_id: int):
    """chunks: list of dicts from ingestion.process_pdf, same order as vectors."""
    client = get_client()
    points = []
    for chunk, vector in zip(chunks, vectors):
        payload = {**chunk, "document_id": document_id}
        points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))
    if points:
        client.upsert(collection_name=Config.QDRANT_COLLECTION, points=points)
    return len(points)


def search(query_vector: list[float], top_k: int = None):
    client = get_client()
    top_k = top_k or Config.TOP_K
    results = client.search(
        collection_name=Config.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
    )
    return [
        {
            "score": r.score,
            "text": r.payload.get("text"),
            "document_name": r.payload.get("document_name"),
            "doc_type": r.payload.get("doc_type"),
            "page_number": r.payload.get("page_number"),
            "document_id": r.payload.get("document_id"),
        }
        for r in results
    ]


def delete_by_document_id(document_id: int):
    client = get_client()
    client.delete(
        collection_name=Config.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[{"key": "document_id", "match": {"value": document_id}}]
        ),
    )

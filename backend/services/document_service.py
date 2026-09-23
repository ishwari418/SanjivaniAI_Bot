import datetime
import os

from config import Config
from models.database import Document, get_session
from rag.ingestion import process_pdf
from rag.embeddings import embed_texts
from rag.retrieval import upsert_chunks, delete_by_document_id


def save_upload(file_storage) -> str:
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    dest_path = os.path.join(Config.UPLOAD_DIR, file_storage.filename)
    file_storage.save(dest_path)
    return dest_path


def index_document(document_id: int, pdf_path: str, doc_type: str = "general"):
    """Runs the full pipeline for one document and updates its DB status.
    Called synchronously right after upload — fine for a handful of PDFs; for larger
    knowledge bases, call this from a background worker/queue instead."""
    session = get_session()
    doc = session.get(Document, document_id)
    try:
        doc.status = "processing"
        session.commit()

        records = process_pdf(pdf_path, doc_name=doc.filename, doc_type=doc_type)
        if not records:
            doc.status = "failed"
            doc.error_message = "No extractable text found in PDF."
            session.commit()
            return

        texts = [r["text"] for r in records]
        vectors = embed_texts(texts)
        upsert_chunks(records, vectors, document_id=document_id)

        doc.status = "processed"
        doc.num_chunks = len(records)
        doc.processed_at = datetime.datetime.utcnow()
        doc.error_message = None
        session.commit()
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        session.commit()
        raise
    finally:
        session.close()


def reindex_document(document_id: int):
    session = get_session()
    doc = session.get(Document, document_id)
    if not doc:
        session.close()
        raise ValueError("Document not found")
    pdf_path = os.path.join(Config.UPLOAD_DIR, doc.filename)
    doc_type = doc.doc_type
    session.close()

    delete_by_document_id(document_id)
    index_document(document_id, pdf_path, doc_type=doc_type)


def delete_document(document_id: int):
    session = get_session()
    doc = session.get(Document, document_id)
    if not doc:
        session.close()
        raise ValueError("Document not found")
    pdf_path = os.path.join(Config.UPLOAD_DIR, doc.filename)
    session.delete(doc)
    session.commit()
    session.close()

    delete_by_document_id(document_id)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

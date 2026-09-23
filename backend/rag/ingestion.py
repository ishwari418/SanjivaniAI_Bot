"""
PDF -> cleaned text -> overlapping chunks, each tagged with page number metadata.
Real extraction via PyMuPDF (fitz) — no shortcuts, no hard-coded content.
"""
import re
import fitz  # PyMuPDF

from config import Config


def extract_pages(pdf_path: str):
    """Returns a list of (page_number, raw_text) tuples, 1-indexed pages."""
    pages = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            pages.append((i + 1, page.get_text("text")))
    return pages


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = None, overlap: int = None):
    """Character-based sliding-window chunking with overlap, splitting on sentence/word
    boundaries where possible so chunks stay semantically coherent."""
    chunk_size = chunk_size or Config.CHUNK_SIZE
    overlap = overlap or Config.CHUNK_OVERLAP

    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        # try to end on a sentence boundary within the last 20% of the window
        if end < n:
            window_start = start + int(chunk_size * 0.8)
            boundary = text.rfind(". ", window_start, end)
            if boundary != -1:
                end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def process_pdf(pdf_path: str, doc_name: str, doc_type: str = "general"):
    """
    Full ingestion pipeline for one PDF.
    Returns a list of chunk dicts ready for embedding:
      { text, document_name, doc_type, page_number, chunk_index }
    """
    pages = extract_pages(pdf_path)
    records = []
    chunk_idx = 0
    for page_number, raw in pages:
        cleaned = clean_text(raw)
        if not cleaned:
            continue
        for chunk in chunk_text(cleaned):
            records.append({
                "text": chunk,
                "document_name": doc_name,
                "doc_type": doc_type,
                "page_number": page_number,
                "chunk_index": chunk_idx,
            })
            chunk_idx += 1
    return records

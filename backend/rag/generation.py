"""
Generation layer: decides whether a question needs the Sanjivani knowledge base,
retrieves grounded context when it does, and calls Gemini to produce the answer.
Keeping this isolated means the LLM provider can be swapped without touching the rest
of the app (see README "Swapping the LLM provider").
"""
import google.generativeai as genai

from config import Config
from rag.embeddings import embed_query
from rag.retrieval import search

_configured = False

SYSTEM_PROMPT = """You are SanjivaniAI, an AI assistant for Sanjivani University.

When answering questions about Sanjivani University, use only the provided retrieved
context. Do not invent university rules, policies, dates, fees, procedures, or
regulations. If the retrieved context does not contain enough information, clearly
state that the information could not be found in the available Sanjivani University
documents, instead of guessing.

For general academic questions unrelated to Sanjivani University specifically, you may
answer using your own general knowledge, and should say so is general knowledge rather
than official university policy.

Be concise and direct. When you use retrieved context, do not restate the sources in
your answer text — they are shown separately."""

# Keywords that suggest the question is about Sanjivani-specific policy/records rather
# than general academic knowledge. This is a lightweight first-pass router; the second
# and stronger signal is simply "did retrieval return anything with a decent score".
COLLEGE_SIGNAL_WORDS = [
    "sanjivani", "attendance", "exam", "examination", "hostel", "scholarship",
    "placement", "fee", "fees", "admission", "semester", "credit", "regulation",
    "rule", "policy", "calendar", "backlog", "kt", "syllabus", "department",
    "university", "college", "campus", "degree", "b.tech", "btech",
]

RELEVANCE_SCORE_THRESHOLD = 0.35  # cosine similarity floor for "this chunk is relevant"


def _configure():
    global _configured
    if not _configured:
        if not Config.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env — see .env.example."
            )
        genai.configure(api_key=Config.GEMINI_API_KEY)
        _configured = True


def looks_college_specific(question: str) -> bool:
    q = question.lower()
    return any(word in q for word in COLLEGE_SIGNAL_WORDS)


def retrieve_context(question: str, top_k: int = None):
    vector = embed_query(question)
    results = search(vector, top_k=top_k)
    relevant = [r for r in results if r["score"] >= RELEVANCE_SCORE_THRESHOLD]
    return relevant


def build_context_block(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(
            f"[Source: {c['document_name']}, Page {c['page_number']}]\n{c['text']}"
        )
    return "\n\n---\n\n".join(parts)


def generate_answer(question: str) -> dict:
    """
    Runs the full router -> retrieve -> generate flow.
    Returns { answer, sources, mode, retrieved_chunks }
    """
    _configure()
    model = genai.GenerativeModel(Config.GEMINI_MODEL, system_instruction=SYSTEM_PROMPT)

    # We always attempt retrieval (cheap, local — no API cost) rather than trusting
    # keyword routing alone: e.g. "can I sit an exam with 68% attendance" doesn't say
    # "Sanjivani" but is clearly college-specific. Retrieval quality is the real router;
    # looks_college_specific() is kept as a documented signal you can use for logging
    # or stricter routing later.
    chunks = retrieve_context(question)

    if chunks:
        context_block = build_context_block(chunks)
        prompt = (
            f"Retrieved context from Sanjivani University documents:\n\n{context_block}"
            f"\n\n---\n\nQuestion: {question}\n\n"
            "Answer using only the retrieved context above. If it doesn't fully answer "
            "the question, say what's missing rather than filling the gap yourself."
        )
        mode = "rag"
    else:
        prompt = (
            f"Question: {question}\n\n"
            "No relevant Sanjivani University documents were found for this question. "
            "If this is a general academic question, answer it using your general "
            "knowledge and note that it isn't Sanjivani-specific policy. If it sounds "
            "like it should be Sanjivani-specific (e.g. about attendance, exams, fees, "
            "hostel, placements), clearly say the information could not be found in the "
            "available Sanjivani University documents rather than guessing."
        )
        mode = "general"

    response = model.generate_content(prompt)
    answer_text = response.text if hasattr(response, "text") else str(response)

    sources = [
        {"document_name": c["document_name"], "page_number": c["page_number"], "score": round(c["score"], 3)}
        for c in chunks
    ]
    # de-duplicate sources by (document, page)
    seen = set()
    deduped_sources = []
    for s in sources:
        key = (s["document_name"], s["page_number"])
        if key not in seen:
            seen.add(key)
            deduped_sources.append(s)

    return {
        "answer": answer_text,
        "sources": deduped_sources,
        "mode": mode,
        "retrieved_chunks": chunks,  # useful for the debug view; frontend can ignore
    }

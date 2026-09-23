from flask import Blueprint, request, jsonify

from rag.generation import generate_answer

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        result = generate_answer(question)
    except RuntimeError as e:
        # e.g. missing GEMINI_API_KEY
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to generate answer: {e}"}), 500

    debug_chunks = [
        {
            "document_name": c["document_name"],
            "page_number": c["page_number"],
            "score": round(c["score"], 3),
            "text_preview": c["text"][:200],
        }
        for c in result["retrieved_chunks"]
    ]

    return jsonify({
        "answer": result["answer"],
        "sources": result["sources"],
        "mode": result["mode"],
        "retrieved_chunks": debug_chunks,
    })

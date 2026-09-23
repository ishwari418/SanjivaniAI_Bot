import os
from functools import wraps

from flask import Blueprint, request, jsonify

from config import Config
from models.database import Document, get_session
from services import document_service

documents_bp = Blueprint("documents", __name__)


def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if not token or token != Config.ADMIN_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in Config.ALLOWED_EXTENSIONS


@documents_bp.route("/api/documents", methods=["GET"])
@require_admin
def list_documents():
    session = get_session()
    docs = session.query(Document).order_by(Document.uploaded_at.desc()).all()
    result = [d.to_dict() for d in docs]
    session.close()
    return jsonify(result)


@documents_bp.route("/api/documents/upload", methods=["POST"])
@require_admin
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file part named 'file'"}), 400
    file = request.files["file"]
    doc_type = request.form.get("doc_type", "general")

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > Config.MAX_UPLOAD_MB:
        return jsonify({"error": f"File exceeds {Config.MAX_UPLOAD_MB}MB limit"}), 400

    session = get_session()
    doc = Document(filename=file.filename, doc_type=doc_type, status="uploaded")
    session.add(doc)
    session.commit()
    document_id = doc.id
    session.close()

    pdf_path = document_service.save_upload(file)

    try:
        document_service.index_document(document_id, pdf_path, doc_type=doc_type)
    except Exception as e:
        # status already recorded as 'failed' inside index_document
        return jsonify({"error": f"Uploaded but indexing failed: {e}", "document_id": document_id}), 500

    session = get_session()
    doc = session.get(Document, document_id)
    result = doc.to_dict()
    session.close()
    return jsonify(result), 201


@documents_bp.route("/api/documents/<int:document_id>", methods=["DELETE"])
@require_admin
def delete_document(document_id):
    try:
        document_service.delete_document(document_id)
    except ValueError:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({"deleted": document_id})


@documents_bp.route("/api/documents/<int:document_id>/reindex", methods=["POST"])
@require_admin
def reindex_document(document_id):
    try:
        document_service.reindex_document(document_id)
    except ValueError:
        return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Reindex failed: {e}"}), 500

    session = get_session()
    doc = session.get(Document, document_id)
    result = doc.to_dict()
    session.close()
    return jsonify(result)

# SanjivaniAI

AI-powered knowledge assistant for Sanjivani University, built on real Retrieval-Augmented
Generation (RAG) — not a keyword search dressed up as AI, and not an LLM hard-coding answers
from memory.

```
User question → Flask → embed query → search Qdrant → retrieve chunks
             → Gemini (context + question) → grounded answer + sources → Next.js UI
```

## Why this build keeps costs low

This is deliberately scoped as a **lean MVP** rather than the full production stack, so you can
run and test it for free before paying for any infrastructure:

| Component | Full-scale choice | This build | Why |
|---|---|---|---|
| Vector DB | Qdrant Cloud (hosted) | **Qdrant embedded**, on-disk in `backend/qdrant_data/` | Zero hosting cost, no Docker needed, same client API — swap to hosted by setting `QDRANT_URL` |
| App DB | PostgreSQL | **SQLite** (`backend/sanjivani.db`) | Zero setup, single file — swap the `DATABASE_URL` in `.env` when you need concurrent writers |
| Embeddings | OpenAI/Gemini embedding API | **Local `sentence-transformers`** (`all-MiniLM-L6-v2`) | Runs on CPU, no per-chunk API cost — this is the expensive part of RAG if you use a hosted API |
| LLM | Gemini Pro | **Gemini 1.5 Flash** | Cheapest Gemini tier that's still good at grounded Q&A; only the *final answer* costs API calls, not retrieval |
| Auth | Full user auth (JWT/OAuth) | **Shared admin token** (`X-Admin-Token` header) | Enough to gate the admin dashboard for a solo/small-team project; upgrade path noted below |
| Deployment | Docker Compose, 3+ containers | **Run directly** with `python` / `npm run dev` | Nothing to containerize until you're actually deploying |

You still get the real pipeline end-to-end: PDF → extract → chunk → embed → store → retrieve →
generate → cite sources. Every step in `backend/rag/` is isolated so you can swap any one piece
(e.g. move to Qdrant Cloud, or Postgres, or a different LLM) without touching the others.

## Project structure

```
SanjivaniAI/
├── frontend/            Next.js + TypeScript + Tailwind chat UI + admin dashboard
├── backend/
│   ├── app.py            Flask entrypoint
│   ├── config.py          Env-driven config
│   ├── routes/            /api/chat, /api/documents/*, /api/health
│   ├── rag/                ingestion.py, embeddings.py, retrieval.py, generation.py
│   ├── models/            SQLite document metadata
│   └── services/          document_service.py ties the pipeline together
├── documents/            Drop your Sanjivani PDFs here (or upload via admin dashboard)
└── docker-compose.yml    Optional — only needed if you later move to hosted Qdrant/Postgres
```

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and set:
#   GEMINI_API_KEY=<your key from https://aistudio.google.com/apikey (free tier available)>
#   ADMIN_TOKEN=<any long random string>

python app.py
# → running on http://localhost:5000
```

The first run downloads the local embedding model (~90MB, one-time) and creates
`sanjivani.db` and `qdrant_data/` automatically — nothing else to provision.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → running on http://localhost:3000
```

### 3. Add documents

Either:
- Go to `http://localhost:3000/admin`, enter your `ADMIN_TOKEN`, and upload PDFs, or
- Drop PDFs into `documents/` and upload each once through the admin UI (uploads must go
  through the API so they get indexed — the folder itself is just storage).

Each upload runs the full pipeline synchronously (extract → chunk → embed → store) and the
dashboard shows live status: `uploaded → processing → processed` (or `failed`, with the
error message shown on hover).

### 4. Chat

Go to `http://localhost:3000` and ask a question. Answers about Sanjivani-specific topics are
grounded in whatever you've indexed, with source documents and page numbers shown under the
answer. If nothing relevant is indexed yet, the assistant says so rather than inventing policy.

## Swapping the LLM provider

`backend/rag/generation.py` is the only file that talks to Gemini. To add another provider,
implement the same `generate_answer(question)` interface in a new module and switch the import
in `routes/chat.py` — the retrieval pipeline doesn't need to change.

## Upgrade path (when you're ready to scale past the free tier)

- **Qdrant Cloud**: create a free cluster, set `QDRANT_URL` and `QDRANT_API_KEY` in `.env` —
  no code changes.
- **PostgreSQL**: set `DATABASE_URL=postgresql://user:pass@host/db` and add `psycopg2-binary`
  to `requirements.txt`.
- **Real auth**: replace the `require_admin` decorator in `routes/documents.py` with session-
  or JWT-based auth once there's more than one admin user.
- **Background indexing**: for large document sets, move `document_service.index_document`
  into a queue (Celery/RQ) instead of running it synchronously on upload.
- **Docker**: a `docker-compose.yml` is included as a starting point once you're deploying,
  not developing.

## API reference

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/health` | GET | none | Liveness check |
| `/api/chat` | POST | none | `{ question }` → `{ answer, sources, mode, retrieved_chunks }` |
| `/api/documents` | GET | admin | List all documents and their indexing status |
| `/api/documents/upload` | POST | admin | Multipart upload (`file`, `doc_type`) → indexes synchronously |
| `/api/documents/:id` | DELETE | admin | Deletes the file, its DB record, and its vectors |
| `/api/documents/:id/reindex` | POST | admin | Re-runs the pipeline for one document |

Admin routes require an `X-Admin-Token` header matching `ADMIN_TOKEN` in `backend/.env`.

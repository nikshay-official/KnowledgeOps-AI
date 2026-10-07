# KnowledgeOps AI

Production-style company knowledge assistant built to run natively on Windows — **no Docker, WSL, PostgreSQL server, or external vector database required**.

## Stack

- **Frontend:** React + TypeScript + Vite
- **API:** FastAPI + Pydantic
- **Metadata DB:** SQLite + SQLAlchemy + Alembic
- **Vector DB:** Qdrant in local/persistent mode
- **AI:** Google Gemini API (`gemini-embedding-2` + `gemini-2.5-flash`)
- **Documents:** TXT, PDF, DOCX
- **RAG:** semantic + lexical hybrid retrieval, context assembly, citations, grounded-answer guardrail
- **Evaluation:** retrieval/source-hit evaluation script
- **Testing:** pytest

## Overview

KnowledgeOps AI lets users upload company documents and ask natural-language questions grounded in those documents. Documents are parsed, cleaned, chunked, embedded, stored in Qdrant, and retrieved through a hybrid semantic + lexical ranking pipeline before Gemini generates a cited, grounded answer.

## Requirements

- Python 3.11+
- Node.js 18+
- A Gemini API key

## Local setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
Copy-Item .env.example .env
```

Add your Gemini API key to `.env`, then initialize the database:

```powershell
cd backend
alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## RAG flow

```text
Document Upload
      ↓
Parse TXT / PDF / DOCX
      ↓
Clean + Chunk
      ↓
Gemini Embeddings
      ↓
Qdrant Vector Store
      ↓
User Query → Query Embedding
      ↓
Semantic Retrieval + Lexical Scoring
      ↓
Hybrid Ranking
      ↓
Context Assembly
      ↓
Gemini Grounded Generation
      ↓
Answer + Citations / Knowledge Gap
```

## Evaluation

The repository includes a retrieval/source-hit evaluation script in `scripts/evaluate_rag.py` and backend tests covering document chunking.

## Production upgrade path

The architecture can later move to managed PostgreSQL, Qdrant Cloud/server mode, object storage, authentication and multi-tenancy, reranking, async ingestion workers, and OpenTelemetry without rewriting the core UI or RAG service.

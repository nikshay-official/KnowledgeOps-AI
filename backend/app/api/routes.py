import json
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Document, Message
from app.ingestion.parsers import SUPPORTED
from app.rag.retriever import HybridRetriever
from app.schemas.api import ChatRequest, ChatResponse, Citation, DocumentOut
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status": "ok", "service": "knowledgeops-api"}

@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.scalars(select(Document).order_by(Document.created_at.desc())).all()

@router.post("/documents/upload", response_model=DocumentOut)
async def upload_document(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED:
        raise HTTPException(400, "Supported files: .txt, .pdf, .docx")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Maximum file size is {settings.max_upload_mb} MB")
    temp_dir = Path("data/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}{suffix}"
    path = temp_dir / safe_name
    path.write_bytes(content)
    try:
        service = IngestionService(request.app.state.vector_store, request.app.state.gemini)
        return service.ingest(db, path, file.filename or safe_name, file.content_type or "application/octet-stream", len(content))
    except Exception as exc:
        raise HTTPException(500, f"Ingestion failed: {exc}") from exc
    finally:
        path.unlink(missing_ok=True)

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, request: Request, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    request.app.state.vector_store.delete_document(document_id)
    db.delete(document)
    db.commit()
    return {"deleted": True}

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, http_request: Request, db: Session = Depends(get_db)):
    start = time.perf_counter()
    conversation_id = request.conversation_id or uuid4().hex
    try:
        retriever = HybridRetriever(http_request.app.state.vector_store, http_request.app.state.gemini)
        results = retriever.retrieve(request.question)
        if not results or results[0]["score"] < 0.32:
            answer = "I couldn't find enough information in the knowledge base to answer that reliably."
            citations = []
        else:
            context_parts = []
            citations = []
            total = 0
            for index, item in enumerate(results, 1):
                block = f"[Source {index}] {item['document_name']}\n{item['text']}"
                if total + len(block) > get_settings().max_context_chars:
                    break
                context_parts.append(block)
                total += len(block)
                citations.append(Citation(document_id=int(item["document_id"]), document_name=item["document_name"], chunk_id=int(item["chunk_id"]), page_number=item.get("page_number"), score=round(float(item["score"]), 4), snippet=item["text"][:240]))
            context = "\n\n".join(context_parts)
            answer = retriever.gemini.generate(request.question, context)
        db.add(Message(conversation_id=conversation_id, role="user", content=request.question, citations_json=[]))
        db.add(Message(conversation_id=conversation_id, role="assistant", content=answer, citations_json=[c.model_dump() for c in citations]))
        db.commit()
        elapsed = round((time.perf_counter() - start) * 1000)
        print(json.dumps({"event": "rag_request", "conversation_id": conversation_id, "retrieved": len(results), "latency_ms": elapsed}))
        return ChatResponse(answer=answer, citations=citations, conversation_id=conversation_id, retrieved_count=len(results))
    except Exception as exc:
        raise HTTPException(500, f"RAG request failed: {exc}") from exc

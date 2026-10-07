from pathlib import Path
from uuid import uuid4
from qdrant_client.models import PointStruct
from sqlalchemy.orm import Session
from app.db.models import Document, DocumentChunk
from app.ingestion.parsers import chunk_text, clean_text, extract_text
from app.rag.vector_store import VectorStore
from app.services.gemini import GeminiService

class IngestionService:
    def __init__(self, vector_store: VectorStore, gemini: GeminiService): self.gemini = gemini; self.vectors = vector_store
    def ingest(self, db: Session, file_path: Path, filename: str, content_type: str, size_bytes: int):
        document = Document(filename=filename, content_type=content_type, size_bytes=size_bytes, status="processing")
        db.add(document); db.commit(); db.refresh(document)
        try:
            raw, _ = extract_text(file_path); text = clean_text(raw); chunks = chunk_text(text)
            if not chunks: raise ValueError("No readable text found in document")
            points = []
            for index, chunk in enumerate(chunks):
                vector = self.gemini.embed(chunk)
                db_chunk = DocumentChunk(document_id=document.id, chunk_index=index, text=chunk, metadata_json={"source": filename, "chunk_index": index})
                db.add(db_chunk); db.flush()
                points.append(PointStruct(id=str(uuid4()), vector=vector, payload={"document_id": document.id, "chunk_id": db_chunk.id, "chunk_index": index, "document_name": filename, "text": chunk, "page_number": None}))
            self.vectors.upsert(points); document.chunk_count = len(chunks); document.status = "ready"; db.commit(); return document
        except Exception:
            document.status = "failed"; db.commit(); raise

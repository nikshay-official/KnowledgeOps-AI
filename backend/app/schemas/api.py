from datetime import datetime
from pydantic import BaseModel, Field

class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    size_bytes: int
    status: str
    chunk_count: int
    created_at: datetime
    model_config = {"from_attributes": True}

class Citation(BaseModel):
    document_id: int
    document_name: str
    chunk_id: int
    page_number: int | None = None
    score: float
    snippet: str

class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    conversation_id: str
    retrieved_count: int

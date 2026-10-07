from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.db.database import Base, engine
from app.db import models  # noqa: F401
from app.rag.vector_store import VectorStore
from app.services.gemini import GeminiService

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.vector_store = VectorStore()
    app.state.gemini = GeminiService()
    try:
        yield
    finally:
        app.state.vector_store.close()

app = FastAPI(title="KnowledgeOps AI", version="1.0.0", description="Production-style grounded company knowledge assistant", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

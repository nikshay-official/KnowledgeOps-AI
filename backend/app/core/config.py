from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-2"
    embedding_dimensions: int = 768
    database_url: str = f"sqlite:///{(ROOT / 'data' / 'knowledgeops.db').as_posix()}"
    qdrant_path: str = str(ROOT / 'data' / 'qdrant')
    qdrant_collection: str = "knowledge_chunks"
    frontend_origin: str = "http://localhost:5173"
    top_k: int = 8
    max_context_chars: int = 24000
    max_upload_mb: int = 20
    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

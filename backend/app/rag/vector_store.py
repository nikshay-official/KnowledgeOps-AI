from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from app.core.config import get_settings

class VectorStore:
    """Application-lifetime wrapper around one persistent Qdrant client."""
    def __init__(self):
        settings = get_settings(); Path(settings.qdrant_path).mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=settings.qdrant_path); self.collection = settings.qdrant_collection
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(collection_name=self.collection, vectors_config=VectorParams(size=settings.embedding_dimensions, distance=Distance.COSINE))
    def upsert(self, points: list[PointStruct]):
        if points: self.client.upsert(collection_name=self.collection, points=points, wait=True)
    def search(self, vector: list[float], limit: int = 12):
        return self.client.query_points(collection_name=self.collection, query=vector, limit=limit, with_payload=True).points
    def delete_document(self, document_id: int):
        from qdrant_client.models import FieldCondition, Filter, MatchValue
        self.client.delete(collection_name=self.collection, points_selector=Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]), wait=True)
    def close(self): self.client.close()

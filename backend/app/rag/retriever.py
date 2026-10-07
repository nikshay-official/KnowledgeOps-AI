import re
from app.core.config import get_settings
from app.rag.vector_store import VectorStore
from app.services.gemini import GeminiService

class HybridRetriever:
    def __init__(self, vector_store: VectorStore, gemini: GeminiService):
        self.settings = get_settings(); self.vectors = vector_store; self.gemini = gemini
    @staticmethod
    def lexical_score(query: str, text: str) -> float:
        q = set(re.findall(r"[a-z0-9]+", query.lower())); words = re.findall(r"[a-z0-9]+", text.lower())
        if not q or not words: return 0.0
        return min(1.0, sum(1 for w in words if w in q) / max(1, len(q)))
    def retrieve(self, question: str, limit: int | None = None):
        limit = limit or self.settings.top_k
        query_vector = self.gemini.embed(question)
        points = self.vectors.search(query_vector, limit=max(limit * 2, 12))
        scored = []
        for point in points:
            payload = point.payload or {}; lexical = self.lexical_score(question, payload.get("text", "")); semantic = float(point.score)
            scored.append({"score": 0.75 * semantic + 0.25 * lexical, "semantic_score": semantic, "lexical_score": lexical, **payload})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

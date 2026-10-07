from google import genai
from google.genai import types
from app.core.config import get_settings

class GeminiService:
    def __init__(self):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env")
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key)
    def embed(self, text: str) -> list[float]:
        result = self.client.models.embed_content(model=self.settings.embedding_model, contents=text, config=types.EmbedContentConfig(output_dimensionality=self.settings.embedding_dimensions))
        return list(result.embeddings[0].values)
    def generate(self, question: str, context: str) -> str:
        system = ("You are KnowledgeOps, a company knowledge assistant. Answer only from the supplied knowledge context. "
                   "If the context does not contain enough evidence, say you could not find that information in the knowledge base. "
                   "Never invent company policies, dates, names, procedures, or numbers. Keep answers concise and cite claims using [Source N] markers.")
        prompt = f"Knowledge context:\n{context}\n\nUser question:\n{question}"
        response = self.client.models.generate_content(model=self.settings.gemini_model, contents=prompt, config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=1200))
        return response.text or "I could not generate an answer from the available knowledge."

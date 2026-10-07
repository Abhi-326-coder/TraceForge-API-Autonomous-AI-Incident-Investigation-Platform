from google import genai
from google.genai import types

from app.config import settings


class GeminiEmbeddingService:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = "gemini-embedding-001"

    def embed(
        self,
        text: str,
    ) -> list[float]:

        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=768,
            ),
        )

        return result.embeddings[0].values
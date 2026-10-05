from google import genai

from app.config import settings


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = settings.gemini_model
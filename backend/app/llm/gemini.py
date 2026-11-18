from google import genai
from google.genai import types

from app.config import settings


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
            # Celery owns retries for investigation tasks. One SDK attempt
            # prevents multiplying provider retries across task attempts.
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1)
            ),
        )

        self.model = settings.gemini_model

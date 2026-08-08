from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            name="groq",
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            model=settings.groq_model,
            timeout=settings.request_timeout_seconds,
        )

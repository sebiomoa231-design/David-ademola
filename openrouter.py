from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            name="openrouter",
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model=settings.openrouter_model,
            timeout=settings.request_timeout_seconds,
            headers={"X-Title": "David AI"},
        )

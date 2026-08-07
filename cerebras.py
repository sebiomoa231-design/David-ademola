from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class CerebrasProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            name="cerebras",
            api_key=settings.cerebras_api_key,
            base_url="https://api.cerebras.ai/v1",
            model=settings.cerebras_model,
            timeout=settings.request_timeout_seconds,
        )

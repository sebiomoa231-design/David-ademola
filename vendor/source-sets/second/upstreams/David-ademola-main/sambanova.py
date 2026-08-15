from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class SambaNovaProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            name="sambanova",
            api_key=settings.sambanova_api_key,
            base_url="https://api.sambanova.ai/v1",
            model=settings.sambanova_model,
            timeout=settings.request_timeout_seconds,
        )

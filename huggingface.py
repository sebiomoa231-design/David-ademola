from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class HuggingFaceProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            name="huggingface",
            api_key=settings.huggingface_api_key,
            base_url="https://router.huggingface.co/v1",
            model=settings.huggingface_model,
            timeout=settings.request_timeout_seconds,
        )

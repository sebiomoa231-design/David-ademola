from __future__ import annotations

from app.core.config import Settings
from app.providers.base import BaseProvider, ProviderResult


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, message: str) -> ProviderResult:
        if not self.settings.gemini_api_key:
            return ProviderResult(provider=self.name, text="Gemini API key not configured.")
        return ProviderResult(provider=self.name, text=f"Gemini processed: {message}")

from __future__ import annotations

from app.core.config import Settings
from app.core.logging import log_provider_selection
from app.providers.base import ProviderResult
from app.providers.cerebras import CerebrasProvider
from app.providers.cloudflare import CloudflareProvider
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.providers.huggingface import HuggingFaceProvider
from app.providers.openrouter import OpenRouterProvider
from app.providers.sambanova import SambaNovaProvider


class AIRouter:
    """Routes chat requests to the highest-priority provider with a configured key."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.providers = {
            "gemini": GeminiProvider(settings),
            "groq": GroqProvider(),
            "openrouter": OpenRouterProvider(),
            "cloudflare": CloudflareProvider(),
            "cerebras": CerebrasProvider(),
            "sambanova": SambaNovaProvider(),
            "huggingface": HuggingFaceProvider(),
        }
        self.key_map = {
            "gemini": settings.gemini_api_key,
            "groq": settings.groq_api_key,
            "openrouter": settings.openrouter_api_key,
            "cloudflare": settings.cloudflare_api_key,
            "cerebras": settings.cerebras_api_key,
            "sambanova": settings.sambanova_api_key,
            "huggingface": settings.huggingface_api_key,
        }

    async def generate(self, message: str) -> ProviderResult:
        for provider_name in self.settings.provider_priority_list:
            if self.key_map.get(provider_name):
                log_provider_selection(provider_name)
                return await self.providers[provider_name].generate(message)

        log_provider_selection("fallback")
        return ProviderResult(
            provider="fallback",
            text=f"David AI is ready. You said: {message}",
        )

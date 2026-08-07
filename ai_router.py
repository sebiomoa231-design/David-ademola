from __future__ import annotations

from app.core.config import Settings
from app.core.logging import log_error, log_provider_selection
from app.providers.base import ProviderError, ProviderResult
from app.providers.cerebras import CerebrasProvider
from app.providers.cloudflare import CloudflareProvider
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.providers.huggingface import HuggingFaceProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.openrouter import OpenRouterProvider
from app.providers.sambanova import SambaNovaProvider


class AIRouter:
    """Routes requests through configured providers with automatic failover."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.providers = {
            "openai": OpenAICompatibleProvider(
                name="openai",
                api_key=settings.openai_api_key,
                base_url="https://api.openai.com/v1",
                model=settings.openai_model,
                timeout=settings.request_timeout_seconds,
            ),
            "gemini": GeminiProvider(settings),
            "groq": GroqProvider(settings),
            "openrouter": OpenRouterProvider(settings),
            "cloudflare": CloudflareProvider(settings),
            "cerebras": CerebrasProvider(settings),
            "sambanova": SambaNovaProvider(settings),
            "huggingface": HuggingFaceProvider(settings),
        }

    async def generate(self, message: str) -> ProviderResult:
        failures: list[str] = []

        for provider_name in self.settings.provider_priority_list:
            provider = self.providers.get(provider_name)
            if provider is None:
                failures.append(f"{provider_name}: unsupported provider")
                continue

            try:
                result = await provider.generate(message)
                log_provider_selection(result.provider)
                return result
            except ProviderError as exc:
                failures.append(f"{provider_name}: {exc}")
                log_error(f"provider:{provider_name}", exc)
            except Exception as exc:  # defensive isolation of upstream failures
                failures.append(f"{provider_name}: {exc}")
                log_error(f"provider:{provider_name}", exc)

        log_provider_selection("fallback")
        detail = "; ".join(failures[-3:])
        return ProviderResult(
            provider="fallback",
            text=(
                "David AI is online, but no configured AI provider completed "
                "this request. "
                + (f"Provider details: {detail}" if detail else "Add an API key in your environment.")
            ),
        )

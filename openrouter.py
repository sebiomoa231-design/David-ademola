from app.providers.base import BaseProvider, ProviderResult


class OpenRouterProvider(BaseProvider):
    name = "openrouter"

    async def generate(self, message: str) -> ProviderResult:
        return ProviderResult(provider=self.name, text=f"OpenRouter processed: {message}")

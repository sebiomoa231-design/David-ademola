from app.providers.base import BaseProvider, ProviderResult


class GroqProvider(BaseProvider):
    name = "groq"

    async def generate(self, message: str) -> ProviderResult:
        return ProviderResult(provider=self.name, text=f"Groq processed: {message}")

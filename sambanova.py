from app.providers.base import BaseProvider, ProviderResult


class SambaNovaProvider(BaseProvider):
    name = "sambanova"

    async def generate(self, message: str) -> ProviderResult:
        return ProviderResult(provider=self.name, text=f"SambaNova processed: {message}")

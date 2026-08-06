from app.providers.base import BaseProvider, ProviderResult


class CerebrasProvider(BaseProvider):
    name = "cerebras"

    async def generate(self, message: str) -> ProviderResult:
        return ProviderResult(provider=self.name, text=f"Cerebras processed: {message}")

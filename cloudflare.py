from app.providers.base import BaseProvider, ProviderResult


class CloudflareProvider(BaseProvider):
    name = "cloudflare"

    async def generate(self, message: str) -> ProviderResult:
        return ProviderResult(provider=self.name, text=f"Cloudflare AI processed: {message}")

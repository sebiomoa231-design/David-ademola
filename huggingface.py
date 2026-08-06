from app.providers.base import BaseProvider, ProviderResult


class HuggingFaceProvider(BaseProvider):
    name = "huggingface"

    async def generate(self, message: str) -> ProviderResult:
        return ProviderResult(provider=self.name, text=f"Hugging Face processed: {message}")

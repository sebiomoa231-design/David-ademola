from __future__ import annotations

import httpx

from app.providers.base import BaseProvider, ProviderError, ProviderResult


class OpenAICompatibleProvider(BaseProvider):
    """Adapter for providers exposing OpenAI-compatible chat completions."""

    def __init__(
        self,
        *,
        name: str,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 45,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.extra_headers = headers or {}

    async def generate(self, message: str) -> ProviderResult:
        if not self.api_key:
            raise ProviderError(f"{self.name} API key is not configured.")

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"{self.name} request failed: {exc}") from exc

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                f"{self.name} returned an unexpected response."
            ) from exc

        if not isinstance(text, str) or not text.strip():
            raise ProviderError(f"{self.name} returned an empty response.")

        return ProviderResult(provider=self.name, text=text.strip())

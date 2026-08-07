from __future__ import annotations

import httpx

from app.core.config import Settings
from app.providers.base import BaseProvider, ProviderError, ProviderResult


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, settings: Settings):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.timeout = settings.request_timeout_seconds

    async def generate(self, message: str) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("Gemini API key is not configured.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent"
        )
        payload = {
            "contents": [{"parts": [{"text": message}]}],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers={
                        "x-goog-api-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc

        try:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(
                part.get("text", "") for part in parts if isinstance(part, dict)
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Gemini returned an unexpected response.") from exc

        if not text.strip():
            raise ProviderError("Gemini returned an empty response.")

        return ProviderResult(provider=self.name, text=text.strip())

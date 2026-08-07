from __future__ import annotations

import httpx

from app.core.config import Settings
from app.providers.base import BaseProvider, ProviderError, ProviderResult


class CloudflareProvider(BaseProvider):
    name = "cloudflare"

    def __init__(self, settings: Settings):
        self.api_key = settings.cloudflare_api_key
        self.account_id = settings.cloudflare_account_id
        self.model = settings.cloudflare_model
        self.timeout = settings.request_timeout_seconds

    async def generate(self, message: str) -> ProviderResult:
        if not self.api_key or not self.account_id:
            raise ProviderError(
                "Cloudflare API token or account ID is not configured."
            )

        url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )
        payload = {"messages": [{"role": "user", "content": message}]}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"Cloudflare request failed: {exc}") from exc

        result = data.get("result") if isinstance(data, dict) else None
        text = result.get("response") if isinstance(result, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise ProviderError("Cloudflare returned an empty or unexpected response.")

        return ProviderResult(provider=self.name, text=text.strip())

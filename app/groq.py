from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


class GroqProvider:
    """Groq API provider."""

    name = "groq"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        api_key = self.settings.groq_api_key

        if not api_key:
            raise RuntimeError("Groq API key is not configured.")

        selected_model = model or self.settings.groq_model

        url = "https://api.groq.com/openai/v1/chat/completions"

        payload: dict[str, Any] = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        timeout = self.settings.request_timeout_seconds

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            raise RuntimeError(
                f"Groq API error {response.status_code}: "
                f"{response.text[:500]}"
            )

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Groq returned an unexpected response."
            ) from exc


groq_provider = GroqProvider()

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


class GeminiProvider:
    """Google Gemini API provider."""

    name = "gemini"

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
        api_key = self.settings.gemini_api_key

        if not api_key:
            raise RuntimeError("Gemini API key is not configured.")

        selected_model = model or self.settings.gemini_model

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{selected_model}:generateContent"
        )

        contents: list[dict[str, Any]] = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "assistant":
                gemini_role = "model"
            else:
                gemini_role = "user"

            contents.append(
                {
                    "role": gemini_role,
                    "parts": [{"text": content}],
                }
            )

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
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
                f"Gemini API error {response.status_code}: "
                f"{response.text[:500]}"
            )

        data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Gemini returned an unexpected response."
            ) from exc


gemini_provider = GeminiProvider()

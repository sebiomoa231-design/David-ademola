"""Optional ElevenLabs capabilities adapted from the official Python SDK.

The existing David voice provider remains responsible for the stable TTS/STT
contracts. This module adds bounded, server-side capabilities from the official
ElevenLabs SDK without exposing the API key or importing the standalone MCP
server into the FastAPI process.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any


class ElevenLabsFeatureError(RuntimeError):
    """Raised when an optional ElevenLabs capability cannot be used."""


class ElevenLabsFeatureClient:
    """Small async adapter around the official ElevenLabs Python SDK."""

    def __init__(self, *, api_key: str = "", base_url: str | None = None) -> None:
        self.api_key = api_key.strip()
        self._client: Any | None = None
        self.import_error: str | None = None
        if not self.api_key:
            return
        try:
            from elevenlabs.client import AsyncElevenLabs
        except ImportError as exc:  # pragma: no cover - depends on deployment extras
            self.import_error = str(exc)
            return
        sdk_base_url = (base_url or "").rstrip("/")
        if sdk_base_url.endswith("/v1"):
            sdk_base_url = sdk_base_url[:-3]
        self._client = AsyncElevenLabs(
            api_key=self.api_key,
            base_url=sdk_base_url or None,
            timeout=60,
        )

    @property
    def configured(self) -> bool:
        return self._client is not None

    def _require_client(self) -> Any:
        if self._client is None:
            if self.import_error:
                raise ElevenLabsFeatureError("The ElevenLabs SDK is not installed")
            raise ElevenLabsFeatureError("ElevenLabs API key is not configured")
        return self._client

    @staticmethod
    def _serialize(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, dict):
            return {str(key): ElevenLabsFeatureClient._serialize(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [ElevenLabsFeatureClient._serialize(item) for item in value]
        if hasattr(value, "model_dump"):
            return ElevenLabsFeatureClient._serialize(value.model_dump(mode="json"))
        if hasattr(value, "dict"):
            return ElevenLabsFeatureClient._serialize(value.dict())
        return str(value)

    @staticmethod
    async def _collect(stream: AsyncIterator[bytes]) -> bytes:
        chunks: list[bytes] = []
        async for chunk in stream:
            if isinstance(chunk, bytes):
                chunks.append(chunk)
        return b"".join(chunks)

    async def search_voices(self, *, search: str | None = None, page_size: int = 20) -> dict[str, Any]:
        client = self._require_client()
        response = await client.voices.search(
            search=search or None,
            page_size=max(1, min(page_size, 100)),
        )
        return {
            "voices": self._serialize(getattr(response, "voices", [])),
            "has_more": bool(getattr(response, "has_more", False)),
            "next_page_token": getattr(response, "next_page_token", None),
            "total_count": getattr(response, "total_count", None),
        }

    async def text_to_sound_effects(
        self,
        *,
        text: str,
        duration_seconds: float | None = None,
        prompt_influence: float | None = None,
        output_format: str = "mp3_44100_128",
    ) -> bytes:
        client = self._require_client()
        stream = client.text_to_sound_effects.convert(
            text=text,
            output_format=output_format,
            duration_seconds=duration_seconds,
            prompt_influence=prompt_influence,
        )
        return await self._collect(stream)

    async def speech_to_speech(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_sts_v2",
        output_format: str = "mp3_44100_128",
        remove_background_noise: bool = False,
    ) -> bytes:
        client = self._require_client()
        stream = client.speech_to_speech.convert(
            voice_id=voice_id,
            audio=(filename, audio_bytes, content_type),
            model_id=model_id,
            output_format=output_format,
            remove_background_noise=remove_background_noise,
        )
        return await self._collect(stream)

    async def transcribe_advanced(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        model_id: str = "scribe_v2",
        language_code: str | None = None,
        tag_audio_events: bool = True,
        diarize: bool = False,
        timestamps_granularity: str | None = None,
        keyterms: list[str] | None = None,
    ) -> dict[str, Any]:
        client = self._require_client()
        result = await client.speech_to_text.convert(
            file=(filename, audio_bytes, content_type),
            model_id=model_id,
            language_code=language_code or None,
            tag_audio_events=tag_audio_events,
            diarize=diarize,
            timestamps_granularity=timestamps_granularity or None,
            keyterms=keyterms or None,
        )
        return self._serialize(result)

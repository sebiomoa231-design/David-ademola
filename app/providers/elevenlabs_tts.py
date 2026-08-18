"""ElevenLabs TTS Provider for David Ademola AI.

This module provides text-to-speech synthesis using ElevenLabs API
with the configured David voice identity.

Replaces the previous Piper TTS (Ryan voice) implementation.
"""
from __future__ import annotations

import base64
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Configuration defaults
ELEVENLABS_API_BASE = os.getenv("ELEVENLABS_API_BASE_URL", "https://api.elevenlabs.io/v1")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pywu1SUjrxSM1ddFHhM7")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")


class ElevenLabsError(Exception):
    """Raised when ElevenLabs API returns an error."""
    pass


class ElevenLabsTTSClient:
    """Client for ElevenLabs Text-to-Speech API.

    Uses the British JARVIS-style deep male voice configured for David AI.
    Supports English and Yoruba via the multilingual v2 model.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.voice_id = voice_id or ELEVENLABS_VOICE_ID
        self.model_id = model_id or ELEVENLABS_MODEL
        self.base_url = (base_url or ELEVENLABS_API_BASE).rstrip("/")

    def is_configured(self) -> bool:
        """Check if the client has the required API key and voice ID."""
        return bool(self.api_key and self.voice_id)

    async def synthesize(
        self,
        text: str,
        output_format: str = "mp3_44100_128",
        voice_settings: Optional[dict] = None,
    ) -> bytes:
        """Synthesize text to speech using ElevenLabs API.

        Args:
            text: The text to convert to speech.
            output_format: Audio output format (default: mp3_44100_128).
            voice_settings: Optional voice settings override.

        Returns:
            Audio bytes in the specified format.

        Raises:
            ElevenLabsError: If the API call fails.
        """
        if not self.is_configured():
            raise ElevenLabsError("ElevenLabs API key or voice ID not configured.")

        url = f"{self.base_url}/text-to-speech/{self.voice_id}"

        # Default voice settings for JARVIS-style: stable, clear, deep
        default_settings = {
            "stability": 0.75,
            "similarity_boost": 0.80,
            "style": 0.35,
            "use_speaker_boost": True,
        }

        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": voice_settings or default_settings,
        }

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        params = {"output_format": output_format}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url, json=payload, headers=headers, params=params
                )
                response.raise_for_status()
                return response.content
            except httpx.HTTPStatusError as exc:
                error_detail = exc.response.text if exc.response else str(exc)
                logger.error(f"ElevenLabs API error: {exc.response.status_code} - {error_detail}")
                raise ElevenLabsError(
                    f"ElevenLabs API returned {exc.response.status_code}: {error_detail}"
                ) from exc
            except httpx.RequestError as exc:
                logger.error(f"ElevenLabs request failed: {exc}")
                raise ElevenLabsError(f"Request to ElevenLabs failed: {exc}") from exc

    async def get_voice_info(self) -> dict:
        """Retrieve information about the configured voice."""
        if not self.is_configured():
            raise ElevenLabsError("ElevenLabs API key not configured.")

        url = f"{self.base_url}/voices/{self.voice_id}"
        headers = {"xi-api-key": self.api_key}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def list_voices(self) -> list[dict]:
        """List all available voices."""
        if not self.api_key:
            raise ElevenLabsError("ElevenLabs API key not configured.")

        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("voices", [])


class ElevenLabsSTTClient:
    """Client for ElevenLabs Speech-to-Text (Scribe) API.

    Supports transcription of audio files with language detection.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.model_id = model_id or os.getenv("ELEVENLABS_STT_MODEL", "scribe_v1")
        self.base_url = (base_url or ELEVENLABS_API_BASE).rstrip("/")

    def is_configured(self) -> bool:
        """Check if the client has the required API key."""
        return bool(self.api_key)

    async def transcribe(
        self,
        audio_bytes: bytes,
        language_code: Optional[str] = None,
        filename: str = "audio.wav",
    ) -> dict:
        """Transcribe audio using ElevenLabs Scribe API.

        Args:
            audio_bytes: Raw audio bytes to transcribe.
            language_code: Optional ISO language code (e.g., 'en', 'yo' for Yoruba).
            filename: Name of the audio file for content-type detection.

        Returns:
            Dictionary with transcription results including text and language.

        Raises:
            ElevenLabsError: If the API call fails.
        """
        if not self.is_configured():
            raise ElevenLabsError("ElevenLabs API key not configured.")

        url = f"{self.base_url}/speech-to-text"

        headers = {"xi-api-key": self.api_key}

        # Determine content type from filename
        content_type = "audio/wav"
        if filename.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif filename.endswith(".webm"):
            content_type = "audio/webm"
        elif filename.endswith(".ogg"):
            content_type = "audio/ogg"

        files = {"file": (filename, audio_bytes, content_type)}
        data = {"model_id": self.model_id}
        if language_code:
            data["language_code"] = language_code

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    url, headers=headers, files=files, data=data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                error_detail = exc.response.text if exc.response else str(exc)
                logger.error(f"ElevenLabs STT error: {exc.response.status_code} - {error_detail}")
                raise ElevenLabsError(
                    f"ElevenLabs STT returned {exc.response.status_code}: {error_detail}"
                ) from exc
            except httpx.RequestError as exc:
                logger.error(f"ElevenLabs STT request failed: {exc}")
                raise ElevenLabsError(f"STT request failed: {exc}") from exc

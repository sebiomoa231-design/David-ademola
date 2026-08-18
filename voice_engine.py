"""David Ademola AI — Voice Engine.

Unified voice engine providing TTS (ElevenLabs) and STT capabilities.
Uses the British JARVIS-style deep male voice (Voice ID: 5hZv9mAOcmcMt1TxA5Iz).

This replaces the previous Piper TTS (Ryan voice) implementation.
ElevenLabs multilingual v2 model supports both English and Yoruba natively.
"""
from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"


class LanguageMode(str, Enum):
    AUTO = "auto"
    ENGLISH = "english"
    YORUBA = "yoruba"


@dataclass
class TranscriptionResult:
    text: str
    language: str
    provider: str
    confidence: float | None = None


@dataclass
class SpeechResult:
    audio_available: bool
    provider: str
    text_fallback: str
    reason: str | None = None
    audio_base64: str | None = None
    audio_format: str = "mp3"


class VoiceEngine:
    """Speech interface for David AI.

    Text-to-speech runs through ElevenLabs using the British JARVIS-style
    deep male voice (Voice ID: 5hZv9mAOcmcMt1TxA5Iz) with the multilingual
    v2 model. This supports both English and Yoruba natively.

    Speech-to-text uses ElevenLabs Scribe (scribe_v1) for transcription
    with automatic language detection.

    Language handling: AUTO is the default. English and Yoruba are the two
    supported language modes. The multilingual v2 model handles both languages
    natively without switching voices.
    """

    SUPPORTED_LANGUAGES = ("english", "yoruba")

    def __init__(
        self,
        elevenlabs_tts=None,
        elevenlabs_stt=None,
        stt_provider: str | None = None,
    ) -> None:
        self.stt_provider = stt_provider or "elevenlabs"
        self._elevenlabs_tts = elevenlabs_tts
        self._elevenlabs_stt = elevenlabs_stt

        # Lazy-initialize ElevenLabs clients if not provided
        if self._elevenlabs_tts is None:
            try:
                from app.providers.elevenlabs_tts import ElevenLabsTTSClient
                self._elevenlabs_tts = ElevenLabsTTSClient()
            except ImportError:
                logger.warning("ElevenLabs TTS client not available")

        if self._elevenlabs_stt is None:
            try:
                from app.providers.elevenlabs_tts import ElevenLabsSTTClient
                self._elevenlabs_stt = ElevenLabsSTTClient()
            except ImportError:
                logger.warning("ElevenLabs STT client not available")

    @property
    def tts_provider(self) -> str | None:
        """Return the active TTS provider name."""
        if self._elevenlabs_tts and self._elevenlabs_tts.is_configured():
            return "elevenlabs"
        return None

    def detect_language(self, text: str) -> str:
        """Detect whether text is English or Yoruba.

        Uses a simple heuristic; a production implementation would use
        a language-ID model. Defaults to English when uncertain.
        """
        yoruba_markers = ("ọ", "ẹ", "ṣ", "ń", "bawo", "pele", "e se", "ẹ kaabo", "o dabo")
        lowered = text.lower()
        if any(marker in lowered for marker in yoruba_markers):
            return "yoruba"
        return "english"

    async def transcribe(
        self,
        audio_bytes: bytes,
        language_mode: LanguageMode = LanguageMode.AUTO,
    ) -> TranscriptionResult:
        """Transcribe audio to text using ElevenLabs Scribe.

        Args:
            audio_bytes: Raw audio data.
            language_mode: Language hint for transcription.

        Returns:
            TranscriptionResult with the transcribed text.
        """
        if not self._elevenlabs_stt or not self._elevenlabs_stt.is_configured():
            return TranscriptionResult(
                text="",
                language=language_mode.value,
                provider="none",
                confidence=None,
            )

        # Map language mode to ISO code for ElevenLabs
        language_code = None
        if language_mode == LanguageMode.ENGLISH:
            language_code = "en"
        elif language_mode == LanguageMode.YORUBA:
            language_code = "yo"

        try:
            result = await self._elevenlabs_stt.transcribe(
                audio_bytes=audio_bytes,
                language_code=language_code,
            )
            return TranscriptionResult(
                text=result.get("text", ""),
                language=result.get("language_code", language_mode.value),
                provider="elevenlabs",
                confidence=result.get("confidence"),
            )
        except Exception as exc:
            logger.error(f"ElevenLabs STT failed: {exc}")
            return TranscriptionResult(
                text="",
                language=language_mode.value,
                provider="elevenlabs",
                confidence=None,
            )

    async def synthesize(
        self,
        text: str,
        language_mode: LanguageMode = LanguageMode.AUTO,
    ) -> SpeechResult:
        """Synthesize text to speech using ElevenLabs.

        The multilingual v2 model supports both English and Yoruba natively,
        so no language-based rejection is needed (unlike the old Piper engine).

        Args:
            text: Text to convert to speech.
            language_mode: Language mode for synthesis.

        Returns:
            SpeechResult with audio data or fallback text.
        """
        language = (
            language_mode.value
            if language_mode != LanguageMode.AUTO
            else self.detect_language(text)
        )

        if not self._elevenlabs_tts or not self._elevenlabs_tts.is_configured():
            return SpeechResult(
                audio_available=False,
                provider="none",
                text_fallback=text,
                reason="ElevenLabs voice not configured (set ELEVENLABS_API_KEY in environment).",
            )

        try:
            audio_bytes = await self._elevenlabs_tts.synthesize(text)
        except Exception as exc:
            logger.error(f"ElevenLabs synthesis failed: {exc}")
            return SpeechResult(
                audio_available=False,
                provider="elevenlabs",
                text_fallback=text,
                reason=f"ElevenLabs synthesis failed: {exc}",
            )

        return SpeechResult(
            audio_available=True,
            provider="elevenlabs",
            text_fallback=text,
            audio_base64=base64.b64encode(audio_bytes).decode("ascii"),
            audio_format="mp3",
        )

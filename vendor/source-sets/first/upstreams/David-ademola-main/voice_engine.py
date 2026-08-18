from __future__ import annotations

import base64
from dataclasses import dataclass
from enum import Enum

from app.providers.piper_tts import PiperError, PiperTTSClient


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
    audio_format: str = "wav"


class VoiceEngine:
    """
    Speech interface for David AI.

    Text-to-speech runs through Piper (https://github.com/rhasspy/piper),
    a local/offline TTS engine -- no API key, no network call, using the
    "Ryan (high)" voice model. Speech-to-text has no provider wired in yet;
    calling transcribe() returns an honest "not configured" result rather
    than fabricating text.

    Language handling: AUTO is the default. English and Yoruba are the two
    supported language modes. Piper's English voice models do not speak
    Yoruba -- if Yoruba output is requested, synthesize() reports that
    plainly and returns the text_fallback instead of pretending to have
    generated Yoruba audio, per the "never fake unsupported capabilities"
    requirement.
    """

    SUPPORTED_LANGUAGES = ("english", "yoruba")

    def __init__(self, stt_provider: str | None = None, piper: PiperTTSClient | None = None) -> None:
        self.stt_provider = stt_provider
        self.piper = piper

    @property
    def tts_provider(self) -> str | None:
        return "piper" if self.piper and self.piper.is_configured() else None

    def detect_language(self, text: str) -> str:
        """Very small heuristic placeholder; a real implementation would use
        a language-ID model. Defaults to English when uncertain."""
        yoruba_markers = ("ọ", "ẹ", "ṣ", "bawo", "pele", "e se")
        lowered = text.lower()
        if any(marker in lowered for marker in yoruba_markers):
            return "yoruba"
        return "english"

    async def transcribe(self, audio_bytes: bytes, language_mode: LanguageMode = LanguageMode.AUTO) -> TranscriptionResult:
        if not self.stt_provider:
            return TranscriptionResult(
                text="",
                language=language_mode.value,
                provider="none",
                confidence=None,
            )
        # Real STT call would happen here once a provider is configured.
        return TranscriptionResult(text="", language=language_mode.value, provider=self.stt_provider)

    async def synthesize(self, text: str, language_mode: LanguageMode = LanguageMode.AUTO) -> SpeechResult:
        language = language_mode.value if language_mode != LanguageMode.AUTO else self.detect_language(text)

        if not self.piper or not self.piper.is_configured():
            return SpeechResult(
                audio_available=False,
                provider="none",
                text_fallback=text,
                reason="Piper voice model isn't configured yet (set PIPER_VOICE_MODEL in .env).",
            )

        if language == "yoruba":
            # The Ryan (high) Piper voice is an English model. Being explicit
            # here instead of silently generating mispronounced audio.
            return SpeechResult(
                audio_available=False,
                provider="piper",
                text_fallback=text,
                reason="The configured Piper voice (Ryan, English) doesn't support Yoruba output; continuing in Yoruba text.",
            )

        try:
            audio_bytes = await self.piper.synthesize(text)
        except PiperError as exc:
            return SpeechResult(
                audio_available=False,
                provider="piper",
                text_fallback=text,
                reason=f"Piper synthesis failed: {exc}",
            )

        return SpeechResult(
            audio_available=True,
            provider="piper",
            text_fallback=text,
            audio_base64=base64.b64encode(audio_bytes).decode("ascii"),
            audio_format="wav",
        )

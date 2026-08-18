"""Additional server-side ElevenLabs capabilities for David AI."""
from __future__ import annotations

import base64
import binascii
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.providers.elevenlabs_features import ElevenLabsFeatureClient, ElevenLabsFeatureError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])

_settings = get_settings()
_features = ElevenLabsFeatureClient(
    api_key=_settings.elevenlabs_api_key,
    base_url=_settings.elevenlabs_api_base_url,
)


class SoundEffectRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2_000)
    duration_seconds: float | None = Field(default=None, ge=0.5, le=30.0)
    prompt_influence: float | None = Field(default=None, ge=0.0, le=1.0)
    output_format: str = Field(default="mp3_44100_128", pattern=r"^[a-z0-9_]+$")


class VoiceChangerRequest(BaseModel):
    audio_base64: str = Field(min_length=1)
    voice_id: str = Field(min_length=1, max_length=200)
    audio_format: str = Field(default="webm", max_length=100)
    model_id: str = Field(default="eleven_multilingual_sts_v2", min_length=1, max_length=100)
    output_format: str = Field(default="mp3_44100_128", pattern=r"^[a-z0-9_]+$")
    remove_background_noise: bool = False


class AdvancedTranscribeRequest(BaseModel):
    audio_base64: str = Field(min_length=1)
    audio_format: str = Field(default="webm", max_length=100)
    model_id: str = Field(default="scribe_v2", min_length=1, max_length=100)
    language: str | None = Field(default=None, max_length=20)
    tag_audio_events: bool = True
    diarize: bool = False
    timestamps_granularity: str | None = Field(default=None, pattern=r"^(word|character)$")
    keyterms: list[str] = Field(default_factory=list, max_length=100)


def _decode_audio(value: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data") from exc


def _audio_metadata(audio_format: str) -> tuple[str, str]:
    normalized = audio_format.lower().strip()
    if normalized.startswith("audio/"):
        normalized = normalized[6:]
    normalized = normalized.split(";", 1)[0]
    content_types = {
        "webm": "audio/webm",
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "m4a": "audio/mp4",
        "mp4": "audio/mp4",
        "flac": "audio/flac",
        "aac": "audio/aac",
        "aiff": "audio/aiff",
        "opus": "audio/opus",
    }
    if normalized not in content_types:
        normalized = "webm"
    return f"audio.{normalized}", content_types[normalized]


def _raise_feature_error(exc: Exception) -> None:
    if isinstance(exc, ElevenLabsFeatureError):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    logger.exception("ElevenLabs optional capability failed")
    raise HTTPException(status_code=502, detail="ElevenLabs capability request failed") from exc


@router.get("/capabilities")
def voice_capabilities() -> dict[str, Any]:
    """Report optional ElevenLabs features without exposing credentials."""
    return {
        "provider": "elevenlabs",
        "sdk_configured": _features.configured,
        "capabilities": [
            "voice_search",
            "text_to_sound_effects",
            "speech_to_speech",
            "advanced_speech_to_text",
        ],
    }


@router.get("/voices")
async def search_voices(
    search: str | None = Query(default=None, max_length=200),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    try:
        return await _features.search_voices(search=search, page_size=page_size)
    except Exception as exc:
        _raise_feature_error(exc)


@router.post("/sound-effects")
async def create_sound_effect(request: SoundEffectRequest) -> dict[str, Any]:
    try:
        audio = await _features.text_to_sound_effects(
            text=request.text,
            duration_seconds=request.duration_seconds,
            prompt_influence=request.prompt_influence,
            output_format=request.output_format,
        )
    except Exception as exc:
        _raise_feature_error(exc)
    return {
        "audio_base64": base64.b64encode(audio).decode("ascii"),
        "audio_format": request.output_format.split("_", 1)[0],
        "provider": "elevenlabs",
    }


@router.post("/voice-changer")
async def change_voice(request: VoiceChangerRequest) -> dict[str, Any]:
    filename, content_type = _audio_metadata(request.audio_format)
    audio_bytes = _decode_audio(request.audio_base64)
    try:
        audio = await _features.speech_to_speech(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=content_type,
            voice_id=request.voice_id,
            model_id=request.model_id,
            output_format=request.output_format,
            remove_background_noise=request.remove_background_noise,
        )
    except Exception as exc:
        _raise_feature_error(exc)
    return {
        "audio_base64": base64.b64encode(audio).decode("ascii"),
        "audio_format": request.output_format.split("_", 1)[0],
        "voice_id": request.voice_id,
        "provider": "elevenlabs",
    }


@router.post("/transcribe/advanced")
async def advanced_transcribe(request: AdvancedTranscribeRequest) -> dict[str, Any]:
    filename, content_type = _audio_metadata(request.audio_format)
    audio_bytes = _decode_audio(request.audio_base64)
    try:
        result = await _features.transcribe_advanced(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=content_type,
            model_id=request.model_id,
            language_code=request.language,
            tag_audio_events=request.tag_audio_events,
            diarize=request.diarize,
            timestamps_granularity=request.timestamps_granularity,
            keyterms=request.keyterms,
        )
    except Exception as exc:
        _raise_feature_error(exc)
    return {**result, "provider": "elevenlabs"}

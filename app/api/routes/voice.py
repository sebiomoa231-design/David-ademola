"""David AI — Voice API Routes.

Provides TTS and STT endpoints for the frontend voice interface.
Uses ElevenLabs with Voice ID 5hZv9mAOcmcMt1TxA5Iz (British JARVIS-style).
"""
from __future__ import annotations

import base64
import logging
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "5hZv9mAOcmcMt1TxA5Iz")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")


class SynthesizeRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = None
    stability: float = 0.75
    similarity_boost: float = 0.80
    style: float = 0.35
    use_speaker_boost: bool = True


class TranscribeRequest(BaseModel):
    audio_base64: str
    language: Optional[str] = None


class VoiceStatusResponse(BaseModel):
    tts_provider: str
    tts_configured: bool
    stt_provider: str
    stt_configured: bool
    voice_id: str
    model: str
    voice_style: str


@router.get("/status", response_model=VoiceStatusResponse)
async def voice_status():
    """Get the current voice system status."""
    return VoiceStatusResponse(
        tts_provider="elevenlabs",
        tts_configured=bool(ELEVENLABS_API_KEY),
        stt_provider="elevenlabs_scribe",
        stt_configured=bool(ELEVENLABS_API_KEY),
        voice_id=ELEVENLABS_VOICE_ID,
        model=ELEVENLABS_MODEL,
        voice_style="British JARVIS-style deep male voice",
    )


@router.post("/synthesize")
async def synthesize_speech(request: SynthesizeRequest):
    """Convert text to speech using ElevenLabs.

    Returns audio as base64-encoded MP3 for the frontend to play.
    The frontend can also call this endpoint and receive raw audio bytes.
    """
    api_key = ELEVENLABS_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs API key not configured. Set ELEVENLABS_API_KEY in environment.",
        )

    voice_id = request.voice_id or ELEVENLABS_VOICE_ID
    model_id = request.model_id or ELEVENLABS_MODEL

    import httpx

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": request.text,
        "model_id": model_id,
        "voice_settings": {
            "stability": request.stability,
            "similarity_boost": request.similarity_boost,
            "style": request.style,
            "use_speaker_boost": request.use_speaker_boost,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            audio_bytes = response.content
    except httpx.HTTPStatusError as exc:
        logger.error(f"ElevenLabs TTS error: {exc.response.status_code}")
        raise HTTPException(
            status_code=502,
            detail=f"ElevenLabs returned error: {exc.response.status_code}",
        )
    except httpx.RequestError as exc:
        logger.error(f"ElevenLabs request failed: {exc}")
        raise HTTPException(status_code=502, detail="Failed to reach ElevenLabs API")

    # Return as base64 for easy frontend consumption
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    return {
        "audio_base64": audio_b64,
        "audio_format": "mp3",
        "voice_id": voice_id,
        "model_id": model_id,
        "text_length": len(request.text),
    }


@router.post("/synthesize/stream")
async def synthesize_speech_stream(request: SynthesizeRequest):
    """Convert text to speech and return raw audio bytes.

    Returns audio/mpeg directly for streaming playback.
    """
    api_key = ELEVENLABS_API_KEY
    if not api_key:
        raise HTTPException(status_code=503, detail="ElevenLabs not configured")

    voice_id = request.voice_id or ELEVENLABS_VOICE_ID
    model_id = request.model_id or ELEVENLABS_MODEL

    import httpx

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": request.text,
        "model_id": model_id,
        "voice_settings": {
            "stability": request.stability,
            "similarity_boost": request.similarity_boost,
            "style": request.style,
            "use_speaker_boost": request.use_speaker_boost,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline"},
            )
    except Exception as exc:
        logger.error(f"ElevenLabs stream error: {exc}")
        raise HTTPException(status_code=502, detail="Voice synthesis failed")


@router.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    """Transcribe audio using ElevenLabs Scribe.

    Accepts base64-encoded audio from the frontend microphone.
    """
    api_key = ELEVENLABS_API_KEY
    if not api_key:
        raise HTTPException(status_code=503, detail="ElevenLabs not configured")

    import httpx

    try:
        audio_bytes = base64.b64decode(request.audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data")

    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": api_key}

    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"model_id": "scribe_v1"}
    if request.language:
        data["language_code"] = request.language

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"ElevenLabs STT error: {exc.response.status_code}")
        raise HTTPException(status_code=502, detail="Transcription failed")
    except httpx.RequestError as exc:
        logger.error(f"ElevenLabs STT request failed: {exc}")
        raise HTTPException(status_code=502, detail="Failed to reach ElevenLabs")

    return {
        "text": result.get("text", ""),
        "language": result.get("language_code", "en"),
        "confidence": result.get("confidence"),
    }

import base64
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.providers.elevenlabs_tts import ElevenLabsSTTClient, ElevenLabsTTSClient
from app.services.supabase_service import SupabaseApiError, SupabasePersistence
from app.services.voice_engine import LanguageMode, VoiceEngine

router = APIRouter(prefix="/voice", tags=["voice"])

_settings = get_settings()
_elevenlabs_tts = ElevenLabsTTSClient(
    api_key=_settings.elevenlabs_api_key,
    voice_id=_settings.elevenlabs_voice_id,
    model_id=_settings.elevenlabs_model,
    base_url=_settings.elevenlabs_api_base_url,
)
_elevenlabs_stt = ElevenLabsSTTClient(
    api_key=_settings.elevenlabs_api_key,
    model_id=_settings.elevenlabs_stt_model,
    base_url=_settings.elevenlabs_api_base_url,
)
engine = VoiceEngine(
    elevenlabs_tts=_elevenlabs_tts,
    elevenlabs_stt=_elevenlabs_stt,
)


class SynthesizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    language_mode: LanguageMode = LanguageMode.AUTO
    persist: bool = False
    project_id: str | None = Field(default=None, max_length=120)


class SynthesizeResponse(BaseModel):
    audio_available: bool
    provider: str
    text_fallback: str
    reason: str | None = None
    audio_base64: str | None = None
    audio_format: str = "wav"
    audio_url: str | None = None
    asset: dict[str, object] | None = None
    persisted: bool = False


class TranscribeRequest(BaseModel):
    audio_base64: str
    language: str | None = None
    audio_format: str = "webm"
    tag_audio_events: bool = True
    diarize: bool = False
    timestamps_granularity: str | None = "word"
    keyterms: list[str] = Field(default_factory=list, max_length=100)
    num_speakers: int | None = None


@router.get("/status")
def voice_status() -> dict:
    return {
        "stt_configured": engine.stt_provider is not None,
        "tts_configured": engine.tts_provider is not None,
        "tts_engine": "elevenlabs" if engine.tts_provider else None,
        "tts_voice": "British deep male (JARVIS-style)" if engine.tts_provider else None,
        "supported_languages": list(engine.SUPPORTED_LANGUAGES),
        "default_language_mode": LanguageMode.AUTO.value,
    }


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(payload: SynthesizeRequest) -> SynthesizeResponse:
    result = await engine.synthesize(payload.text, payload.language_mode)
    response = SynthesizeResponse(**result.__dict__)
    if not payload.persist or not response.audio_available or not response.audio_base64:
        return response

    try:
        audio_bytes = base64.b64decode(response.audio_base64, validate=True)
        if not audio_bytes:
            raise ValueError("generated audio is empty")
        stored = SupabasePersistence(get_settings()).upload_asset(
            filename=f"david-voice-{uuid4().hex}.mp3",
            content=audio_bytes,
            content_type="audio/mpeg",
            project_id=payload.project_id,
            kind="audio",
            metadata={
                "generation_type": "voice_synthesis",
                "provider": response.provider,
                "language_mode": payload.language_mode.value,
                "text_length": len(payload.text),
            },
        )
        response.audio_url = str(stored.get("signed_url")) if stored.get("signed_url") else None
        response.asset = stored
        response.persisted = bool(response.audio_url)
    except (SupabaseApiError, ValueError, KeyError) as exc:
        response.reason = f"Audio generated, but persistence failed: {exc}"
    return response


@router.post("/transcribe")
async def transcribe(payload: TranscribeRequest) -> dict[str, object]:
    try:
        audio_bytes = base64.b64decode(payload.audio_base64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data") from exc
    language = (payload.language or "").lower()
    language_mode = LanguageMode.ENGLISH if language in {"en", "english"} else LanguageMode.YORUBA if language in {"yo", "yoruba"} else LanguageMode.AUTO
    extension = payload.audio_format.lower().replace("audio/", "").split(";")[0] or "webm"
    if extension not in {"webm", "wav", "mp3", "ogg", "m4a", "mp4"}:
        extension = "webm"
    result = await engine.transcribe(
        audio_bytes,
        language_mode,
        filename=f"audio.{extension}",
        tag_audio_events=payload.tag_audio_events,
        diarize=payload.diarize,
        timestamps_granularity=payload.timestamps_granularity,
        keyterms=payload.keyterms,
        num_speakers=payload.num_speakers,
    )
    if not result.text and result.provider == "none":
        raise HTTPException(status_code=503, detail="Speech-to-text provider is not configured")
    response: dict[str, object] = {
        "text": result.text,
        "language": result.language,
        "confidence": result.confidence,
        "provider": result.provider,
    }
    if isinstance(result.raw, dict):
        response.update({
            "words": result.raw.get("words", []),
            "audio_events": result.raw.get("audio_events", []),
            "language_probability": result.raw.get("language_probability"),
        })
    return response

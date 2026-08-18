import base64

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.providers.elevenlabs_tts import ElevenLabsSTTClient, ElevenLabsTTSClient
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
    text: str
    language_mode: LanguageMode = LanguageMode.AUTO


class SynthesizeResponse(BaseModel):
    audio_available: bool
    provider: str
    text_fallback: str
    reason: str | None = None
    audio_base64: str | None = None
    audio_format: str = "wav"


class TranscribeRequest(BaseModel):
    audio_base64: str
    language: str | None = None
    audio_format: str = "webm"


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
    return SynthesizeResponse(**result.__dict__)


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
    result = await engine.transcribe(audio_bytes, language_mode, filename=f"audio.{extension}")
    if not result.text and result.provider == "none":
        raise HTTPException(status_code=503, detail="Speech-to-text provider is not configured")
    return {"text": result.text, "language": result.language, "confidence": result.confidence, "provider": result.provider}

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.providers.piper_tts import PiperTTSClient
from app.services.voice_engine import LanguageMode, VoiceEngine

router = APIRouter(prefix="/voice", tags=["voice"])

_settings = get_settings()
_piper = PiperTTSClient(
    executable=_settings.piper_executable,
    voice_model_path=_settings.piper_voice_model,
)
engine = VoiceEngine(piper=_piper)


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


@router.get("/status")
def voice_status() -> dict:
    return {
        "stt_configured": engine.stt_provider is not None,
        "tts_configured": engine.tts_provider is not None,
        "tts_engine": "piper" if engine.tts_provider else None,
        "tts_voice": "Ryan (high)" if engine.tts_provider else None,
        "supported_languages": list(engine.SUPPORTED_LANGUAGES),
        "default_language_mode": LanguageMode.AUTO.value,
    }


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(payload: SynthesizeRequest) -> SynthesizeResponse:
    result = await engine.synthesize(payload.text, payload.language_mode)
    return SynthesizeResponse(**result.__dict__)

from fastapi import APIRouter
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

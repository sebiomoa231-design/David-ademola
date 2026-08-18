"""Legacy compatibility — redirects to ElevenLabs TTS provider."""
from piper_tts import PiperError, PiperTTSClient  # noqa: F401
from app.providers.elevenlabs_tts import (  # noqa: F401
    ElevenLabsTTSClient,
    ElevenLabsSTTClient,
    ElevenLabsError,
)

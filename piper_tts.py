"""Legacy Piper TTS module — DEPRECATED.

This module is retained for backward compatibility only.
David AI now uses ElevenLabs TTS with Voice ID 5hZv9mAOcmcMt1TxA5Iz
(British JARVIS-style deep male voice).

All new code should import from app.providers.elevenlabs_tts instead.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "piper_tts is deprecated. David AI now uses ElevenLabs TTS. "
    "Import from app.providers.elevenlabs_tts instead.",
    DeprecationWarning,
    stacklevel=2,
)


class PiperError(Exception):
    """Legacy exception kept for backward compatibility."""
    pass


class PiperTTSClient:
    """Legacy Piper TTS client — DEPRECATED.

    This class is a no-op stub. David AI has migrated to ElevenLabs TTS.
    Use app.providers.elevenlabs_tts.ElevenLabsTTSClient instead.
    """

    def __init__(self, *args, **kwargs) -> None:
        pass

    def is_configured(self) -> bool:
        """Always returns False — Piper is no longer the active TTS provider."""
        return False

    async def synthesize(self, text: str) -> bytes:
        raise PiperError(
            "Piper TTS has been replaced by ElevenLabs. "
            "Use app.providers.elevenlabs_tts.ElevenLabsTTSClient instead."
        )

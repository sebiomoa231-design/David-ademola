"""Realtime ElevenLabs Speech Engine integration for David AI."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.api.routes.orchestrator import OrchestratorRequest, process_with_orchestrator
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice", "speech-engine"])


class SpeechEngineBridge:
    """Lazily loads the configured official ElevenLabs Speech Engine resource."""

    def __init__(self) -> None:
        self._engine: Any | None = None
        self._client: Any | None = None

    @staticmethod
    def _sdk_base_url(value: str) -> str | None:
        base_url = (value or "").rstrip("/")
        if base_url.endswith("/v1"):
            base_url = base_url[:-3]
        return base_url or None

    async def get_engine(self) -> Any:
        settings = get_settings()
        if not settings.elevenlabs_api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not configured")
        if not settings.elevenlabs_speech_engine_id:
            raise RuntimeError("ELEVENLABS_SPEECH_ENGINE_ID is not configured")
        if self._engine is not None:
            return self._engine
        try:
            from elevenlabs.client import AsyncElevenLabs
        except ImportError as exc:  # pragma: no cover - deployment dependency guard
            raise RuntimeError("The ElevenLabs SDK is not installed") from exc
        self._client = AsyncElevenLabs(
            api_key=settings.elevenlabs_api_key,
            base_url=self._sdk_base_url(settings.elevenlabs_api_base_url),
            timeout=60,
        )
        self._engine = await self._client.speech_engine.get(settings.elevenlabs_speech_engine_id)
        return self._engine


bridge = SpeechEngineBridge()


@router.get("/speech-engine/status")
def speech_engine_status() -> dict[str, Any]:
    """Report Speech Engine readiness without exposing credentials."""
    settings = get_settings()
    return {
        "provider": "elevenlabs",
        "configured": bool(settings.elevenlabs_api_key and settings.elevenlabs_speech_engine_id),
        "engine_id": settings.elevenlabs_speech_engine_id or None,
        "public_ws_url": settings.elevenlabs_speech_engine_public_ws_url or None,
        "websocket_path": "/api/voice/speech-engine/ws",
        "authentication": "elevenlabs-speech-engine-jwt",
    }


@router.websocket("/speech-engine/ws")
async def speech_engine_websocket(websocket: WebSocket) -> None:
    """Accept authenticated ElevenLabs Speech Engine sessions."""
    try:
        engine = await bridge.get_engine()
        if not engine.verify_request(dict(websocket.headers)):
            await websocket.close(code=1008, reason="Invalid Speech Engine authorization")
            return
        await websocket.accept()
        session = engine.create_session(websocket, debug=False)

        async def on_init(conversation_id: str) -> None:
            logger.info("Speech Engine session started: %s", conversation_id)

        async def on_transcript(transcript: list[Any]) -> None:
            user_message = next(
                (message.content.strip() for message in reversed(transcript) if getattr(message, "role", "") == "user"),
                "",
            )
            if not user_message:
                return
            response = await process_with_orchestrator(
                OrchestratorRequest(
                    message=user_message,
                    context={
                        "source": "elevenlabs_speech_engine",
                        "conversation_id": session.conversation_id,
                    },
                    use_multi_agent=True,
                )
            )
            await session.send_response(response.text or "I’m ready. How can I help?")

        async def on_close() -> None:
            logger.info("Speech Engine session closed: %s", session.conversation_id)

        async def on_error(error: Exception) -> None:
            logger.warning("Speech Engine session error: %s", error)

        session.on("init", on_init)
        session.on("user_transcript", on_transcript)
        session.on("close", on_close)
        session.on("error", on_error)
        await session.run()
    except WebSocketDisconnect:
        logger.info("Speech Engine WebSocket disconnected")
    except Exception:
        logger.exception("Speech Engine WebSocket failed")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=1011, reason="Speech Engine unavailable")

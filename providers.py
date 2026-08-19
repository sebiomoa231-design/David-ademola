from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.provider_registry import (
    CapabilityRouter,
    ProviderIntegrationError,
    ProviderRegistry,
)

router = APIRouter(prefix="/providers", tags=["providers"])


class CapabilityRequest(BaseModel):
    capability: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)
    preferred_providers: list[str] = Field(default_factory=list, max_length=8)


class ReasoningRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=100_000)
    model: str | None = None
    preferred_providers: list[str] = Field(default_factory=list, max_length=8)
    max_tokens: int | None = Field(default=None, ge=1, le=32_000)


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str | None = None
    preferred_providers: list[str] = Field(default_factory=list, max_length=8)


class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)
    model: str | None = None
    size: str | None = None
    quality: str | None = None
    n: int = Field(default=1, ge=1, le=4)
    image_base64: str | None = Field(default=None, max_length=12_000_000)
    image_mime_type: str | None = Field(default=None, max_length=100)
    preferred_providers: list[str] = Field(default_factory=list, max_length=8)


def _router(settings: Settings = Depends(get_settings)) -> CapabilityRouter:
    return CapabilityRouter(settings)


def _provider_error(exc: ProviderIntegrationError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc), "retryable": exc.retryable})


@router.get("", summary="List provider readiness without exposing credentials")
def list_providers(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    return {"providers": ProviderRegistry(settings).list()}


@router.get("/capabilities", summary="List centrally routable capabilities")
def list_provider_capabilities(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    registry = ProviderRegistry(settings)
    capabilities: dict[str, list[str]] = {}
    for item in registry.list():
        for capability in item["capabilities"]:
            capabilities.setdefault(capability, []).append(item["id"])
    return {"capabilities": capabilities, "policy": {"server_side_credentials": True, "fallbacks_are_truthful": True}}


@router.post("/execute", summary="Execute a capability through the central provider router")
async def execute_capability(request: CapabilityRequest, router_service: CapabilityRouter = Depends(_router)) -> dict[str, Any]:
    try:
        return await router_service.execute(request.capability, request.payload, request.preferred_providers)
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc


@router.get("/video/operations", summary="Poll a verified Gemini video operation")
async def video_operation(name: str = Query(min_length=1, max_length=500), router_service: CapabilityRouter = Depends(_router)) -> dict[str, Any]:
    try:
        return await router_service.video_operation(name)
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc


@router.get("/video/download", summary="Download a completed verified video artifact")
async def video_download(uri: str = Query(min_length=1, max_length=2000), router_service: CapabilityRouter = Depends(_router)) -> Response:
    parsed = urlparse(uri)
    if parsed.hostname not in {"generativelanguage.googleapis.com", "generativelanguage.googleapis.com."}:
        raise HTTPException(status_code=400, detail="Video artifact URI is not a trusted Gemini download URL.")
    try:
        content, content_type = await router_service.download_video(uri)
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc
    return Response(content=content, media_type=content_type, headers={"Content-Disposition": "inline; filename=generated-video.mp4"})


@router.post("/reasoning", summary="Generate text through the configured reasoning fallback chain")
async def reasoning(request: ReasoningRequest, router_service: CapabilityRouter = Depends(_router)) -> dict[str, Any]:
    payload = {"prompt": request.prompt, "model": request.model, "max_tokens": request.max_tokens}
    try:
        return await router_service.execute("reasoning", payload, request.preferred_providers)
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc


@router.post("/embeddings", summary="Create embeddings through Voyage AI")
async def embeddings(request: EmbeddingRequest, router_service: CapabilityRouter = Depends(_router)) -> dict[str, Any]:
    payload = {"input": request.input, "model": request.model}
    try:
        return await router_service.execute("embeddings", payload, request.preferred_providers)
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc


@router.post("/images", summary="Generate images through OpenAI or Gemini")
async def images(request: ImageRequest, router_service: CapabilityRouter = Depends(_router)) -> dict[str, Any]:
    payload = request.model_dump(mode="json")
    preferred = payload.pop("preferred_providers", [])
    try:
        return await router_service.execute("image", payload, preferred)
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc


@router.post("/tts", summary="Generate speech without returning provider credentials")
async def text_to_speech(payload: dict[str, Any], router_service: CapabilityRouter = Depends(_router)) -> Response:
    try:
        result = await router_service.execute("tts", payload, payload.get("preferred_providers", []))
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc
    audio_bytes = result.pop("audio_bytes", b"")
    if not audio_bytes:
        raise HTTPException(status_code=502, detail={"code": "empty_provider_audio", "message": "Provider returned no audio"})
    return Response(content=audio_bytes, media_type=str(result.get("content_type") or "audio/mpeg"), headers={"X-David-Provider": str(result.get("provider", "unknown"))})


@router.post("/stt", summary="Transcribe an uploaded audio file")
async def speech_to_text(
    file: UploadFile = File(...),
    preferred_provider: str | None = None,
    router_service: CapabilityRouter = Depends(_router),
) -> dict[str, Any]:
    content = await file.read()
    if len(content) > router_service.settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Uploaded audio exceeds the configured size limit")
    payload = {"audio_bytes": content, "filename": file.filename or "audio.wav", "content_type": file.content_type or "audio/wav"}
    try:
        return await router_service.execute("stt", payload, [preferred_provider] if preferred_provider else None)
    except ProviderIntegrationError as exc:
        raise _provider_error(exc) from exc

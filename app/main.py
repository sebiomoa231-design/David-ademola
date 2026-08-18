"""David AI backend entrypoint.

This entrypoint intentionally mounts the existing voice and orchestration routes
without replacing them. Additional domain routes can be added behind the same
FastAPI application as their implementations become available.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI

from app.api.routes.orchestrator import router as orchestrator_router
from app.api.routes.voice import router as voice_router
from app.core.cors import configure_cors


APP_VERSION = os.getenv("DAVID_AI_VERSION", "handoff-scaffold")

app = FastAPI(
    title="David Ademola AI",
    version=APP_VERSION,
    description="Personal AI operating system backend scaffold.",
    docs_url="/docs",
    redoc_url="/redoc",
)

configure_cors(app)
app.include_router(voice_router)
app.include_router(orchestrator_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "David Ademola AI",
        "status": "online",
        "version": APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "david-ai-backend",
        "version": APP_VERSION,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def compatibility_health() -> dict[str, str]:
    """Compatibility alias for existing frontend/deployment clients."""
    return await health()


@app.get("/api/readiness")
async def readiness() -> dict[str, object]:
    """Report scaffold readiness without pretending optional providers are configured."""
    return {
        "ready": True,
        "mode": "scaffold",
        "voice_routes": True,
        "orchestrator_routes": True,
        "external_providers_configured": bool(os.getenv("ELEVENLABS_API_KEY")),
        "note": "Domain persistence, auth, and external connector routes remain to be implemented.",
    }

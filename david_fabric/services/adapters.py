from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from david_fabric.core.config import settings


@dataclass(frozen=True)
class CapabilityAdapter:
    """A safe service boundary for a mixed-runtime upstream capability."""

    id: str
    capability: str
    name: str
    runtime: str
    source: str
    license: str
    url_attr: str | None = None
    health_path: str = "/"

    def url(self) -> str:
        return str(getattr(settings, self.url_attr, "")) if self.url_attr else ""


ADAPTERS: tuple[CapabilityAdapter, ...] = (
    CapabilityAdapter(
        id="voice-backend",
        capability="david-voice-backend",
        name="David Voice Backend reference",
        runtime="Python/FastAPI",
        source="uploaded:DavidAI-backend-with-voice (incomplete part-ab only)",
        license="not verified: complete archive part-aa missing",
        url_attr="voice_backend_url",
    ),
    CapabilityAdapter(
        id="creative-backend",
        capability="creative-backend",
        name="David Creative Backend",
        runtime="Node/Express/Mongo",
        source="uploaded:David-Sources-Pack-1-2/david-ai-backend.zip",
        license="inspect upstream LICENSE before redistribution",
        url_attr="creative_backend_url",
    ),
    CapabilityAdapter(
        id="agent-framework",
        capability="multi-agent",
        name="Microsoft Agent Framework",
        runtime="Python/.NET",
        source="uploaded:David-Sources-Pack-1-2/agent-framework-main.zip",
        license="MIT",
    ),
    CapabilityAdapter(
        id="playwright",
        capability="playwright",
        name="Playwright browser automation",
        runtime="Node",
        source="uploaded:David-Sources-Pack-2*/playwright-main.zip (partial)",
        license="Apache-2.0 + NOTICE",
        url_attr="playwright_url",
    ),
    CapabilityAdapter(
        id="wan2gp",
        capability="video",
        name="WanGP video/image/audio generation",
        runtime="Python/CUDA",
        source="uploaded:David-Sources-Pack-3/Wan2GP-main.zip (partial)",
        license="WanGP custom license; no paid API/SaaS/OEM without separate license",
        url_attr="wan2gp_url",
    ),
    CapabilityAdapter(
        id="n8n",
        capability="automation",
        name="n8n workflow automation",
        runtime="Node",
        source="uploaded:David-Sources-Pack-4/n8n-master.zip (partial)",
        license="Sustainable Use License; .ee files require Enterprise terms",
        url_attr="n8n_url",
    ),
    CapabilityAdapter(
        id="browser-use",
        capability="browser-use",
        name="Browser Use",
        runtime="Python",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="browser_use_url",
    ),
    CapabilityAdapter(
        id="comfyui",
        capability="image",
        name="ComfyUI image workflows",
        runtime="Python/CUDA",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="comfyui_url",
    ),
    CapabilityAdapter(
        id="faster-whisper",
        capability="stt",
        name="faster-whisper speech-to-text",
        runtime="Python/CTranslate2",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="faster_whisper_url",
    ),
    CapabilityAdapter(
        id="chatterbox",
        capability="voice",
        name="Chatterbox text-to-speech",
        runtime="Python/PyTorch",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="chatterbox_url",
    ),
    CapabilityAdapter(
        id="langfuse",
        capability="observability",
        name="Langfuse observability",
        runtime="Node/ClickHouse",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="langfuse_url",
    ),
    CapabilityAdapter(
        id="temporal",
        capability="durable-execution",
        name="Temporal durable execution",
        runtime="Go/server",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="temporal_url",
    ),
    CapabilityAdapter(
        id="coolify",
        capability="deployment-coolify",
        name="Coolify deployment",
        runtime="PHP/TypeScript",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="coolify_url",
    ),
    CapabilityAdapter(
        id="dokploy",
        capability="deployment-dokploy",
        name="Dokploy deployment",
        runtime="Node/TypeScript",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="dokploy_url",
    ),
)


def list_adapters() -> list[dict[str, Any]]:
    return [
        {
            "id": adapter.id,
            "capability": adapter.capability,
            "name": adapter.name,
            "runtime": adapter.runtime,
            "source": adapter.source,
            "license": adapter.license,
            "configured": bool(adapter.url()) if adapter.url_attr else True,
            "url_configured_by": adapter.url_attr,
        }
        for adapter in ADAPTERS
    ]


async def adapter_health() -> dict[str, dict[str, Any]]:
    """Report configured status and perform bounded GET probes when configured."""

    result: dict[str, dict[str, Any]] = {}
    timeout = httpx.Timeout(settings.adapter_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for adapter in ADAPTERS:
            url = adapter.url()
            if not url:
                result[adapter.id] = {"status": "unconfigured", "runtime": adapter.runtime}
                continue
            target = url.rstrip("/") + adapter.health_path
            try:
                response = await client.get(target)
                result[adapter.id] = {
                    "status": "healthy" if response.status_code < 500 else "unhealthy",
                    "code": response.status_code,
                    "runtime": adapter.runtime,
                }
            except Exception as exc:  # network failures are health data, not API failures
                result[adapter.id] = {
                    "status": "unreachable",
                    "error": str(exc)[:160],
                    "runtime": adapter.runtime,
                }
    return result

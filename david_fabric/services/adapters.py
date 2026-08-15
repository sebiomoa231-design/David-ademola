from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from david_fabric.core.config import settings


@dataclass(frozen=True)
class CapabilityAdapter:
    """A David-controlled boundary for a mixed-runtime capability."""

    id: str
    capability: str
    name: str
    runtime: str
    source: str
    license: str
    url_attr: str | None = None
    health_path: str = "/health"
    execute_path: str = "/execute"
    requires_gpu: bool = False
    requires_credentials: bool = False
    supports_fallback: bool = True

    def url(self) -> str:
        return str(getattr(settings, self.url_attr, "")) if self.url_attr else ""


ADAPTERS: tuple[CapabilityAdapter, ...] = (
    CapabilityAdapter(
        id="voice-backend",
        capability="david-voice-backend",
        name="David Voice Backend reference",
        runtime="Python/FastAPI",
        source="uploaded:DavidAI-backend-with-voice.part-aa+part-ab (missing middle archive chunks)",
        license="not verified: no license entry was recoverable from the supplied fragments",
        url_attr="voice_backend_url",
        requires_credentials=True,
    ),
    CapabilityAdapter(
        id="creative-backend",
        capability="creative-backend",
        name="David Creative Backend",
        runtime="Node/Express/Mongo",
        source="recovered:David-Sources-Pack-1/david-ai-backend.zip",
        license="no upstream LICENSE file present in supplied tree; adapter-only boundary",
        url_attr="creative_backend_url",
    ),
    CapabilityAdapter(
        id="agent-framework",
        capability="multi-agent",
        name="Microsoft Agent Framework",
        runtime="Python/.NET",
        source="recovered:David-Sources-Pack-1/agent-framework-main.zip",
        license="MIT",
    ),
    CapabilityAdapter(
        id="playwright",
        capability="playwright",
        name="Playwright browser automation",
        runtime="Node",
        source="recovered:David-Sources-Pack-2-1+2-2/playwright-main.zip",
        license="Apache-2.0 + NOTICE",
        url_attr="playwright_url",
    ),
    CapabilityAdapter(
        id="wan2gp",
        capability="video",
        name="WanGP video/image/audio generation",
        runtime="Python/CUDA",
        source="recovered:David-Sources-Pack-3+3-1+3-2/Wan2GP-main.zip (partial)",
        license="WanGP custom license; no paid API/SaaS/OEM without separate license",
        url_attr="wan2gp_url",
        requires_gpu=True,
    ),
    CapabilityAdapter(
        id="n8n",
        capability="automation",
        name="n8n workflow automation",
        runtime="Node",
        source="recovered:David-Sources-Pack-4/n8n-master.zip (partial)",
        license="Sustainable Use License; .ee files require Enterprise terms",
        url_attr="n8n_url",
        requires_credentials=True,
    ),
    CapabilityAdapter(
        id="browser-use",
        capability="browser-use",
        name="Browser Use",
        runtime="Python",
        source="recovered:David-Sources-Pack-1/browser-use-main.zip",
        license="MIT; upstream notice preserved",
        url_attr="browser_use_url",
        requires_credentials=True,
    ),
    CapabilityAdapter(
        id="openhands",
        capability="coding",
        name="OpenHands coding worker",
        runtime="Node/React/agent-server",
        source="recovered:David-Sources-Pack-1/OpenHands-main.zip",
        license="MIT",
        url_attr="openhands_url",
        requires_credentials=True,
    ),
    CapabilityAdapter(
        id="comfyui",
        capability="image",
        name="ComfyUI image workflows",
        runtime="Python/CUDA",
        source="recovered:David-Sources-Pack-2-1+2-2/ComfyUI-master.zip",
        license="GPL-3.0; adapter-only boundary",
        url_attr="comfyui_url",
        requires_gpu=True,
    ),
    CapabilityAdapter(
        id="faster-whisper",
        capability="stt",
        name="faster-whisper speech-to-text",
        runtime="Python/CTranslate2",
        source="recovered:David-Sources-Pack-2-1+2-2/faster-whisper-master.zip (corrupt test fixture)",
        license="MIT; upstream license preserved",
        url_attr="faster_whisper_url",
        requires_gpu=False,
    ),
    CapabilityAdapter(
        id="chatterbox",
        capability="voice",
        name="Chatterbox text-to-speech",
        runtime="Python/PyTorch",
        source="recovered:David-Sources-Pack-2-1+2-2/chatterbox-master.zip",
        license="see preserved upstream LICENSE; GPU/Torch runtime isolated",
        url_attr="chatterbox_url",
        requires_gpu=True,
    ),
    CapabilityAdapter(
        id="langfuse",
        capability="observability",
        name="Langfuse observability",
        runtime="Node/ClickHouse",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="langfuse_url",
        requires_credentials=True,
    ),
    CapabilityAdapter(
        id="langgraph",
        capability="stateful-agents",
        name="LangGraph stateful agent workflows",
        runtime="Python",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="langgraph_url",
    ),
    CapabilityAdapter(
        id="temporal",
        capability="durable-execution",
        name="Temporal durable execution",
        runtime="Go/server",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="temporal_url",
        requires_credentials=True,
    ),
    CapabilityAdapter(
        id="coolify",
        capability="deployment-coolify",
        name="Coolify deployment",
        runtime="PHP/TypeScript",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="coolify_url",
        requires_credentials=True,
    ),
    CapabilityAdapter(
        id="dokploy",
        capability="deployment-dokploy",
        name="Dokploy deployment",
        runtime="Node/TypeScript",
        source="configured service boundary",
        license="upstream terms apply",
        url_attr="dokploy_url",
        requires_credentials=True,
    ),
)


_ADAPTER_BY_ID = {adapter.id: adapter for adapter in ADAPTERS}
_ADAPTER_BY_CAPABILITY = {adapter.capability: adapter for adapter in ADAPTERS}


def get_adapter(adapter_id: str | None) -> CapabilityAdapter | None:
    if not adapter_id:
        return None
    return _ADAPTER_BY_ID.get(adapter_id)


def adapter_for_capability(capability_id: str, item: dict[str, Any] | None = None) -> CapabilityAdapter | None:
    configured_id = (item or {}).get("adapter")
    return get_adapter(str(configured_id)) if configured_id else _ADAPTER_BY_CAPABILITY.get(capability_id)


def _base_state(adapter: CapabilityAdapter | None) -> tuple[str, str, bool]:
    if adapter is None:
        return "IMPLEMENTED", "native Fabric capability", True
    if not adapter.url_attr:
        return "IMPLEMENTED", "upstream source preserved; native Fabric boundary available", True
    if not adapter.url():
        return "REQUIRES_EXTERNAL_SERVICE", "service URL is not configured", False
    return "CONNECTED", "service URL configured; health probe required", False


def readiness_for_adapter(
    adapter: CapabilityAdapter | None,
    health: dict[str, Any] | None = None,
    *,
    requires_approval: bool = False,
) -> tuple[list[str], str, bool, str]:
    state, reason, available = _base_state(adapter)
    readiness: list[str] = [state]
    if adapter is None:
        readiness.extend(["CONNECTED", "HEALTHY", "READY"])
    elif not adapter.url_attr:
        readiness.extend(["CONNECTED", "HEALTHY", "READY"])
    else:
        status = str((health or {}).get("status", state)).lower()
        if status == "healthy":
            readiness.extend(["HEALTHY", "READY"])
            state, reason, available = "READY", "service health probe passed", True
        elif status in {"unreachable", "unhealthy"}:
            state, reason, available = status.upper(), "service health probe failed", False
        elif not adapter.url():
            readiness = ["REQUIRES_EXTERNAL_SERVICE"]
        else:
            readiness.append("CONNECTED")
    if adapter and adapter.requires_credentials and not adapter.url():
        readiness.append("REQUIRES_CREDENTIAL")
    if adapter and adapter.requires_gpu:
        readiness.append("REQUIRES_GPU")
    if requires_approval:
        readiness.append("REQUIRES_APPROVAL")
        available = False
    return list(dict.fromkeys(readiness)), state, available, reason


def list_adapters() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for adapter in ADAPTERS:
        readiness, state, available, reason = readiness_for_adapter(adapter)
        result.append(
            {
                "id": adapter.id,
                "capability": adapter.capability,
                "name": adapter.name,
                "runtime": adapter.runtime,
                "source": adapter.source,
                "license": adapter.license,
                "configured": bool(adapter.url()) if adapter.url_attr else True,
                "url_configured_by": adapter.url_attr,
                "requires_gpu": adapter.requires_gpu,
                "requires_credentials": adapter.requires_credentials,
                "supports_fallback": adapter.supports_fallback,
                "readiness": readiness,
                "state": state,
                "available": available,
                "reason": reason,
            }
        )
    return result


async def adapter_health() -> dict[str, dict[str, Any]]:
    """Perform bounded health probes; missing services are reported, never faked."""

    result: dict[str, dict[str, Any]] = {}
    timeout = httpx.Timeout(settings.adapter_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for adapter in ADAPTERS:
            url = adapter.url()
            if not url:
                result[adapter.id] = {
                    "status": "unconfigured",
                    "state": "REQUIRES_EXTERNAL_SERVICE" if adapter.url_attr else "READY",
                    "runtime": adapter.runtime,
                    "configured": False if adapter.url_attr else True,
                }
                continue
            target = url.rstrip("/") + adapter.health_path
            try:
                response = await client.get(target)
                healthy = response.status_code < 500
                result[adapter.id] = {
                    "status": "healthy" if healthy else "unhealthy",
                    "state": "READY" if healthy else "UNAVAILABLE",
                    "code": response.status_code,
                    "runtime": adapter.runtime,
                    "configured": True,
                }
            except Exception as exc:  # network failures are health data, not API failures
                result[adapter.id] = {
                    "status": "unreachable",
                    "state": "UNAVAILABLE",
                    "error": str(exc)[:160],
                    "runtime": adapter.runtime,
                    "configured": True,
                }
    return result


async def invoke_adapter(
    adapter: CapabilityAdapter,
    *,
    run_id: str,
    objective: str,
    input_data: dict[str, Any],
) -> dict[str, Any]:
    """Invoke a configured service only through the documented generic Fabric contract."""

    url = adapter.url()
    if not url:
        raise RuntimeError(f"{adapter.id} requires an external service URL")
    target = url.rstrip("/") + adapter.execute_path
    timeout = httpx.Timeout(settings.adapter_timeout_seconds)
    payload = {"run_id": run_id, "objective": objective, "input": input_data}
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.post(target, json=payload)
        if response.status_code >= 400:
            raise RuntimeError(f"{adapter.id} returned HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(f"{adapter.id} returned non-JSON output") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{adapter.id} returned an invalid execution envelope")
    return data

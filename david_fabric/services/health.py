from __future__ import annotations

from typing import Any

from david_fabric.services.adapters import adapter_health
from david_fabric.services.registry import list_enriched_capabilities


async def service_health() -> dict[str, dict[str, Any]]:
    return await adapter_health()


async def fabric_readiness() -> dict[str, Any]:
    services = await adapter_health()
    capabilities = list_enriched_capabilities(services)
    ready = [item for item in capabilities if item.get("state") == "READY"]
    unavailable = [item for item in capabilities if not item.get("available")]
    return {
        "status": "ready" if not unavailable else "degraded",
        "ready_capabilities": len(ready),
        "unavailable_capabilities": len(unavailable),
        "capabilities": capabilities,
        "services": services,
    }

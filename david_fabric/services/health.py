from __future__ import annotations

from david_fabric.services.adapters import adapter_health


async def service_health() -> dict[str, dict[str, object]]:
    return await adapter_health()

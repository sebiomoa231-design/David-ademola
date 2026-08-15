from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from david_fabric.services.adapters import adapter_for_capability, readiness_for_adapter


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG = PROJECT_ROOT / "config" / "capabilities.yaml"


@lru_cache(maxsize=1)
def load_capabilities() -> list[dict[str, Any]]:
    with CONFIG.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    capabilities = data.get("capabilities", [])
    return [item for item in capabilities if isinstance(item, dict) and item.get("id")]


def clear_registry_cache() -> None:
    load_capabilities.cache_clear()


def get_capability(capability_id: str) -> dict[str, Any] | None:
    item = next(
        (item for item in load_capabilities() if item.get("id") == capability_id),
        None,
    )
    return deepcopy(item) if item else None


def enrich_capability(
    item: dict[str, Any],
    health: dict[str, Any] | None = None,
) -> dict[str, Any]:
    enriched = deepcopy(item)
    capability_id = str(enriched.get("id"))
    adapter = adapter_for_capability(capability_id, enriched)
    adapter_id = str(enriched.get("adapter") or adapter.id) if adapter else enriched.get("adapter")
    health_record = (health or {}).get(adapter_id, {}) if adapter_id else {}
    requires_approval = bool(enriched.get("requires_approval", False))
    readiness, state, available, reason = readiness_for_adapter(
        adapter,
        health_record,
        requires_approval=requires_approval,
    )
    if str(enriched.get("mode", "")).lower() == "native":
        readiness = ["IMPLEMENTED", "CONNECTED", "HEALTHY", "READY"]
        state, available, reason = "READY", True, "native David implementation"
    elif not adapter and enriched.get("status", "").startswith("not-uploaded"):
        readiness = ["REQUIRES_EXTERNAL_SERVICE"]
        state, available, reason = "UNAVAILABLE", False, "service boundary is not configured"
    elif enriched.get("status", "").startswith("partial-upload"):
        readiness = ["IMPLEMENTED", "REQUIRES_EXTERNAL_SERVICE"]
        state, available, reason = "UNAVAILABLE", False, "supplied source is incomplete"
    enriched.update(
        {
            "adapter": adapter_id,
            "readiness": list(dict.fromkeys(readiness)),
            "state": state,
            "available": available,
            "reason": reason,
            "fallback_capabilities": list(enriched.get("fallbacks", [])),
            "agent": enriched.get("agent"),
            "skill": enriched.get("skill"),
            "tool": enriched.get("tool"),
            "provider": enriched.get("provider"),
            "inputs": list(enriched.get("inputs", [])),
            "outputs": list(enriched.get("outputs", [])),
            "permissions": list(enriched.get("permissions", [])),
        }
    )
    return enriched


def list_enriched_capabilities(health: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [enrich_capability(item, health) for item in load_capabilities()]


def match_capabilities(
    text: str,
    *,
    requested_capability: str | None = None,
    health: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return deterministic, enriched candidates ordered by match then readiness."""

    normalized = text.casefold()
    requested = (requested_capability or "").casefold()
    scored: list[tuple[int, int, int, dict[str, Any]]] = []
    for index, raw_item in enumerate(load_capabilities()):
        item = enrich_capability(raw_item, health)
        capability_id = str(item["id"]).casefold()
        keywords = [str(keyword).casefold() for keyword in item.get("keywords", [])]
        score = sum(1 for keyword in keywords if keyword and keyword in normalized)
        if requested and (requested == capability_id or requested == str(item.get("category", "")).casefold()):
            score += 100
        elif requested and requested in keywords:
            score += 50
        if score or not text.strip():
            readiness_bonus = 10 if item.get("available") else 0
            scored.append((score, readiness_bonus, -index, item))
    scored.sort(key=lambda row: (row[0], row[1], row[2]), reverse=True)
    return [item for _, _, _, item in scored]

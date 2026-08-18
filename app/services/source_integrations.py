"""Safe catalog of separately adapted David AI source repositories.

The primary David AI control plane remains authoritative. This module exposes only
public metadata about source packs and the compatibility boundaries used when
adapting them; it never reads or returns credentials, environment files, or raw
source-control tokens.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


SOURCE_PACKS: tuple[dict[str, Any], ...] = (
    {
        "id": "david-ai-backend",
        "name": "David AI Backend",
        "repository": "https://github.com/sebiomoa231-design/DavidAI-backend",
        "family": "FastAPI backend",
        "adapted_capabilities": [
            "provider-oriented routing patterns",
            "private single-user workspace boundaries",
            "Manus agent-task adapter reference",
        ],
        "integration_boundary": "Provider and capability metadata only; the primary FastAPI control plane remains authoritative.",
        "source_files": [
            "david/providers/manus.py",
            "david/api/routes_capabilities.py",
            "david/security/workspace.py",
        ],
    },
    {
        "id": "david-ai-backend-304",
        "name": "David AI Backend 3.0.4",
        "repository": "https://github.com/sebiomoa231-design/DavidAI-backend3.0.4",
        "family": "FastAPI compatibility backend",
        "adapted_capabilities": [
            "health and version compatibility conventions",
            "voice, knowledge, and planning route inventory",
            "Render-safe startup shims",
        ],
        "integration_boundary": "Compatibility inventory and route contracts; existing primary routes are not replaced.",
        "source_files": [
            "main.py",
            "app/api/router.py",
            "voice_engine.py",
            "knowledge_engine.py",
        ],
    },
    {
        "id": "david-ai-command-center",
        "name": "David AI Command Center",
        "repository": "https://github.com/sebiomoa231-design/david-ai-command-center-e7c1dffe",
        "family": "TanStack Start command center",
        "adapted_capabilities": [
            "David core visual language",
            "prompt-driven generation workspace",
            "capability-oriented navigation vocabulary",
        ],
        "integration_boundary": "Visual and interaction patterns adapted into isolated Next.js components.",
        "source_files": [
            "src/components/david/core-orb.tsx",
            "src/components/david/generate-workspace.tsx",
            "src/routes/websites.tsx",
        ],
    },
    {
        "id": "jarvis-unified-intelligence",
        "name": "Jarvis Unified Intelligence",
        "repository": "https://github.com/sebiomoa231-design/jarvis-unified-intelligence",
        "family": "TanStack Start intelligence UI",
        "adapted_capabilities": [
            "extended assistant state vocabulary",
            "Jarvis-style execution and processing states",
            "HUD-oriented status presentation",
        ],
        "integration_boundary": "State vocabulary is mapped into the primary command-center surface; its separate auth and database shell is not imported.",
        "source_files": [
            "src/components/jarvis/ai-core.tsx",
            "src/components/jarvis/hud-panel.tsx",
            "src/lib/jarvis/activity.ts",
        ],
    },
    {
        "id": "david-ai-os-5ea657d7",
        "name": "David AI OS",
        "repository": "https://github.com/sebiomoa231-design/david-ai-os-5ea657d7",
        "family": "TanStack Start AI OS",
        "adapted_capabilities": [
            "prompt-to-website workflow",
            "AI core state badge patterns",
            "OS-style capability status language",
        ],
        "integration_boundary": "Website generation behavior is adapted to the primary /api/website/generate contract.",
        "source_files": [
            "src/routes/websites.tsx",
            "src/components/os/AICore.tsx",
            "src/components/os/CoreStateContext.tsx",
        ],
    },
    {
        "id": "david-ai-os-bd15f232",
        "name": "David AI OS — alternate source",
        "repository": "https://github.com/sebiomoa231-design/david-ai-os-bd15f232",
        "family": "TanStack Start AI OS variant",
        "adapted_capabilities": [
            "cross-checked OS component contracts",
            "route and capability naming compatibility",
            "responsive workspace patterns",
        ],
        "integration_boundary": "Used as a separately audited reference; duplicate generated scaffolding is intentionally not copied.",
        "source_files": [
            "src/components/os/OSShell.tsx",
            "src/components/os/Panel.tsx",
            "src/routes/automations.tsx",
        ],
    },
)


def list_source_packs() -> list[dict[str, Any]]:
    """Return a defensive copy suitable for public API responses."""
    return deepcopy(list(SOURCE_PACKS))


def get_source_pack(source_id: str) -> dict[str, Any] | None:
    """Return one source pack by stable identifier."""
    normalized = source_id.strip().lower()
    for source in SOURCE_PACKS:
        if source["id"] == normalized:
            return deepcopy(source)
    return None

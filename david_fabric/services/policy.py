from __future__ import annotations

from typing import Any

from david_fabric.core.config import settings


SIDE_EFFECTS = {
    "deployment",
    "deployment-coolify",
    "deployment-dokploy",
    "publish",
    "delete",
    "purchase",
    "external_write",
    "automation",
    "n8n",
    "webhook",
    "deploy",
}

APPROVAL_REQUIRED = {
    "deployment",
    "deployment-coolify",
    "deployment-dokploy",
    "publish",
    "delete",
    "purchase",
    "automation",
    "n8n",
    "webhook",
    "deploy",
}


def _normalize(capability: str) -> str:
    return capability.strip().casefold().replace("_", "-")


def _metadata_requires_approval(capability: str) -> bool:
    try:
        from david_fabric.services.registry import get_capability

        item = get_capability(capability) or {}
        permissions = {_normalize(str(value)) for value in item.get("permissions", [])}
        return bool(item.get("requires_approval")) or bool(
            permissions & {"external-write", "deploy", "publish", "delete", "purchase", "webhook"}
        )
    except Exception:
        return False


def requires_approval(capability: str) -> bool:
    normalized = _normalize(capability)
    return normalized in APPROVAL_REQUIRED or _metadata_requires_approval(capability)


def authorize(capability: str, approved: bool = False) -> tuple[bool, str]:
    normalized = _normalize(capability)
    is_side_effect = normalized in SIDE_EFFECTS or requires_approval(capability)
    if is_side_effect and not settings.allow_external_side_effects:
        return False, "External side effects are disabled by policy."
    if requires_approval(capability) and not approved:
        return False, "Explicit approval is required for this capability."
    return True, "allowed"


def policy_snapshot() -> dict[str, Any]:
    return {
        "external_side_effects": {
            "allowed": settings.allow_external_side_effects,
            "default": "deny",
        },
        "approval_required": sorted(APPROVAL_REQUIRED),
        "credentials_never_exposed_to_model": True,
        "audit_events": ["tool_calls", "provider_events", "agent_handoffs"],
    }

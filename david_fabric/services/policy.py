from __future__ import annotations

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
}


def requires_approval(capability: str) -> bool:
    return capability in APPROVAL_REQUIRED


def authorize(capability: str, approved: bool = False) -> tuple[bool, str]:
    if capability in SIDE_EFFECTS and not settings.allow_external_side_effects:
        return False, "External side effects are disabled by policy."
    if requires_approval(capability) and not approved:
        return False, "Explicit approval is required for this capability."
    return True, "allowed"

from david_fabric.core.config import settings

SIDE_EFFECTS = {"deployment", "publish", "delete", "purchase", "external_write"}

def requires_approval(capability):
    if capability in {"deployment", "publish"}:
        return settings.require_approval_for_deployment if capability=="deployment" else settings.require_approval_for_publish
    if capability == "delete":
        return settings.require_approval_for_delete
    if capability == "purchase":
        return settings.require_approval_for_purchase
    return False

def authorize(capability, approved=False):
    if not settings.allow_external_side_effects and capability in SIDE_EFFECTS:
        return False, "External side effects are disabled by policy."
    if requires_approval(capability) and not approved:
        return False, "Explicit approval is required for this capability."
    return True, "allowed"

from __future__ import annotations

"""Safe, data-only discovery for David capability manifests.

This module deliberately reads only explicit manifest files from an allowlisted
directory. It does not import, evaluate, or execute repository code while
discovering capabilities.
"""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

import yaml

from david_fabric.core.config import PROJECT_ROOT


MANIFEST_ROOT = PROJECT_ROOT / "capabilities"
MANIFEST_FILENAMES = {"capability.yaml", "capability.yml", "capability.json"}
CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
REQUIRED_FIELDS = {"id", "name", "category", "description", "inputs", "outputs", "keywords"}
ALLOWED_FIELDS = REQUIRED_FIELDS | {
    "agent",
    "skill",
    "tool",
    "provider",
    "runtime",
    "permissions",
    "fallbacks",
    "requires_approval",
    "entrypoint",
    "version",
}
SENSITIVE_FIELD_TOKENS = ("secret", "token", "password", "api_key", "apikey", "credential")


@dataclass(frozen=True)
class ManifestIssue:
    path: str
    reason: str


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _is_safe_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def _contains_sensitive_field(data: dict[str, Any]) -> bool:
    return any(token in key.casefold() for key in data for token in SENSITIVE_FIELD_TOKENS)


def _read_manifest(path: Path) -> dict[str, Any]:
    if path.suffix == ".json":
        import json

        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    else:
        with path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("manifest root must be an object")
    return loaded


def _validate_manifest(data: dict[str, Any]) -> str | None:
    missing = REQUIRED_FIELDS - set(data)
    if missing:
        return f"missing required fields: {', '.join(sorted(missing))}"
    unsupported = set(data) - ALLOWED_FIELDS
    if unsupported:
        return f"unsupported fields: {', '.join(sorted(unsupported))}"
    if _contains_sensitive_field(data):
        return "sensitive fields are not permitted in capability manifests"
    if not isinstance(data["id"], str) or not CAPABILITY_ID.fullmatch(data["id"]):
        return "id must be lowercase kebab-case"
    for field in ("name", "category", "description"):
        if not isinstance(data[field], str) or not data[field].strip():
            return f"{field} must be a non-empty string"
    for field in ("inputs", "outputs", "keywords"):
        if not _is_safe_string_list(data[field]):
            return f"{field} must be a non-empty string array"
    for field in ("permissions", "fallbacks"):
        if field in data and not _is_safe_string_list(data[field]):
            return f"{field} must be a non-empty string array when provided"
    if "entrypoint" in data and (not isinstance(data["entrypoint"], str) or not data["entrypoint"].startswith("registry:")):
        return "entrypoint must use a registry: reference"
    return None


def discover_manifest_capabilities(existing_ids: set[str] | None = None) -> tuple[list[dict[str, Any]], list[ManifestIssue]]:
    """Return validated manifest entries and non-sensitive rejection diagnostics."""

    existing_ids = set(existing_ids or set())
    capabilities: list[dict[str, Any]] = []
    issues: list[ManifestIssue] = []
    if not MANIFEST_ROOT.is_dir():
        return capabilities, issues

    for path in sorted(MANIFEST_ROOT.rglob("*")):
        if not path.is_file() or path.name not in MANIFEST_FILENAMES or path.is_symlink():
            continue
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(MANIFEST_ROOT.resolve(strict=True))
        except (OSError, ValueError):
            issues.append(ManifestIssue(_relative(path), "manifest is outside the allowlisted directory"))
            continue
        try:
            data = _read_manifest(resolved)
            reason = _validate_manifest(data)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            issues.append(ManifestIssue(_relative(path), f"manifest could not be read: {type(exc).__name__}"))
            continue
        if reason:
            issues.append(ManifestIssue(_relative(path), reason))
            continue
        capability_id = str(data["id"])
        if capability_id in existing_ids:
            issues.append(ManifestIssue(_relative(path), f"duplicate capability id: {capability_id}"))
            continue
        existing_ids.add(capability_id)
        content_hash = sha256(resolved.read_bytes()).hexdigest()
        capabilities.append(
            {
                **data,
                "source": f"manifest:{_relative(path)}",
                "mode": "registered-manifest",
                "status": "registered-not-executable-until-adapter-is-connected",
                "manifest_path": _relative(path),
                "manifest_hash": content_hash,
                "registration": "explicit-manifest",
            }
        )
    return capabilities, issues


def discovery_report(existing_ids: set[str] | None = None) -> dict[str, Any]:
    capabilities, issues = discover_manifest_capabilities(existing_ids)
    return {
        "mode": "allowlisted-manifest-scan",
        "root": "capabilities",
        "executed_repository_code": False,
        "capabilities": capabilities,
        "issues": [{"path": issue.path, "reason": issue.reason} for issue in issues],
    }

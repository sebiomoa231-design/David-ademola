"""GitHub repository and audit-log persistence for David AI.

Mirrors the conventions of ``SupabasePersistence``: server-side secret
headers only, safe error mapping, ``owner_id``, ``uuid4`` ids, and ISO
timestamps. Everything lands in the existing David AI Supabase project
(tables ``david_github_repositories`` and ``david_github_audit_log``) so no
second database is created.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.services.supabase_service import SupabaseApiError, SupabasePersistence, _now
from app.services.github_service import (
    AUDIT_DEPLOYMENT_COMPLETED,
    AUDIT_DEPLOYMENT_FAILED,
    AUDIT_DEPLOYMENT_REQUESTED,
    AUDIT_GITHUB_CONNECTED,
    AUDIT_GITHUB_DISCONNECTED,
    AUDIT_REPO_COMMIT_CREATED,
    AUDIT_REPO_CREATED,
    AUDIT_REPO_FILES_PUSHED,
    AUDIT_REPO_INITIALIZED,
    AUDIT_REPO_NAME_COLLISION,
    AUDIT_REPO_UPDATED,
)

logger = logging.getLogger(__name__)


class GitHubPersistence:
    """Database boundary for GitHub repository tracking and audit logs."""

    REPOS_TABLE = "david_github_repositories"
    AUDIT_TABLE = "david_github_audit_log"
    owner_id = "default-owner"

    def __init__(self, supabase: SupabasePersistence) -> None:
        self.supabase = supabase

    def _client(self):
        return self.supabase.require_database()

    @property
    def is_available(self) -> bool:
        return self.supabase.database_enabled

    # ------------------------------------------------------------------
    # Repository records
    # ------------------------------------------------------------------

    def list_repositories(self, project_id: str | None = None) -> list[dict[str, Any]]:
        return self.supabase.list_github_repositories(project_id=project_id)

    def get_repository(self, repository_id: str) -> dict[str, Any] | None:
        return self.supabase.get_github_repository(repository_id)

    def get_repository_by_name(self, repository_full_name: str) -> dict[str, Any] | None:
        return self.supabase.get_github_repository_by_full_name(repository_full_name)

    def create_repository_record(self, payload: dict[str, Any], project_id: str | None = None) -> dict[str, Any]:
        data = dict(payload)
        if project_id:
            data["project_id"] = project_id
        return self.supabase.create_github_repository(data)

    def update_repository(self, repository_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        rows = self.supabase.update_github_repository(repository_id, payload)
        return rows[0] if rows else None

    def set_deployment(
        self,
        repository_id: str,
        *,
        provider: str | None = None,
        url: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        payload: dict[str, Any] = {}
        if provider is not None:
            payload["deployment_provider"] = provider
        if url is not None:
            payload["deployment_url"] = url
        if status is not None:
            payload["deployment_status"] = status
        return self.update_repository(repository_id, payload)

    # ------------------------------------------------------------------
    # Audit log (never stores secrets; details are sanitized metadata)
    # ------------------------------------------------------------------

    def log_event(self, event: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        sanitized = sanitize_details(details or {})
        try:
            return self.supabase.create_github_audit_event(event, sanitized)
        except SupabaseApiError as exc:
            logger.warning(f"audit log write failed for event '{event}': {exc}")
            return {"id": str(uuid.uuid4()), "event": event, "details": sanitized}

    def list_audit_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.supabase.list_github_audit_events(limit=limit)


def sanitize_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove anything secret-shaped so audit records never persist secrets."""
    out: dict[str, Any] = {}
    for key, value in details.items():
        lowered = str(key).lower()
        if any(secret in lowered for secret in ("token", "secret", "key", "password", "authorization", "private", "credential")):
            continue
        out[key] = value
    return out


# Centralized audit helpers so every GitHub route logs consistently.
def audit_connected(persistence: GitHubPersistence, github_login: str) -> None:
    persistence.log_event(AUDIT_GITHUB_CONNECTED, {"github_login": github_login})


def audit_disconnected(persistence: GitHubPersistence) -> None:
    persistence.log_event(AUDIT_GITHUB_DISCONNECTED, {})


def audit_repository_created(persistence: GitHubPersistence, repo: dict[str, Any], project_id: str | None) -> None:
    persistence.log_event(
        AUDIT_REPO_CREATED,
        {
            "repository_full_name": repo.get("repository_full_name"),
            "repository_url": repo.get("repository_url"),
            "project_id": project_id,
        },
    )


def audit_name_collision(persistence: GitHubPersistence, name: str) -> None:
    persistence.log_event(AUDIT_REPO_NAME_COLLISION, {"repository_name": name})


def audit_initialized(persistence: GitHubPersistence, full_name: str) -> None:
    persistence.log_event(AUDIT_REPO_INITIALIZED, {"repository_full_name": full_name})


def audit_files_pushed(persistence: GitHubPersistence, full_name: str, file_count: int, project_id: str | None) -> None:
    persistence.log_event(
        AUDIT_REPO_FILES_PUSHED, {"repository_full_name": full_name, "file_count": file_count, "project_id": project_id}
    )


def audit_commit_created(persistence: GitHubPersistence, full_name: str, sha: str, project_id: str | None) -> None:
    persistence.log_event(AUDIT_REPO_COMMIT_CREATED, {"repository_full_name": full_name, "commit_sha": sha, "project_id": project_id})


def audit_repository_updated(persistence: GitHubPersistence, full_name: str, change: str) -> None:
    persistence.log_event(AUDIT_REPO_UPDATED, {"repository_full_name": full_name, "change": change})


def audit_deployment_requested(persistence: GitHubPersistence, full_name: str, provider: str) -> None:
    persistence.log_event(AUDIT_DEPLOYMENT_REQUESTED, {"repository_full_name": full_name, "provider": provider})


def audit_deployment_completed(persistence: GitHubPersistence, full_name: str, provider: str, url: str) -> None:
    persistence.log_event(AUDIT_DEPLOYMENT_COMPLETED, {"repository_full_name": full_name, "provider": provider, "deployment_url": url})


def audit_deployment_failed(persistence: GitHubPersistence, full_name: str, provider: str, reason: str) -> None:
    persistence.log_event(AUDIT_DEPLOYMENT_FAILED, {"repository_full_name": full_name, "provider": provider, "reason": reason})

from __future__ import annotations

import json
import logging
import mimetypes
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import quote
from uuid import uuid4

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class SupabaseApiError(RuntimeError):
    """A safe, non-secret error returned by Supabase Data or Storage APIs."""

    def __init__(self, message: str, status_code: int | None = None, path: str = "") -> None:
        self.status_code = status_code
        self.path = path
        super().__init__(message)


class SupabaseNotConfigured(SupabaseApiError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _first(rows: Any) -> dict[str, Any]:
    if isinstance(rows, list) and rows:
        return dict(rows[0])
    if isinstance(rows, dict):
        return dict(rows)
    raise SupabaseApiError("Supabase did not return the expected record representation")


def _safe_filename(filename: str) -> str:
    name = PurePosixPath(filename or "upload.bin").name
    cleaned = "".join(char if char.isalnum() or char in ".-_" else "_" for char in name)
    return cleaned[:180] or "upload.bin"


class SupabaseClient:
    """Small dependency-light client for the Supabase Data and Storage APIs.

    The secret key is read from ``Settings`` and is used only in backend-to-
    Supabase requests. It is never returned in errors or response models.
    """

    def __init__(self, settings: Settings) -> None:
        if not settings.supabase_url or not settings.supabase_secret_key:
            raise SupabaseNotConfigured("Supabase server configuration is incomplete")
        self.settings = settings
        self.base_url = settings.supabase_url.rstrip("/")
        self.timeout = settings.supabase_request_timeout_seconds
        self.headers = {
            "apikey": settings.supabase_secret_key,
            "Authorization": f"Bearer {settings.supabase_secret_key}",
            "X-Client-Info": "david-ai-backend",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        request_headers = dict(self.headers)
        request_headers.update(headers or {})
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    content=content,
                    headers=request_headers,
                )
        except httpx.HTTPError as exc:
            raise SupabaseApiError("Supabase request failed", path=path) from exc

        if response.status_code >= 400:
            message = "Supabase request was rejected"
            try:
                payload = response.json()
                if isinstance(payload, dict):
                    message = str(payload.get("message") or payload.get("error") or payload.get("details") or message)
            except ValueError:
                pass
            raise SupabaseApiError(message[:500], response.status_code, path)

        if not response.content:
            return None
        content_type = response.headers.get("content-type", "")
        if "json" in content_type:
            try:
                return response.json()
            except ValueError:
                return None
        return response.content

    def select(self, table: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        result = self._request("GET", f"/rest/v1/{quote(table, safe='')}", params=params or {})
        if not isinstance(result, list):
            raise SupabaseApiError("Supabase select did not return a list")
        return [dict(item) for item in result if isinstance(item, dict)]

    def insert(self, table: str, payload: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = self._request(
            "POST",
            f"/rest/v1/{quote(table, safe='')}",
            json_body=payload,
            headers={"Prefer": "return=representation"},
        )
        if result is None:
            return []
        if isinstance(result, dict):
            return [dict(result)]
        if isinstance(result, list):
            return [dict(item) for item in result if isinstance(item, dict)]
        raise SupabaseApiError("Supabase insert returned an unexpected response")

    def upsert(self, table: str, payload: dict[str, Any] | list[dict[str, Any]], on_conflict: str) -> list[dict[str, Any]]:
        result = self._request(
            "POST",
            f"/rest/v1/{quote(table, safe='')}",
            params={"on_conflict": on_conflict},
            json_body=payload,
            headers={"Prefer": "resolution=merge-duplicates,return=representation"},
        )
        if result is None:
            return []
        if isinstance(result, dict):
            return [dict(result)]
        if isinstance(result, list):
            return [dict(item) for item in result if isinstance(item, dict)]
        raise SupabaseApiError("Supabase upsert returned an unexpected response")

    def update(self, table: str, payload: dict[str, Any], filters: dict[str, str]) -> list[dict[str, Any]]:
        result = self._request(
            "PATCH",
            f"/rest/v1/{quote(table, safe='')}",
            params=filters,
            json_body=payload,
            headers={"Prefer": "return=representation"},
        )
        if result is None:
            return []
        if isinstance(result, dict):
            return [dict(result)]
        if isinstance(result, list):
            return [dict(item) for item in result if isinstance(item, dict)]
        raise SupabaseApiError("Supabase update returned an unexpected response")

    def delete(self, table: str, filters: dict[str, str]) -> list[dict[str, Any]]:
        result = self._request(
            "DELETE",
            f"/rest/v1/{quote(table, safe='')}",
            params=filters,
            headers={"Prefer": "return=representation"},
        )
        if result is None:
            return []
        if isinstance(result, dict):
            return [dict(result)]
        if isinstance(result, list):
            return [dict(item) for item in result if isinstance(item, dict)]
        return []

    def upload(self, path: str, content: bytes, content_type: str | None = None) -> dict[str, Any] | None:
        bucket = quote(self.settings.supabase_storage_bucket, safe="")
        object_path = quote(path.lstrip("/"), safe="/")
        return self._request(
            "POST",
            f"/storage/v1/object/{bucket}/{object_path}",
            content=content,
            headers={
                "Content-Type": content_type or "application/octet-stream",
                "x-upsert": "false",
            },
        )

    def remove(self, path: str) -> Any:
        bucket = quote(self.settings.supabase_storage_bucket, safe="")
        return self._request(
            "DELETE",
            "/storage/v1/object",
            json_body={"prefixes": [f"{self.settings.supabase_storage_bucket}/{path.lstrip('/')}" ]},
        )

    def signed_url(self, path: str, expires_in: int) -> str:
        bucket = quote(self.settings.supabase_storage_bucket, safe="")
        object_path = quote(path.lstrip("/"), safe="/")
        result = self._request(
            "POST",
            f"/storage/v1/object/sign/{bucket}/{object_path}",
            json_body={"expiresIn": max(60, int(expires_in))},
            headers={"Content-Type": "application/json"},
        )
        if not isinstance(result, dict):
            raise SupabaseApiError("Supabase did not return a signed URL")
        signed = result.get("signedURL") or result.get("signedUrl") or result.get("signed_url")
        if not isinstance(signed, str) or not signed:
            raise SupabaseApiError("Supabase did not return a signed URL")
        if signed.startswith("http://") or signed.startswith("https://"):
            return signed
        if signed.startswith("/storage/v1/"):
            return f"{self.base_url}{signed}"
        return f"{self.base_url}/storage/v1/{signed.lstrip('/')}"


class SupabasePersistence:
    """Persistence and asset operations used by David's existing services."""

    owner_id = "default-owner"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = SupabaseClient(settings) if settings.supabase_is_configured else None

    @property
    def storage_enabled(self) -> bool:
        return self.client is not None

    @property
    def database_enabled(self) -> bool:
        return self.client is not None and self.settings.supabase_persistence_enabled

    def require_client(self) -> SupabaseClient:
        if self.client is None:
            raise SupabaseNotConfigured("Supabase is not configured")
        return self.client

    def require_database(self) -> SupabaseClient:
        if not self.database_enabled:
            raise SupabaseNotConfigured("Supabase database persistence is disabled")
        return self.require_client()

    def health(self) -> dict[str, Any]:
        client = self.require_client()
        # The REST root is a safe connectivity probe even before David's tables
        # have been created by the migration in database/migrations/.
        client._request("GET", "/rest/v1/")
        return {"configured": True, "database_enabled": self.database_enabled, "storage_bucket": self.settings.supabase_storage_bucket}

    def _list(self, table: str, *, limit: int = 100, order: str = "updated_at.desc", filters: dict[str, str] | None = None) -> list[dict[str, Any]]:
        params = {"select": "*", "limit": str(max(1, min(limit, 500)))}
        if order:
            params["order"] = order
        if filters:
            params.update(filters)
        return self.require_database().select(table, params)

    def list_memories(self) -> list[dict[str, Any]]:
        return self._list("david_memories", order="created_at.desc")

    def create_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload)
        data.setdefault("id", str(uuid4()))
        data.setdefault("owner_id", self.owner_id)
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        data.setdefault("status", "active")
        return _first(self.require_database().insert("david_memories", data))

    def update_memory(self, memory_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        rows = self.require_database().update("david_memories", {**payload, "updated_at": _now()}, {"id": f"eq.{memory_id}"})
        return rows[0] if rows else None

    def archive_memory(self, memory_id: str) -> bool:
        return bool(self.require_database().update("david_memories", {"status": "archived", "updated_at": _now()}, {"id": f"eq.{memory_id}"}))

    def list_projects(self) -> list[dict[str, Any]]:
        return self._list("david_projects")

    def create_project(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload)
        data.setdefault("id", str(uuid4()))
        data.setdefault("owner_id", self.owner_id)
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return _first(self.require_database().insert("david_projects", data))

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        rows = self.require_database().select("david_projects", {"select": "*", "id": f"eq.{project_id}", "limit": "1"})
        return dict(rows[0]) if rows else None

    def update_project(self, project_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        rows = self.require_database().update("david_projects", {**payload, "updated_at": _now()}, {"id": f"eq.{project_id}"})
        return dict(rows[0]) if rows else None

    def delete_project(self, project_id: str) -> bool:
        return bool(self.require_database().delete("david_projects", {"id": f"eq.{project_id}"}))

    def list_tasks(self) -> list[dict[str, Any]]:
        return self._list("david_tasks")

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        rows = self.require_database().select("david_tasks", {"select": "*", "id": f"eq.{task_id}", "limit": "1"})
        return dict(rows[0]) if rows else None

    def update_task(self, task_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        rows = self.require_database().update("david_tasks", {**payload, "updated_at": _now()}, {"id": f"eq.{task_id}"})
        return dict(rows[0]) if rows else None

    def delete_task(self, task_id: str) -> bool:
        return bool(self.require_database().delete("david_tasks", {"id": f"eq.{task_id}"}))

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload)
        data.setdefault("id", str(uuid4()))
        data.setdefault("owner_id", self.owner_id)
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return _first(self.require_database().insert("david_tasks", data))

    def set_task_status(self, task_id: str, status: str) -> bool:
        return bool(self.require_database().update("david_tasks", {"status": status, "updated_at": _now()}, {"id": f"eq.{task_id}"}))

    def list_conversations(self) -> list[dict[str, Any]]:
        conversations = self._list("david_conversations", order="updated_at.desc")
        if not conversations:
            return []
        ids = [str(item.get("id")) for item in conversations if item.get("id")]
        messages = self.require_database().select(
            "david_messages",
            {"select": "*", "conversation_id": f"in.({','.join(ids)})", "order": "created_at.asc", "limit": "1000"},
        )
        grouped: dict[str, list[dict[str, Any]]] = {conversation_id: [] for conversation_id in ids}
        for message in messages:
            grouped.setdefault(str(message.get("conversation_id")), []).append(message)
        for conversation in conversations:
            conversation["messages"] = grouped.get(str(conversation.get("id")), [])
        return conversations

    def create_conversation(self, title: str) -> dict[str, Any]:
        created_at = _now()
        row = {"id": str(uuid4()), "owner_id": self.owner_id, "title": title, "created_at": created_at, "updated_at": created_at}
        return _first(self.require_database().insert("david_conversations", row))

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        self.require_database().insert(
            "david_messages",
            {"id": str(uuid4()), "conversation_id": conversation_id, "role": role, "content": content, "created_at": _now()},
        )
        self.require_database().update("david_conversations", {"updated_at": _now()}, {"id": f"eq.{conversation_id}"})

    def clear_conversation(self, conversation_id: str) -> bool:
        deleted = self.require_database().delete("david_messages", {"conversation_id": f"eq.{conversation_id}"})
        updated = self.require_database().update("david_conversations", {"updated_at": _now()}, {"id": f"eq.{conversation_id}"})
        return bool(deleted or updated)

    def delete_conversation(self, conversation_id: str) -> bool:
        return bool(self.require_database().delete("david_conversations", {"id": f"eq.{conversation_id}"}))

    def list_github_repositories(self, project_id: str | None = None) -> list[dict[str, Any]]:
        filters: dict[str, str] = {}
        if project_id:
            filters["project_id"] = f"eq.{project_id}"
        return self._list("david_github_repositories", order="created_at.desc", filters=filters)

    def get_github_repository(self, repository_id: str) -> dict[str, Any] | None:
        rows = self.require_database().select("david_github_repositories", {"select": "*", "id": f"eq.{repository_id}", "limit": "1"})
        rows = rows or []
        return dict(rows[0]) if rows else None

    def get_github_repository_by_full_name(self, repository_full_name: str) -> dict[str, Any] | None:
        rows = self.require_database().select(
            "david_github_repositories", {"select": "*", "repository_full_name": f"eq.{repository_full_name}", "limit": "1"}
        )
        rows = rows or []
        return dict(rows[0]) if rows else None

    def create_github_repository(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload)
        data.setdefault("id", str(uuid4()))
        data.setdefault("owner_id", self.owner_id)
        data.setdefault("deployment_status", "none")
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return _first(self.require_database().insert("david_github_repositories", data))

    def update_github_repository(self, repository_id: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        return self.require_database().update("david_github_repositories", {**payload, "updated_at": _now()}, {"id": f"eq.{repository_id}"})

    def create_github_audit_event(self, event: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        return _first(
            self.require_database().insert(
                "david_github_audit_log",
                {"id": str(uuid4()), "owner_id": self.owner_id, "event": event, "details": details or {}, "created_at": _now()},
            )
        )

    def list_github_audit_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._list("david_github_audit_log", order="created_at.desc", limit=min(limit, 200))

    def list_assets(self, project_id: str | None = None, kind: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        filters: dict[str, str] = {}
        if project_id:
            filters["project_id"] = f"eq.{project_id}"
        if kind:
            filters["kind"] = f"eq.{kind}"
        rows = self._list("david_assets", limit=limit, order="created_at.desc", filters=filters)
        for row in rows:
            try:
                row["signed_url"] = self.require_client().signed_url(str(row["storage_path"]), self.settings.supabase_signed_url_ttl)
            except SupabaseApiError:
                row["signed_url"] = None
        return rows

    def create_generation(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload)
        data.setdefault("id", str(uuid4()))
        data.setdefault("owner_id", self.owner_id)
        data.setdefault("created_at", _now())
        return _first(self.require_database().insert("david_generations", data))

    def list_generations(self, project_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        filters = {"project_id": f"eq.{project_id}"} if project_id else None
        return self._list("david_generations", limit=limit, order="created_at.desc", filters=filters)

    def set_favorite(self, asset_id: str, favorite: bool) -> dict[str, Any] | None:
        rows = self.require_database().update("david_assets", {"favorite": favorite, "updated_at": _now()}, {"id": f"eq.{asset_id}"})
        if rows:
            self.require_database().upsert(
                "david_favorites",
                {"owner_id": self.owner_id, "asset_id": asset_id, "created_at": _now()},
                "owner_id,asset_id",
            ) if favorite else self.require_database().delete("david_favorites", {"owner_id": f"eq.{self.owner_id}", "asset_id": f"eq.{asset_id}"})
            rows[0]["signed_url"] = self.require_client().signed_url(str(rows[0]["storage_path"]), self.settings.supabase_signed_url_ttl)
            return rows[0]
        return None

    def upload_asset(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        project_id: str | None = None,
        kind: str = "other",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        client = self.require_client()
        asset_id = str(uuid4())
        safe_name = _safe_filename(filename)
        project_segment = project_id or "unassigned"
        storage_path = f"projects/{project_segment}/{kind}/{asset_id}-{safe_name}"
        client.upload(storage_path, content, content_type or mimetypes.guess_type(safe_name)[0])
        row = {
            "id": asset_id,
            "owner_id": self.owner_id,
            "project_id": project_id,
            "filename": safe_name,
            "storage_path": storage_path,
            "content_type": content_type or "application/octet-stream",
            "size_bytes": len(content),
            "kind": kind,
            "metadata": metadata or {},
            "favorite": False,
            "created_at": _now(),
            "updated_at": _now(),
        }
        try:
            stored = _first(self.require_database().insert("david_assets", row))
        except Exception:
            logger.exception("Supabase asset metadata insert failed after upload")
            raise
        stored["signed_url"] = client.signed_url(storage_path, self.settings.supabase_signed_url_ttl)
        return stored


def get_supabase_persistence(settings: Settings) -> SupabasePersistence:
    return SupabasePersistence(settings)

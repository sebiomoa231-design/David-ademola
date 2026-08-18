from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings
from app.services.supabase_service import SupabaseNotConfigured, SupabasePersistence
from storage import JsonStorage


_STORAGE = JsonStorage()
_GOALS = "intelligence_fabric_goals"
_PLANS = "intelligence_fabric_plans"
_RUNS = "intelligence_fabric_runs"
_EVENTS = "intelligence_fabric_events"
_ATTEMPTS = "intelligence_fabric_attempts"
_ARTIFACTS = "intelligence_fabric_artifacts"
_VERIFICATIONS = "intelligence_fabric_verifications"

_REMOTE_GOALS = "david_agent_goals"
_REMOTE_PLANS = "david_agent_plans"
_REMOTE_RUNS = "david_agent_runs"
_REMOTE_ATTEMPTS = "david_agent_attempts"
_REMOTE_ARTIFACTS = "david_agent_artifacts"
_REMOTE_VERIFICATIONS = "david_agent_verifications"
_REMOTE_EVENTS = "david_agent_events"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _payload(item: Any) -> dict[str, Any]:
    if hasattr(item, "model_dump"):
        return dict(item.model_dump(mode="json"))
    return dict(item)


def _remote() -> Any | None:
    """Return the existing server-side Supabase client when persistence is enabled.

    Local JSON is intentionally retained only for developer/test deployments where
    Supabase persistence is explicitly disabled. A configured Supabase failure is
    allowed to surface instead of silently claiming a record was durable.
    """

    persistence = SupabasePersistence(get_settings())
    if not persistence.database_enabled:
        return None
    try:
        return persistence.require_database()
    except SupabaseNotConfigured:
        return None


def init_db() -> None:
    """Keep the startup contract and initialize local development fallback files."""

    for name in (_GOALS, _PLANS, _RUNS, _EVENTS, _ATTEMPTS, _ARTIFACTS, _VERIFICATIONS):
        _STORAGE.read(name, [])


def _upsert_local(name: str, item: dict[str, Any], key: str) -> None:
    items = _STORAGE.read(name, [])
    if not isinstance(items, list):
        items = []
    for index, current in enumerate(items):
        if isinstance(current, dict) and current.get(key) == item.get(key):
            items[index] = item
            _STORAGE.write(name, items)
            return
    items.append(item)
    _STORAGE.write(name, items)


def _find_local(name: str, key: str, value: str) -> dict[str, Any] | None:
    return next((item for item in _STORAGE.read(name, []) if isinstance(item, dict) and item.get(key) == value), None)


def _for_run_local(name: str, run_id: str) -> list[dict[str, Any]]:
    return [item for item in _STORAGE.read(name, []) if isinstance(item, dict) and item.get("run_id") == run_id]


def _select_one(table: str, field: str, value: str) -> tuple[bool, dict[str, Any] | None]:
    client = _remote()
    if client is None:
        return False, None
    rows = client.select(table, {"select": "*", field: f"eq.{value}", "limit": "1"})
    return True, rows[0] if rows else None


def _select_for_run(table: str, run_id: str, order: str = "created_at.asc") -> tuple[bool, list[dict[str, Any]]]:
    client = _remote()
    if client is None:
        return False, []
    return True, client.select(table, {"select": "*", "run_id": f"eq.{run_id}", "order": order, "limit": "1000"})


def _goal_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "objective": row.get("objective"),
        "project_id": row.get("project_id"),
        "context": row.get("context") or {},
        "status": row.get("status") or "created",
        "created_at": row.get("created_at"),
    }


def _run_from_row(row: dict[str, Any]) -> dict[str, Any]:
    payload = dict(row.get("payload") or {})
    for field in (
        "id", "goal_id", "status", "approved", "objective", "requested_capability",
        "selected_capability", "selected_agent", "selected_tool", "selected_provider",
        "failure_reason", "created_at", "completed_at",
    ):
        if field in row:
            payload[field] = row.get(field)
    payload.setdefault("attempts", [])
    return payload


def _attempt_from_row(row: dict[str, Any]) -> dict[str, Any]:
    payload = dict(row.get("payload") or {})
    for field in ("id", "run_id", "capability_id", "status", "created_at", "finished_at"):
        if field in row:
            payload[field] = row.get(field)
    return payload


def _artifact_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"), "run_id": row.get("run_id"), "attempt_id": row.get("attempt_id"),
        "name": row.get("name"), "kind": row.get("kind"), "uri": row.get("uri"),
        "content_type": row.get("content_type"), "checksum": row.get("checksum"),
        "metadata": row.get("metadata") or {}, "created_at": row.get("created_at"),
    }


def _verification_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"), "run_id": row.get("run_id"), "attempt_id": row.get("attempt_id"),
        "status": row.get("status"), "checks": row.get("checks") or [], "message": row.get("message"),
        "created_at": row.get("created_at"),
    }


def save_goal(goal: Any) -> None:
    payload = _payload(goal)
    client = _remote()
    if client is None:
        _upsert_local(_GOALS, payload, "id")
        return
    client.upsert(_REMOTE_GOALS, {
        "id": payload["id"], "owner_id": "default-owner", "title": payload["title"],
        "objective": payload["objective"], "project_id": payload.get("project_id"),
        "context": payload.get("context") or {}, "status": payload.get("status") or "created",
        "created_at": payload.get("created_at") or _now(),
    }, "id")


def get_goal(goal_id: str) -> dict[str, Any] | None:
    remote_active, row = _select_one(_REMOTE_GOALS, "id", goal_id)
    return _goal_from_row(row) if row else (None if remote_active else _find_local(_GOALS, "id", goal_id))


def save_plan(plan: Any) -> None:
    payload = _payload(plan)
    client = _remote()
    if client is None:
        _upsert_local(_PLANS, {"goal_id": plan.goal_id, "plan": payload, "created_at": _now()}, "goal_id")
        return
    client.upsert(_REMOTE_PLANS, {"goal_id": payload["goal_id"], "plan": payload, "created_at": payload.get("generated_at") or _now()}, "goal_id")


def get_plan(goal_id: str) -> dict[str, Any] | None:
    remote_active, row = _select_one(_REMOTE_PLANS, "goal_id", goal_id)
    return dict(row.get("plan") or {}) if row else (None if remote_active else ((_find_local(_PLANS, "goal_id", goal_id) or {}).get("plan")))


def save_run(run: Any) -> None:
    payload = _payload(run)
    client = _remote()
    if client is None:
        _upsert_local(_RUNS, payload, "id")
        return
    client.upsert(_REMOTE_RUNS, {
        "id": payload["id"], "owner_id": "default-owner", "goal_id": payload["goal_id"],
        "status": payload.get("status") or "queued", "approved": bool(payload.get("approved")),
        "objective": payload.get("objective"), "requested_capability": payload.get("requested_capability"),
        "selected_capability": payload.get("selected_capability"), "selected_agent": payload.get("selected_agent"),
        "selected_tool": payload.get("selected_tool"), "selected_provider": payload.get("selected_provider"),
        "failure_reason": payload.get("failure_reason"), "payload": payload,
        "created_at": payload.get("created_at") or _now(), "completed_at": payload.get("completed_at"),
    }, "id")


def update_run(run_id: str, **changes: Any) -> dict[str, Any] | None:
    run = get_run(run_id)
    if not run:
        return None
    run.update(changes)
    save_run(run)
    return run


def get_run(run_id: str) -> dict[str, Any] | None:
    remote_active, row = _select_one(_REMOTE_RUNS, "id", run_id)
    return _run_from_row(row) if row else (None if remote_active else _find_local(_RUNS, "id", run_id))


def save_attempt(attempt: Any) -> None:
    payload = _payload(attempt)
    client = _remote()
    if client is None:
        _upsert_local(_ATTEMPTS, payload, "id")
        return
    client.upsert(_REMOTE_ATTEMPTS, {
        "id": payload["id"], "run_id": payload["run_id"], "capability_id": payload["capability_id"],
        "status": payload.get("status") or "queued", "payload": payload,
        "created_at": payload.get("created_at") or _now(), "finished_at": payload.get("finished_at"),
    }, "id")


def get_attempt(attempt_id: str) -> dict[str, Any] | None:
    remote_active, row = _select_one(_REMOTE_ATTEMPTS, "id", attempt_id)
    return _attempt_from_row(row) if row else (None if remote_active else _find_local(_ATTEMPTS, "id", attempt_id))


def get_attempts(run_id: str) -> list[dict[str, Any]]:
    remote_active, rows = _select_for_run(_REMOTE_ATTEMPTS, run_id)
    return [_attempt_from_row(row) for row in rows] if remote_active else _for_run_local(_ATTEMPTS, run_id)


def save_artifact(artifact: Any) -> None:
    payload = _payload(artifact)
    client = _remote()
    if client is None:
        _upsert_local(_ARTIFACTS, payload, "id")
        return
    client.upsert(_REMOTE_ARTIFACTS, {
        "id": payload["id"], "run_id": payload["run_id"], "attempt_id": payload.get("attempt_id"),
        "name": payload["name"], "kind": payload["kind"], "uri": payload.get("uri"),
        "content_type": payload.get("content_type"), "checksum": payload.get("checksum"),
        "metadata": payload.get("metadata") or {}, "created_at": payload.get("created_at") or _now(),
    }, "id")


def get_artifacts(run_id: str) -> list[dict[str, Any]]:
    remote_active, rows = _select_for_run(_REMOTE_ARTIFACTS, run_id)
    return [_artifact_from_row(row) for row in rows] if remote_active else _for_run_local(_ARTIFACTS, run_id)


def save_verification(verification: Any) -> None:
    payload = _payload(verification)
    client = _remote()
    if client is None:
        _upsert_local(_VERIFICATIONS, payload, "id")
        return
    client.upsert(_REMOTE_VERIFICATIONS, {
        "id": payload["id"], "run_id": payload["run_id"], "attempt_id": payload.get("attempt_id"),
        "status": payload.get("status") or "pending", "checks": payload.get("checks") or [],
        "message": payload.get("message"), "created_at": payload.get("created_at") or _now(),
    }, "id")


def get_verification(run_id: str) -> dict[str, Any] | None:
    remote_active, rows = _select_for_run(_REMOTE_VERIFICATIONS, run_id, "created_at.desc")
    if remote_active:
        return _verification_from_row(rows[0]) if rows else None
    local_records = _for_run_local(_VERIFICATIONS, run_id)
    return local_records[-1] if local_records else None


def add_event(run_id: str, event_type: str, payload: dict[str, Any]) -> None:
    client = _remote()
    event = {"run_id": run_id, "event_type": event_type, "payload": payload, "created_at": _now()}
    if client is None:
        events = _STORAGE.read(_EVENTS, [])
        if not isinstance(events, list):
            events = []
        event["id"] = len(events) + 1
        events.append(event)
        _STORAGE.write(_EVENTS, events)
        return
    client.insert(_REMOTE_EVENTS, event)


def get_events(run_id: str) -> list[dict[str, Any]]:
    remote_active, rows = _select_for_run(_REMOTE_EVENTS, run_id)
    if not remote_active:
        return _for_run_local(_EVENTS, run_id)
    return [{"id": row.get("id"), "run_id": row.get("run_id"), "event_type": row.get("event_type"), "payload": row.get("payload") or {}, "created_at": row.get("created_at")} for row in rows]

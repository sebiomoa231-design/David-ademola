from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from storage import JsonStorage


_STORAGE = JsonStorage()
_GOALS = "intelligence_fabric_goals"
_PLANS = "intelligence_fabric_plans"
_RUNS = "intelligence_fabric_runs"
_EVENTS = "intelligence_fabric_events"
_ATTEMPTS = "intelligence_fabric_attempts"
_ARTIFACTS = "intelligence_fabric_artifacts"
_VERIFICATIONS = "intelligence_fabric_verifications"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    """Keep the upstream startup contract without creating a second database."""

    for name in (
        _GOALS,
        _PLANS,
        _RUNS,
        _EVENTS,
        _ATTEMPTS,
        _ARTIFACTS,
        _VERIFICATIONS,
    ):
        _STORAGE.read(name, [])


def _upsert(name: str, item: dict[str, Any], key: str) -> None:
    items = _STORAGE.read(name, [])
    if not isinstance(items, list):
        items = []
    replaced = False
    for index, current in enumerate(items):
        if isinstance(current, dict) and current.get(key) == item.get(key):
            items[index] = item
            replaced = True
            break
    if not replaced:
        items.append(item)
    _STORAGE.write(name, items)


def _find(name: str, key: str, value: str) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in _STORAGE.read(name, [])
            if isinstance(item, dict) and item.get(key) == value
        ),
        None,
    )


def _for_run(name: str, run_id: str) -> list[dict[str, Any]]:
    return [
        item
        for item in _STORAGE.read(name, [])
        if isinstance(item, dict) and item.get("run_id") == run_id
    ]


def save_goal(goal: Any) -> None:
    _upsert(_GOALS, goal.model_dump(mode="json"), "id")


def get_goal(goal_id: str) -> dict[str, Any] | None:
    return _find(_GOALS, "id", goal_id)


def save_plan(plan: Any) -> None:
    _upsert(
        _PLANS,
        {"goal_id": plan.goal_id, "plan": plan.model_dump(mode="json"), "created_at": _now()},
        "goal_id",
    )


def get_plan(goal_id: str) -> dict[str, Any] | None:
    record = _find(_PLANS, "goal_id", goal_id)
    return record.get("plan") if record else None


def save_run(run: Any) -> None:
    payload = run.model_dump(mode="json") if hasattr(run, "model_dump") else dict(run)
    _upsert(_RUNS, payload, "id")


def update_run(run_id: str, **changes: Any) -> dict[str, Any] | None:
    run = get_run(run_id)
    if not run:
        return None
    run.update(changes)
    save_run(run)
    return run


def get_run(run_id: str) -> dict[str, Any] | None:
    return _find(_RUNS, "id", run_id)


def save_attempt(attempt: Any) -> None:
    payload = attempt.model_dump(mode="json") if hasattr(attempt, "model_dump") else dict(attempt)
    _upsert(_ATTEMPTS, payload, "id")


def get_attempt(attempt_id: str) -> dict[str, Any] | None:
    return _find(_ATTEMPTS, "id", attempt_id)


def get_attempts(run_id: str) -> list[dict[str, Any]]:
    return _for_run(_ATTEMPTS, run_id)


def save_artifact(artifact: Any) -> None:
    payload = artifact.model_dump(mode="json") if hasattr(artifact, "model_dump") else dict(artifact)
    _upsert(_ARTIFACTS, payload, "id")


def get_artifacts(run_id: str) -> list[dict[str, Any]]:
    return _for_run(_ARTIFACTS, run_id)


def save_verification(verification: Any) -> None:
    payload = verification.model_dump(mode="json") if hasattr(verification, "model_dump") else dict(verification)
    _upsert(_VERIFICATIONS, payload, "id")


def get_verification(run_id: str) -> dict[str, Any] | None:
    records = _for_run(_VERIFICATIONS, run_id)
    return records[-1] if records else None


def add_event(run_id: str, event_type: str, payload: dict[str, Any]) -> None:
    events = _STORAGE.read(_EVENTS, [])
    if not isinstance(events, list):
        events = []
    events.append(
        {
            "id": len(events) + 1,
            "run_id": run_id,
            "event_type": event_type,
            "payload": payload,
            "created_at": _now(),
        }
    )
    _STORAGE.write(_EVENTS, events)


def get_events(run_id: str) -> list[dict[str, Any]]:
    return [
        item
        for item in _STORAGE.read(_EVENTS, [])
        if isinstance(item, dict) and item.get("run_id") == run_id
    ]

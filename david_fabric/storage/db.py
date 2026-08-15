from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from storage import JsonStorage


_STORAGE = JsonStorage()
_GOALS = "intelligence_fabric_goals"
_PLANS = "intelligence_fabric_plans"
_RUNS = "intelligence_fabric_runs"
_EVENTS = "intelligence_fabric_events"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    """Keep the upstream startup contract without creating a second database."""

    for name in (_GOALS, _PLANS, _RUNS, _EVENTS):
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


def save_goal(goal: Any) -> None:
    _upsert(_GOALS, goal.model_dump(mode="json"), "id")


def get_goal(goal_id: str) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in _STORAGE.read(_GOALS, [])
            if isinstance(item, dict) and item.get("id") == goal_id
        ),
        None,
    )


def save_plan(plan: Any) -> None:
    _upsert(
        _PLANS,
        {"goal_id": plan.goal_id, "plan": plan.model_dump(mode="json"), "created_at": _now()},
        "goal_id",
    )


def get_plan(goal_id: str) -> dict[str, Any] | None:
    record = next(
        (
            item
            for item in _STORAGE.read(_PLANS, [])
            if isinstance(item, dict) and item.get("goal_id") == goal_id
        ),
        None,
    )
    return record.get("plan") if record else None


def save_run(run: Any) -> None:
    _upsert(_RUNS, run.model_dump(mode="json"), "id")


def get_run(run_id: str) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in _STORAGE.read(_RUNS, [])
            if isinstance(item, dict) and item.get("id") == run_id
        ),
        None,
    )


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

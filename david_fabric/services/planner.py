from __future__ import annotations

from typing import Any

from david_fabric.core.models import Goal, GoalPlan, PlanStep
from david_fabric.services.registry import get_capability, match_capabilities


DEFAULT_CAPABILITY_ID = "david-core"


def _requires_approval(item: dict[str, Any]) -> bool:
    return bool(item.get("requires_approval", False)) or bool(
        set(item.get("permissions", [])) & {"external_write", "deploy", "publish", "delete", "purchase", "webhook"}
    )


def create_plan(goal: Goal, health: dict[str, Any] | None = None) -> GoalPlan:
    matches = match_capabilities(
        f"{goal.title} {goal.objective}",
        requested_capability=goal.context.get("requested_capability"),
        health=health,
    )
    if not matches:
        selected = get_capability(DEFAULT_CAPABILITY_ID) or {
            "id": DEFAULT_CAPABILITY_ID,
            "name": "David Core",
            "state": "READY",
            "available": True,
        }
        matches = [selected]

    # Keep the original multi-step behavior for compound goals. The first step
    # is the preferred route; all other matched steps remain explicit options
    # and are also available as fallback candidates at execution time.
    selected_matches = matches[:6]
    primary = selected_matches[0]
    primary_fallbacks = list(primary.get("fallback_capabilities", []))
    for candidate in selected_matches[1:]:
        candidate_id = str(candidate.get("id"))
        if candidate_id not in primary_fallbacks and candidate_id != primary.get("id"):
            primary_fallbacks.append(candidate_id)

    steps: list[PlanStep] = []
    previous_id: str | None = None
    for index, item in enumerate(selected_matches):
        fallback_ids = primary_fallbacks if index == 0 else list(item.get("fallback_capabilities", []))
        step = PlanStep(
            title=f"{item.get('name', item['id'])} for goal",
            capability=str(item["id"]),
            depends_on=[previous_id] if previous_id else [],
            requires_approval=_requires_approval(item),
            agent=item.get("agent"),
            skill=item.get("skill"),
            tool=item.get("tool"),
            provider=item.get("provider"),
            adapter=item.get("adapter"),
            fallback_capabilities=fallback_ids,
            inputs=list(item.get("inputs", [])),
            outputs=list(item.get("outputs", [])),
            readiness=list(item.get("readiness", [])),
            metadata={
                "category": item.get("category"),
                "mode": item.get("mode"),
                "source": item.get("source"),
                "state": item.get("state"),
                "available": item.get("available"),
                "reason": item.get("reason"),
                "permissions": item.get("permissions", []),
                "preferred": index == 0,
                "fallback_chain": fallback_ids,
            },
        )
        steps.append(step)
        previous_id = step.id

    return GoalPlan(goal_id=goal.id, steps=steps)

from __future__ import annotations

from typing import Any

import yaml
from fastapi import APIRouter, HTTPException, Query

from david_fabric.core.models import (
    CapabilitySelectionRequest,
    CapabilitySelectionResponse,
    ExecutionRequest,
    Goal,
    GoalCreate,
    GoalPlan,
    GovernedRequest,
    GovernedRequestResponse,
    Run,
    RunCreate,
    RunResult,
)
from david_fabric.services.adapters import list_adapters
from david_fabric.services.execution import execute_goal
from david_fabric.services.health import fabric_readiness, service_health
from david_fabric.services.planner import create_plan
from david_fabric.services.policy import authorize, policy_snapshot
from david_fabric.services.registry import (
    get_capability,
    list_enriched_capabilities,
    load_capabilities,
    match_capabilities,
    registry_discovery_report,
)
from david_fabric.storage import db
from david_fabric.core.config import PROJECT_ROOT


fabric_router = APIRouter(prefix="/intelligence", tags=["intelligence-fabric"])


def _directory(kind: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in list_enriched_capabilities():
        value = item.get(kind)
        if not value or value in seen:
            continue
        seen.add(str(value))
        items.append(
            {
                "id": value,
                "capabilities": [candidate["id"] for candidate in list_enriched_capabilities() if candidate.get(kind) == value],
                "state": item.get("state"),
                "readiness": item.get("readiness", []),
            }
        )
    return items


async def _select_capability(payload: CapabilitySelectionRequest) -> CapabilitySelectionResponse:
    health = await service_health()
    candidates = match_capabilities(
        payload.objective,
        requested_capability=payload.requested_capability,
        health=health,
    )
    typed = []
    for candidate in candidates:
        typed.append(
            {
                "capability_id": candidate["id"],
                "name": candidate.get("name", candidate["id"]),
                "category": candidate.get("category"),
                "score": sum(
                    1
                    for keyword in candidate.get("keywords", [])
                    if str(keyword).casefold() in payload.objective.casefold()
                ),
                "agent": candidate.get("agent"),
                "skill": candidate.get("skill"),
                "tool": candidate.get("tool"),
                "provider": candidate.get("provider"),
                "adapter": candidate.get("adapter"),
                "mode": candidate.get("mode"),
                "readiness": candidate.get("readiness", []),
                "state": candidate.get("state", "UNAVAILABLE"),
                "available": bool(candidate.get("available")),
                "reason": candidate.get("reason"),
                "fallback_capabilities": candidate.get("fallback_capabilities", []),
            }
        )
    selected = next((item for item in typed if item["available"]), typed[0] if typed else None)
    fallback_chain = []
    if selected:
        fallback_chain = list(selected.get("fallback_capabilities", []))
        fallback_chain.extend(
            item["capability_id"]
            for item in typed
            if item["capability_id"] != selected["capability_id"] and item["capability_id"] not in fallback_chain
        )
    return CapabilitySelectionResponse(
        objective=payload.objective,
        candidates=typed,
        selected=selected,
        fallback_chain=fallback_chain,
    )


@fabric_router.get("/health")
async def intelligence_health() -> dict[str, object]:
    return {
        "status": "ok",
        "component": "david-ai-intelligence-fabric",
        "services": await service_health(),
    }


@fabric_router.get("/readiness")
async def readiness() -> dict[str, Any]:
    return await fabric_readiness()


@fabric_router.get("/capabilities")
def capabilities() -> dict[str, object]:
    return {"capabilities": list_enriched_capabilities()}


@fabric_router.get("/capabilities/discovery")
def capability_discovery() -> dict[str, object]:
    """Return safe manifest-discovery provenance; discovery never executes repo code."""

    return registry_discovery_report()


@fabric_router.get("/capabilities/{capability_id}")
def capability(capability_id: str) -> dict[str, object]:
    item = get_capability(capability_id)
    if not item:
        raise HTTPException(status_code=404, detail="Capability not found")
    return next(
        candidate
        for candidate in list_enriched_capabilities()
        if candidate.get("id") == capability_id
    )


@fabric_router.get("/adapters")
def adapters() -> dict[str, object]:
    return {"adapters": list_adapters()}


@fabric_router.get("/agents")
def agents() -> dict[str, object]:
    return {"agents": _directory("agent")}


@fabric_router.get("/tools")
def tools() -> dict[str, object]:
    return {"tools": _directory("tool")}


@fabric_router.get("/providers")
def providers() -> dict[str, object]:
    return {"providers": _directory("provider")}


@fabric_router.get("/workflows")
def workflows() -> dict[str, object]:
    path = PROJECT_ROOT / "config" / "workflows.yaml"
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {"workflows": {}}


@fabric_router.get("/policies")
def policies() -> dict[str, Any]:
    return policy_snapshot()


@fabric_router.post("/route", response_model=CapabilitySelectionResponse)
async def route_capability(payload: CapabilitySelectionRequest) -> CapabilitySelectionResponse:
    return await _select_capability(payload)


@fabric_router.post("/requests", response_model=GovernedRequestResponse)
async def create_governed_request(payload: GovernedRequest) -> GovernedRequestResponse:
    """Route every natural-language request through a saved goal and plan first.

    `execute` is deliberately false by default. The execution layer remains the
    only path that can invoke adapters and it enforces capability approvals.
    """

    route = await _select_capability(
        CapabilitySelectionRequest(
            objective=payload.objective,
            requested_capability=payload.requested_capability,
            context=payload.context,
        )
    )
    selected = route.selected
    if not selected:
        return GovernedRequestResponse(status="unmatched", route=route)

    goal = Goal(
        title=payload.title or payload.objective[:160],
        objective=payload.objective,
        context={
            **payload.context,
            "requested_capability": selected.capability_id,
            "selection_source": "governed-request",
        },
    )
    db.save_goal(goal)
    db.add_event(
        goal.id,
        "goal_created_from_request",
        {"selected_capability": selected.capability_id, "available": selected.available},
    )
    plan = create_plan(goal)
    db.save_plan(plan)
    db.add_event(goal.id, "plan_created", {"steps": [step.capability for step in plan.steps]})

    if not payload.execute:
        return GovernedRequestResponse(status="planned", route=route, goal=goal, plan=plan)
    if not selected.available:
        return GovernedRequestResponse(status="unavailable", route=route, goal=goal, plan=plan)

    run = Run(
        goal_id=goal.id,
        approved=payload.approved,
        objective=goal.objective,
        requested_capability=selected.capability_id,
    )
    db.save_run(run)
    db.add_event(run.id, "run_created_from_request", {"goal_id": goal.id})
    result = await execute_goal(goal, run, plan, input_data=payload.input)
    return GovernedRequestResponse(
        status=result.run.status,
        route=route,
        goal=goal,
        plan=plan,
        run=result.run,
        result=result,
    )


@fabric_router.post("/goals", response_model=Goal)
def create_goal(payload: GoalCreate) -> Goal:
    goal = Goal(**payload.model_dump())
    db.save_goal(goal)
    db.add_event(goal.id, "goal_created", {"objective": goal.objective})
    return goal


@fabric_router.post("/goals/{goal_id}/plan", response_model=GoalPlan)
def plan_goal(goal_id: str) -> GoalPlan:
    row = db.get_goal(goal_id)
    if not row:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal = Goal(**row)
    plan = create_plan(goal)
    db.save_plan(plan)
    db.add_event(goal_id, "plan_created", {"steps": [step.capability for step in plan.steps]})
    return plan


@fabric_router.get("/goals/{goal_id}/plan", response_model=GoalPlan)
def get_goal_plan(goal_id: str) -> GoalPlan:
    plan = db.get_plan(goal_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return GoalPlan(**plan)


@fabric_router.post("/runs", response_model=Run)
def create_run(payload: RunCreate) -> Run:
    goal_row = db.get_goal(payload.goal_id)
    if not goal_row:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal = Goal(**goal_row)
    run = Run(
        goal_id=payload.goal_id,
        approved=payload.approved,
        objective=payload.objective or goal.objective,
        requested_capability=payload.requested_capability,
    )
    db.save_run(run)
    db.add_event(run.id, "run_created", {"goal_id": run.goal_id, "objective": run.objective})
    return run


@fabric_router.post("/runs/{run_id}/authorize")
def authorize_run(
    run_id: str,
    capability: str = Query(..., min_length=1),
) -> dict[str, object]:
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    allowed, reason = authorize(capability, approved=True)
    if not allowed:
        raise HTTPException(status_code=403, detail=reason)
    db.update_run(run_id, approved=True)
    db.add_event(run_id, "approval_granted", {"capability": capability})
    return {"allowed": True, "capability": capability}


@fabric_router.post("/runs/{run_id}/execute", response_model=RunResult)
async def execute_run(run_id: str, payload: ExecutionRequest | None = None) -> RunResult:
    row = db.get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    run = Run(**row)
    goal_row = db.get_goal(run.goal_id)
    if not goal_row:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal = Goal(**goal_row)
    if payload:
        if payload.approved:
            run.approved = True
        if payload.objective:
            run.objective = payload.objective
        if payload.requested_capability:
            run.requested_capability = payload.requested_capability
        db.save_run(run)
    if run.objective:
        goal.objective = run.objective
    if run.requested_capability:
        goal.context = {**goal.context, "requested_capability": run.requested_capability}
    plan_row = db.get_plan(goal.id)
    plan = GoalPlan(**plan_row) if plan_row else create_plan(goal)
    if not plan_row:
        db.save_plan(plan)
    return await execute_goal(goal, run, plan, input_data=payload.input if payload else {})


@fabric_router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, object]:
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run": run,
        "events": db.get_events(run_id),
        "attempts": db.get_attempts(run_id),
        "artifacts": db.get_artifacts(run_id),
        "verification": db.get_verification(run_id),
    }


@fabric_router.get("/runs/{run_id}/artifacts")
def get_run_artifacts(run_id: str) -> dict[str, object]:
    if not db.get_run(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    return {"artifacts": db.get_artifacts(run_id)}


@fabric_router.get("/runs/{run_id}/verification")
def get_run_verification(run_id: str) -> dict[str, object]:
    if not db.get_run(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    return {"verification": db.get_verification(run_id)}


# Upstream Core Fabric compatibility name. David mounts ``fabric_router``
# under the existing ``/api`` router, while standalone imports can keep using
# the original symbol.
api_router = fabric_router

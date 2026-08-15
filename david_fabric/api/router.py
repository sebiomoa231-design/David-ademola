from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from david_fabric.core.models import Goal, GoalCreate, GoalPlan, Run, RunCreate
from david_fabric.services.adapters import list_adapters
from david_fabric.services.health import service_health
from david_fabric.services.planner import create_plan
from david_fabric.services.policy import authorize
from david_fabric.services.registry import get_capability, load_capabilities
from david_fabric.storage import db


fabric_router = APIRouter(prefix="/intelligence", tags=["intelligence-fabric"])


@fabric_router.get("/health")
async def intelligence_health() -> dict[str, object]:
    return {
        "status": "ok",
        "component": "david-ai-intelligence-fabric",
        "services": await service_health(),
    }


@fabric_router.get("/capabilities")
def capabilities() -> dict[str, object]:
    return {"capabilities": load_capabilities()}


@fabric_router.get("/capabilities/{capability_id}")
def capability(capability_id: str) -> dict[str, object]:
    item = get_capability(capability_id)
    if not item:
        raise HTTPException(status_code=404, detail="Capability not found")
    return item


@fabric_router.get("/adapters")
def adapters() -> dict[str, object]:
    return {"adapters": list_adapters()}


@fabric_router.post("/goals", response_model=Goal)
def create_goal(payload: GoalCreate) -> Goal:
    goal = Goal(**payload.model_dump())
    db.save_goal(goal)
    return goal


@fabric_router.post("/goals/{goal_id}/plan", response_model=GoalPlan)
def plan_goal(goal_id: str) -> GoalPlan:
    row = db.get_goal(goal_id)
    if not row:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal = Goal(**row)
    plan = create_plan(goal)
    db.save_plan(plan)
    return plan


@fabric_router.get("/goals/{goal_id}/plan", response_model=GoalPlan)
def get_goal_plan(goal_id: str) -> GoalPlan:
    plan = db.get_plan(goal_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return GoalPlan(**plan)


@fabric_router.post("/runs", response_model=Run)
def create_run(payload: RunCreate) -> Run:
    if not db.get_goal(payload.goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    run = Run(goal_id=payload.goal_id, approved=payload.approved)
    db.save_run(run)
    db.add_event(run.id, "run_created", {"goal_id": run.goal_id})
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
    db.add_event(run_id, "approval_granted", {"capability": capability})
    return {"allowed": True, "capability": capability}


@fabric_router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, object]:
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run": run, "events": db.get_events(run_id)}


# Upstream Core Fabric compatibility name. David mounts ``fabric_router``
# under the existing ``/api`` router, while standalone imports can keep using
# the original symbol.
api_router = fabric_router

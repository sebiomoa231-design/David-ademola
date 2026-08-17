"""HTTP contract for David AI's governed operating system."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from david_fabric.services.operating_system import (
    OperatingSystemError,
    PolicyBlocked,
    OwnerApprovalRequired,
    get_operating_system,
)


router = APIRouter()


def _os():
    return get_operating_system()


def _call(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except OperatingSystemError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "invalid_request", "message": str(exc)}) from exc


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    action: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    project_id: str | None = None
    objective_id: str | None = None
    due_at: str | None = None
    max_retries: int = Field(default=3, ge=0, le=10)
    risk: str = Field(default="low", pattern="^(low|medium|high|critical)$")
    actor: str = "owner"
    approved: bool = False


class TaskCheckpointRequest(BaseModel):
    checkpoint: dict[str, Any]
    actor: str = "owner"


class ActionRequest(BaseModel):
    actor: str = "owner"
    approved: bool = False
    reason: str | None = None


class ObjectiveCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=5000)
    priority: int = Field(default=50, ge=0, le=100)
    resources: list[str] = Field(default_factory=list)
    deadline: str | None = None
    actor: str = "owner"
    approved: bool = False


class MilestoneCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    due_at: str | None = None


class WorkflowCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    steps: list[dict[str, Any]] = Field(min_length=1, max_length=30)
    version: int = Field(default=1, ge=1)
    owner_approval: bool = True
    actor: str = "owner"
    approved: bool = False


class ScheduleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    action: str = Field(min_length=1, max_length=120)
    interval_seconds: int | None = Field(default=None, ge=1, le=31_536_000)
    cron: str | None = None
    enabled: bool = True
    actor: str = "owner"
    approved: bool = False


class AgentDispatchRequest(BaseModel):
    action: str = Field(min_length=1, max_length=160)
    payload: dict[str, Any] = Field(default_factory=dict)
    actor: str = "owner"
    approved: bool = False
    chain: list[str] = Field(default_factory=list)
    max_calls: int = Field(default=8, ge=1, le=32)
    max_depth: int = Field(default=4, ge=1, le=12)


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    sources: list[dict[str, Any]] = Field(default_factory=list, max_length=50)
    findings: list[str] = Field(default_factory=list, max_length=100)
    confidence: float | None = Field(default=None, ge=0, le=1)
    license_notes: list[str] = Field(default_factory=list, max_length=50)
    actor: str = "owner"


class CapabilityGapRequest(BaseModel):
    capability: str = Field(min_length=1, max_length=160)
    evidence: dict[str, Any] = Field(default_factory=dict)
    severity: str = "medium"
    actor: str = "david"


class EvolutionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    problem: str = Field(min_length=1, max_length=5000)
    scope: list[str] = Field(default_factory=list, max_length=50)
    risk: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    actor: str = "owner"


class EvolutionTransitionRequest(BaseModel):
    state: str = Field(min_length=1, max_length=40)
    actor: str = "owner"
    approved: bool = False
    evidence: dict[str, Any] = Field(default_factory=dict)


class MemoryContextRequest(BaseModel):
    query: str = Field(default="", max_length=5000)
    project_id: str | None = None
    task_id: str | None = None
    limit: int = Field(default=8, ge=1, le=20)


class SystemModeRequest(BaseModel):
    actor: str = "owner"
    approved: bool = False


@router.get("/system/health")
def system_health() -> dict[str, Any]:
    return _os().health()


@router.get("/system/status")
def system_status() -> dict[str, Any]:
    return _os().status()


@router.post("/system/stop")
def system_stop(request: SystemModeRequest) -> dict[str, Any]:
    decision = _call(_os().policy.set_emergency_stop, True, actor=request.actor, approved=request.approved)
    return {"decision": decision.as_dict()}


@router.post("/system/resume")
def system_resume(request: SystemModeRequest) -> dict[str, Any]:
    decision = _call(_os().policy.set_emergency_stop, False, actor=request.actor, approved=request.approved)
    return {"decision": decision.as_dict()}


@router.post("/system/autonomous-mode")
def autonomous_mode(enabled: bool, request: SystemModeRequest) -> dict[str, Any]:
    decision = _call(_os().policy.set_autonomous_mode, enabled, actor=request.actor, approved=request.approved)
    return {"decision": decision.as_dict(), "enabled": enabled if decision.allowed else False}


@router.post("/system/proactive-scan")
def proactive_scan() -> dict[str, Any]:
    return {"signals": _os().proactive_scan()}


@router.post("/system/resources/observe")
def observe_resources(task_id: str | None = None) -> dict[str, Any]:
    return _os().resources.observe(task_id=task_id)


@router.get("/system/events")
def system_events(event_type: str | None = None, limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
    return {"events": _os().store.events(event_type=event_type, limit=limit)}


@router.get("/system/audit")
def system_audit(limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
    return {"audit": _os().store.audits(limit)}


@router.get("/tasks")
def list_tasks(status: str | None = None, limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().tasks.list(status=status, limit=limit)


@router.post("/tasks")
def create_task(request: TaskCreateRequest) -> dict[str, Any]:
    return _call(_os().tasks.create, **request.model_dump())


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, Any]:
    task = _os().tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Task not found"})
    return task


@router.post("/tasks/{task_id}/run")
def run_task(task_id: str, request: ActionRequest) -> dict[str, Any]:
    return _call(_os().run_task, task_id, actor=request.actor, approved=request.approved)


@router.post("/tasks/{task_id}/pause")
def pause_task(task_id: str, request: ActionRequest) -> dict[str, Any]:
    return _call(_os().tasks.transition, task_id, "PAUSED", actor=request.actor, approved=request.approved, reason=request.reason)


@router.post("/tasks/{task_id}/resume")
def resume_task(task_id: str, request: ActionRequest) -> dict[str, Any]:
    return _call(_os().tasks.transition, task_id, "QUEUED", actor=request.actor, approved=request.approved, reason=request.reason)


@router.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str, request: ActionRequest) -> dict[str, Any]:
    return _call(_os().tasks.transition, task_id, "CANCELLED", actor=request.actor, approved=request.approved, reason=request.reason)


@router.post("/tasks/{task_id}/checkpoint")
def checkpoint_task(task_id: str, request: TaskCheckpointRequest) -> dict[str, Any]:
    return _call(_os().tasks.checkpoint, task_id, request.checkpoint, actor=request.actor)


@router.get("/objectives")
def list_objectives() -> list[dict[str, Any]]:
    return _os().objectives.list()


@router.post("/objectives")
def create_objective(request: ObjectiveCreateRequest) -> dict[str, Any]:
    return _call(_os().objectives.create, **request.model_dump())


@router.post("/objectives/{objective_id}/milestones")
def create_milestone(objective_id: str, request: MilestoneCreateRequest) -> dict[str, Any]:
    return _call(_os().objectives.milestone, objective_id, request.title, due_at=request.due_at)


@router.get("/objectives/conflicts")
def objective_conflicts(resources: str = "") -> dict[str, Any]:
    values = [item.strip() for item in resources.split(",") if item.strip()]
    return {"resources": values, "conflicts": _os().objectives.conflicts(values)}


@router.get("/agents/registry")
def agents() -> list[dict[str, Any]]:
    return _os().agents.list()


@router.get("/agents/{agent_id}")
def get_agent(agent_id: str) -> dict[str, Any]:
    agent = _os().agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail={"code": "agent_not_found", "message": "Agent not found"})
    return agent


@router.post("/agents/{agent_id}/dispatch")
def dispatch_agent(agent_id: str, request: AgentDispatchRequest) -> dict[str, Any]:
    return _call(_os().agents.dispatch, agent_id, request.action, request.payload, lambda action, payload: _os().execute(action, payload), actor=request.actor, approved=request.approved, chain=request.chain, max_calls=request.max_calls, max_depth=request.max_depth)


@router.get("/agent-runs")
def list_agent_runs(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().store.list("agent_run", limit=limit)


@router.get("/workflows")
def list_workflows() -> list[dict[str, Any]]:
    return _os().workflows.list()


@router.post("/workflows")
def create_workflow(request: WorkflowCreateRequest) -> dict[str, Any]:
    return _call(_os().workflows.create, **request.model_dump())


@router.post("/workflows/{workflow_id}/run")
def run_workflow(workflow_id: str, request: ActionRequest) -> dict[str, Any]:
    return _call(_os().workflows.run, workflow_id, _os().tasks.create, actor=request.actor, approved=request.approved)


@router.get("/schedules")
def list_schedules() -> list[dict[str, Any]]:
    return _os().scheduler.list()


@router.post("/schedules")
def create_schedule(request: ScheduleCreateRequest) -> dict[str, Any]:
    return _call(_os().scheduler.create, **request.model_dump())


@router.get("/events")
def list_events(event_type: str | None = None, limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().store.events(event_type=event_type, limit=limit)


@router.get("/notifications")
def list_notifications(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().notifications.notifications(limit)


@router.get("/signals")
def list_signals(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().notifications.signals(limit)


@router.get("/projects/{project_id}/health")
def project_health(project_id: str) -> dict[str, Any]:
    return _os().project_health(project_id)


@router.post("/memory/context")
def memory_context(request: MemoryContextRequest) -> dict[str, Any]:
    return _os().context(request.query, project_id=request.project_id, task_id=request.task_id, limit=request.limit)


@router.get("/research")
def list_research(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().research.list(limit)


@router.post("/research")
def record_research(request: ResearchRequest) -> dict[str, Any]:
    return _call(_os().research.record, **request.model_dump())


@router.post("/capability-gaps")
def record_capability_gap(request: CapabilityGapRequest) -> dict[str, Any]:
    return _call(_os().research.gap, **request.model_dump())


@router.get("/capability-gaps")
def list_capability_gaps(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().store.list("capability_gap", limit=limit)


@router.get("/capabilities/registry")
def capability_registry() -> dict[str, Any]:
    rows = _os().providers.list()
    capabilities = sorted({capability for row in rows for capability in row.get("capabilities", [])})
    return {"providers": rows, "capabilities": capabilities, "gaps": _os().store.list("capability_gap", status="OPEN", limit=100)}


@router.get("/providers/{provider_id}/health")
def provider_health(provider_id: str) -> dict[str, Any]:
    provider = _os().providers.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail={"code": "provider_not_found", "message": "Provider not found"})
    rows = [row for row in _os().providers.list() if row.get("id") == provider_id]
    return rows[0] if rows else {"id": provider_id, "status": "unknown"}


@router.get("/evolutions")
def list_evolutions(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().evolutions.list(limit)


@router.post("/evolutions")
def create_evolution(request: EvolutionCreateRequest) -> dict[str, Any]:
    return _call(_os().evolutions.create, **request.model_dump())


@router.post("/evolutions/{evolution_id}/transition")
def transition_evolution(evolution_id: str, request: EvolutionTransitionRequest) -> dict[str, Any]:
    return _call(_os().evolutions.transition, evolution_id, **request.model_dump())


@router.get("/policy")
def policy_snapshot() -> dict[str, Any]:
    return _os().policy.snapshot()


@router.get("/audit")
def audit_log(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, Any]]:
    return _os().store.audits(limit)


@router.post("/worker/run-once")
def run_worker_once(limit: int = Query(default=1, ge=1, le=10)) -> dict[str, Any]:
    tasks = [_os().run_task(task["id"]) for task in _os().tasks.list(status="QUEUED", limit=limit)]
    return {"processed": len(tasks), "tasks": tasks}


@router.post("/automations")
def create_automation(request: WorkflowCreateRequest) -> dict[str, Any]:
    return _call(_os().workflows.create, **request.model_dump())


@router.get("/automations")
def list_automations() -> list[dict[str, Any]]:
    return _os().workflows.list()

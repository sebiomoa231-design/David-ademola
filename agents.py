from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services.agent_engine import AgentManager
from app.services.external_agents import ExternalAgentError, ExternalAgentRegistry


router = APIRouter(prefix="/agents", tags=["agents"])
settings = get_settings()
manager = AgentManager(settings)
external_agents = ExternalAgentRegistry(settings)


class DispatchRequest(BaseModel):
    agent_name: str = Field(min_length=1, max_length=100)
    goal: str = Field(min_length=1, max_length=12_000)
    background: bool = Field(default=False, description="Return a queued run immediately when true")


def _run_payload(run: Any) -> dict[str, Any]:
    return run.as_dict()


@router.get("")
def list_agents() -> list[dict[str, Any]]:
    return manager.list_agents()


@router.post("/dispatch")
async def dispatch(payload: DispatchRequest) -> dict[str, Any]:
    try:
        if payload.background:
            run = await manager.dispatch_background(payload.agent_name, payload.goal)
        else:
            run = await manager.dispatch(payload.agent_name, payload.goal)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _run_payload(run)


@router.get("/runs")
def list_runs(limit: int = Query(default=50, ge=1, le=100)) -> list[dict[str, Any]]:
    return manager.list_runs(limit)


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    run = manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_payload(run)


@router.post("/runs/{run_id}/cancel")
def cancel_run(run_id: str) -> dict[str, Any]:
    run = manager.cancel(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_payload(run)


class ExternalConsultRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=12_000)
    context: dict[str, Any] = Field(default_factory=dict)


@router.get("/external")
def list_external_agents() -> dict[str, Any]:
    """List redacted metadata for explicitly configured external agents."""
    return {"agents": external_agents.list()}


@router.post("/external/{agent_id}/consult")
async def consult_external_agent(agent_id: str, payload: ExternalConsultRequest) -> dict[str, Any]:
    """Consult one allowlisted external agent and return a traceable result."""
    try:
        return await external_agents.consult(agent_id, payload.objective, payload.context)
    except ExternalAgentError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc

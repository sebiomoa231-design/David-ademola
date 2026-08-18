from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services.agent_engine import AgentManager


router = APIRouter(prefix="/agents", tags=["agents"])
manager = AgentManager(get_settings())


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

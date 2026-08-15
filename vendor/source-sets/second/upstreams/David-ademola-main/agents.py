from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.agent_engine import AgentManager

router = APIRouter(prefix="/agents", tags=["agents"])
manager = AgentManager()


class DispatchRequest(BaseModel):
    agent_name: str
    goal: str


@router.get("")
def list_agents() -> list[dict]:
    return manager.list_agents()


@router.post("/dispatch")
async def dispatch(payload: DispatchRequest) -> dict:
    try:
        run = await manager.dispatch(payload.agent_name, payload.goal)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "id": run.id,
        "agent_name": run.agent_name,
        "goal": run.goal,
        "state": run.state.value,
        "steps": [
            {"id": s.id, "title": s.title, "state": s.state.value, "output": s.output, "error": s.error}
            for s in run.steps
        ],
        "logs": run.logs,
    }


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict:
    run = manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "id": run.id,
        "agent_name": run.agent_name,
        "goal": run.goal,
        "state": run.state.value,
        "steps": [
            {"id": s.id, "title": s.title, "state": s.state.value, "output": s.output, "error": s.error}
            for s in run.steps
        ],
        "logs": run.logs,
    }

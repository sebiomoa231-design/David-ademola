"""David AI — Orchestrator API Routes.

Exposes the multi-agent orchestration system and provider health
to the frontend for real-time status and interaction.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])


class OrchestratorRequest(BaseModel):
    message: str
    context: Optional[dict] = None
    use_multi_agent: bool = True


class OrchestratorResponse(BaseModel):
    text: str
    plan_id: Optional[str] = None
    objective: Optional[str] = None
    agents_used: list[str] = []
    providers_used: list[str] = []
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_tasks: int = 0
    task_details: list[dict] = []


# These will be initialized by the app startup
_orchestrator = None
_intelligent_router = None


def init_orchestrator(orchestrator, intelligent_router):
    """Initialize the orchestrator and router references."""
    global _orchestrator, _intelligent_router
    _orchestrator = orchestrator
    _intelligent_router = intelligent_router


@router.post("/process", response_model=OrchestratorResponse)
async def process_with_orchestrator(request: OrchestratorRequest):
    """Process a message through the multi-agent orchestrator.

    The orchestrator will:
    1. Detect which sub-agents are needed
    2. Create a plan with sub-tasks
    3. Execute tasks in parallel where possible
    4. Synthesize results from all agents
    """
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    result = await _orchestrator.process(
        message=request.message,
        context=request.context,
    )
    return OrchestratorResponse(**result)


@router.get("/status")
async def get_orchestrator_status():
    """Get the current status of all sub-agents and the orchestrator."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    return _orchestrator.get_status()


@router.get("/agents")
async def list_agents():
    """List all available sub-agents and their current state."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    return {
        "agents": [
            agent.get_status()
            for agent in _orchestrator.agents.values()
        ]
    }


@router.get("/agents/{role}")
async def get_agent_detail(role: str):
    """Get detailed status for a specific sub-agent."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    from app.agents.orchestrator import AgentRole
    try:
        agent_role = AgentRole(role)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown agent role: {role}")

    status = _orchestrator.get_agent_status(agent_role)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Agent not found: {role}")
    return status


@router.get("/providers/health")
async def get_provider_health():
    """Get health report for all AI providers.

    Shows: state, success rate, latency, availability for each provider.
    Used by the frontend provider dashboard.
    """
    if _intelligent_router is None:
        raise HTTPException(status_code=503, detail="Router not initialized")
    return _intelligent_router.get_health_report()


@router.post("/providers/{provider_name}/reset")
async def reset_provider_circuit(provider_name: str):
    """Manually reset a provider's circuit breaker.

    Use when a provider has recovered but the circuit is still open.
    """
    if _intelligent_router is None:
        raise HTTPException(status_code=503, detail="Router not initialized")

    success = _intelligent_router.reset_provider(provider_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Provider not found: {provider_name}")
    return {"message": f"Circuit breaker reset for {provider_name}", "provider": provider_name}


@router.get("/plans")
async def list_plans():
    """List recent orchestration plans."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Return last 20 plans
    recent_plans = _orchestrator.plans[-20:]
    return {
        "plans": [p.to_dict() for p in reversed(recent_plans)],
        "total": len(_orchestrator.plans),
    }


@router.get("/plans/{plan_id}")
async def get_plan_detail(plan_id: str):
    """Get detailed view of a specific plan and its sub-tasks."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    for plan in _orchestrator.plans:
        if plan.id == plan_id:
            return plan.to_dict()

    raise HTTPException(status_code=404, detail=f"Plan not found: {plan_id}")

"""Public, credential-safe AI Core API routes."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from david_fabric.services.ai_core import AICoreService
from david_fabric.services.registry import list_enriched_capabilities, registry_discovery_report


router = APIRouter(prefix="/ai-core", tags=["ai-core"])


class AIRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = Field(default=None, max_length=200)
    project_id: str | None = Field(default=None, max_length=200)
    task_id: str | None = Field(default=None, max_length=200)
    requested_capability: str | None = Field(default=None, max_length=100)
    context: dict[str, Any] = Field(default_factory=dict)
    approved: bool = False
    preferred_providers: list[str] = Field(default_factory=list, max_length=12)


class IntentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    requested_capability: str | None = Field(default=None, max_length=100)


class PlanRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    requested_capability: str | None = Field(default=None, max_length=100)
    project_id: str | None = Field(default=None, max_length=200)
    task_id: str | None = Field(default=None, max_length=200)
    context: dict[str, Any] = Field(default_factory=dict)


def get_ai_core(settings: Settings = Depends(get_settings)) -> AICoreService:
    return AICoreService(settings)


@router.post("/process")
async def process(request: AIRequest, core: AICoreService = Depends(get_ai_core)) -> dict[str, Any]:
    try:
        result = await core.process(
            request.message,
            conversation_id=request.conversation_id,
            project_id=request.project_id,
            task_id=request.task_id,
            context=request.context,
            requested_capability=request.requested_capability,
            approved=request.approved,
            preferred_providers=request.preferred_providers,
        )
        return result.as_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="AI Core orchestration failed safely") from exc


@router.get("/health")
def health(core: AICoreService = Depends(get_ai_core)) -> dict[str, Any]:
    return core.health()


@router.get("/status")
def status(core: AICoreService = Depends(get_ai_core)) -> dict[str, Any]:
    return core.status()


@router.post("/intent")
def intent(request: IntentRequest, core: AICoreService = Depends(get_ai_core)) -> dict[str, Any]:
    return {"intent": core.intent_classify(request.message, request.requested_capability).as_dict()}


@router.post("/plan")
def plan(request: PlanRequest, core: AICoreService = Depends(get_ai_core)) -> dict[str, Any]:
    try:
        return core.plan_only(
            request.message,
            requested_capability=request.requested_capability,
            context=request.context,
            project_id=request.project_id,
            task_id=request.task_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="AI Core planning failed safely") from exc


@router.get("/capabilities")
def capabilities(core: AICoreService = Depends(get_ai_core)) -> dict[str, Any]:
    # Registry data is readiness metadata only; no credentials or secret values
    # are included in list_enriched_capabilities/provider status responses.
    return {
        "capabilities": list_enriched_capabilities(),
        "providers": core.capability_router.registry.list(),
        "discovery": registry_discovery_report(),
    }


__all__ = ["router"]

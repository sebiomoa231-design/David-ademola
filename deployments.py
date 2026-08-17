from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.render_service import RenderApiError, RenderService

router = APIRouter(prefix="/deployments", tags=["deployments"])


class RenderServiceRequest(BaseModel):
    type: str = Field(default="web_service", pattern="^(static_site|web_service|private_service|background_worker|cron_job)$")
    name: str = Field(min_length=1, max_length=100)
    repo: str | None = None
    branch: str | None = None
    autoDeploy: str = Field(default="yes", pattern="^(yes|no)$")
    rootDir: str | None = None
    envVars: list[dict[str, str]] = Field(default_factory=list, max_length=50)


def _service(settings: Settings = Depends(get_settings)) -> RenderService:
    return RenderService(settings)


def _render_error(exc: RenderApiError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc), "retryable": exc.retryable})


@router.get("/render/health")
async def render_health(service: RenderService = Depends(_service)) -> dict[str, Any]:
    return await service.health()


@router.get("/render/services")
async def render_services(service: RenderService = Depends(_service)) -> dict[str, Any] | list[Any]:
    try:
        return await service.list_services()
    except RenderApiError as exc:
        raise _render_error(exc) from exc


@router.post("/render/services")
async def create_render_service(payload: RenderServiceRequest, service: RenderService = Depends(_service)) -> dict[str, Any] | list[Any]:
    try:
        return await service.create_service(payload.model_dump(exclude_none=True, by_alias=True))
    except RenderApiError as exc:
        raise _render_error(exc) from exc


@router.post("/render/services/{service_id}/deploy")
async def trigger_render_deploy(service_id: str, clear_cache: bool = False, service: RenderService = Depends(_service)) -> dict[str, Any] | list[Any]:
    try:
        return await service.trigger_deploy(service_id, clear_cache=clear_cache)
    except RenderApiError as exc:
        raise _render_error(exc) from exc


@router.get("/render/services/{service_id}/deploys")
async def list_render_deploys(service_id: str, service: RenderService = Depends(_service)) -> dict[str, Any] | list[Any]:
    try:
        return await service.list_deploys(service_id)
    except RenderApiError as exc:
        raise _render_error(exc) from exc


@router.get("/render/services/{service_id}/deploys/{deploy_id}")
async def get_render_deploy(service_id: str, deploy_id: str, service: RenderService = Depends(_service)) -> dict[str, Any] | list[Any]:
    try:
        return await service.get_deploy(service_id, deploy_id)
    except RenderApiError as exc:
        raise _render_error(exc) from exc

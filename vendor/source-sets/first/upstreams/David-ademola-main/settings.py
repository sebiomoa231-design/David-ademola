from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsResponse(BaseModel):
    name: str
    theme: str
    memory_enabled: bool
    provider_priority: list[str]
    max_upload_mb: int


@router.get("", response_model=SettingsResponse)
def get_settings_route(settings: Settings = Depends(get_settings)) -> SettingsResponse:
    return SettingsResponse(
        name="David",
        theme="dark",
        memory_enabled=True,
        provider_priority=settings.provider_priority_list,
        max_upload_mb=settings.max_upload_mb,
    )

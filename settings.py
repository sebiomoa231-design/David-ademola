from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.models import PersistentSettings, SettingsUpdate
from app.services.supabase_service import SupabaseApiError, SupabasePersistence

router = APIRouter(prefix="/settings", tags=["settings"])


def _defaults(settings: Settings) -> dict:
    return {
        "name": "David",
        "theme": "dark",
        "memory_enabled": True,
        "provider_priority": settings.provider_priority_list,
        "max_upload_mb": settings.max_upload_mb,
        "preferences": {},
        "workspace_name": "David AI",
        "brand_voice": "calm, intelligent, authoritative",
        "timezone": "UTC",
    }


def _response(settings: Settings, payload: dict, status: str) -> PersistentSettings:
    merged = {**_defaults(settings), **payload}
    merged["persistence_status"] = status
    return PersistentSettings(**merged)


@router.get("", response_model=PersistentSettings)
def get_settings_route(settings: Settings = Depends(get_settings)) -> PersistentSettings:
    persistence = SupabasePersistence(settings)
    if not persistence.database_enabled:
        return _response(settings, {}, "local-only")
    try:
        stored = persistence.get_settings() or {}
    except SupabaseApiError as exc:
        raise HTTPException(status_code=502, detail="Settings persistence is unavailable") from exc
    return _response(settings, stored, "persisted" if stored else "local-only")


@router.patch("", response_model=PersistentSettings)
def update_settings_route(
    payload: SettingsUpdate,
    settings: Settings = Depends(get_settings),
) -> PersistentSettings:
    persistence = SupabasePersistence(settings)
    if not persistence.database_enabled:
        raise HTTPException(status_code=503, detail="Settings persistence is not enabled")
    try:
        current = persistence.get_settings() or {}
        merged = {**_defaults(settings), **current, **payload.model_dump(exclude_none=True)}
        stored = persistence.update_settings(merged)
    except SupabaseApiError as exc:
        raise HTTPException(status_code=502, detail="Settings persistence failed") from exc
    return _response(settings, stored, "persisted")

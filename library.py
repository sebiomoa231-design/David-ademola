from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import Settings, get_settings
from app.models import AssetItem, FavoriteRequest, GenerationCreate, GenerationItem, SupabaseStatus
from app.services.supabase_service import SupabaseApiError, SupabasePersistence

router = APIRouter(prefix="/library", tags=["library"])


def get_persistence(settings: Settings = Depends(get_settings)) -> SupabasePersistence:
    return SupabasePersistence(settings)


def require_database(persistence: SupabasePersistence) -> SupabasePersistence:
    if not persistence.database_enabled:
        raise HTTPException(
            status_code=503,
            detail="Supabase database persistence is not enabled; apply database/migrations/0001_david_ai_core.sql and set SUPABASE_PERSISTENCE_ENABLED=true",
        )
    return persistence


@router.get("/status", response_model=SupabaseStatus)
def library_status(settings: Settings = Depends(get_settings)) -> SupabaseStatus:
    persistence = SupabasePersistence(settings)
    configured = persistence.storage_enabled
    migration_required = configured and not persistence.database_enabled
    if configured:
        try:
            persistence.health()
        except SupabaseApiError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
    return SupabaseStatus(
        configured=configured,
        database_enabled=persistence.database_enabled,
        storage_bucket=settings.supabase_storage_bucket,
        migration_required=migration_required,
    )


@router.get("/assets", response_model=list[AssetItem])
def list_assets(
    project_id: str | None = Query(default=None),
    kind: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    persistence: SupabasePersistence = Depends(get_persistence),
) -> list[AssetItem]:
    try:
        rows = require_database(persistence).list_assets(project_id=project_id, kind=kind, limit=limit)
    except SupabaseApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [AssetItem(**row) for row in rows]


@router.post("/assets/{asset_id}/favorite", response_model=AssetItem)
def set_favorite(
    asset_id: str,
    payload: FavoriteRequest,
    persistence: SupabasePersistence = Depends(get_persistence),
) -> AssetItem:
    try:
        row = require_database(persistence).set_favorite(asset_id, payload.favorite)
    except SupabaseApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not row:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetItem(**row)


@router.get("/generations", response_model=list[GenerationItem])
def list_generations(
    project_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    persistence: SupabasePersistence = Depends(get_persistence),
) -> list[GenerationItem]:
    try:
        rows = require_database(persistence).list_generations(project_id=project_id, limit=limit)
    except SupabaseApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [GenerationItem(**row) for row in rows]


@router.post("/generations", response_model=GenerationItem)
def create_generation(
    payload: GenerationCreate,
    persistence: SupabasePersistence = Depends(get_persistence),
) -> GenerationItem:
    try:
        row = require_database(persistence).create_generation(payload.model_dump(mode="json"))
    except SupabaseApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return GenerationItem(**row)

from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from app.core.config import Settings, get_settings
from app.core.logging import log_upload
from app.core.security import sanitize_filename, validate_upload_size
from app.services.supabase_service import SupabaseApiError, SupabasePersistence

router = APIRouter(prefix="/files", tags=["files"])


def _upload_dir(settings: Settings) -> Path:
    path = Path(settings.data_dir) / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    project_id: str | None = Form(default=None),
    kind: str = Form(default="other"),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    safe_name = sanitize_filename(file.filename or "upload.bin")
    content = await file.read()
    validate_upload_size(len(content))
    persistence = SupabasePersistence(settings)
    normalized_kind = kind if kind in {"image", "video", "audio", "document", "website", "other"} else "other"

    if persistence.database_enabled:
        try:
            return persistence.upload_asset(
                filename=safe_name,
                content=content,
                content_type=file.content_type,
                project_id=project_id,
                kind=normalized_kind,
            )
        except SupabaseApiError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    upload_dir = _upload_dir(settings)
    target = upload_dir / f"{uuid4().hex}_{safe_name}"
    target.write_bytes(content)
    log_upload(safe_name, len(content))
    return {
        "filename": safe_name,
        "stored_as": target.name,
        "status": "saved",
        "backend": "local-json",
        "kind": normalized_kind,
        "size_bytes": len(content),
        "download_url": f"/api/files/local/{target.name}",
    }


@router.get("/local-assets")
def list_local_assets(
    kind: str | None = Query(default=None, max_length=32),
    settings: Settings = Depends(get_settings),
) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for path in sorted(_upload_dir(settings).iterdir(), key=lambda item: item.stat().st_mtime, reverse=True):
        if not path.is_file():
            continue
        if kind and kind not in path.name.lower():
            continue
        assets.append({
            "id": path.name,
            "filename": path.name.split("_", 1)[-1],
            "stored_as": path.name,
            "size_bytes": path.stat().st_size,
            "created_at": path.stat().st_mtime,
            "backend": "local-json",
            "download_url": f"/api/files/local/{path.name}",
        })
    return assets[:200]


@router.get("/local/{stored_as}")
def download_local_asset(stored_as: str, settings: Settings = Depends(get_settings)) -> FileResponse:
    safe_name = Path(stored_as).name
    target = _upload_dir(settings) / safe_name
    if not target.is_file():
        raise HTTPException(status_code=404, detail="The local asset was not found.")
    return FileResponse(target)

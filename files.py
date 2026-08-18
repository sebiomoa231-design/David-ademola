from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.config import Settings, get_settings
from app.core.logging import log_upload
from app.core.security import sanitize_filename, validate_upload_size
from app.services.supabase_service import SupabaseApiError, SupabasePersistence

router = APIRouter(prefix="/files", tags=["files"])


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

    if persistence.database_enabled:
        try:
            return persistence.upload_asset(
                filename=safe_name,
                content=content,
                content_type=file.content_type,
                project_id=project_id,
                kind=kind if kind in {"image", "video", "audio", "document", "website", "other"} else "other",
            )
        except SupabaseApiError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    upload_dir = Path(settings.data_dir) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Preserve the existing local behavior until the database migration is
    # applied and SUPABASE_PERSISTENCE_ENABLED=true is set server-side.
    target = upload_dir / f"{uuid4().hex}_{safe_name}"
    target.write_bytes(content)
    log_upload(safe_name, len(content))

    return {"filename": safe_name, "stored_as": target.name, "status": "saved", "backend": "local-json"}

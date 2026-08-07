from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.config import Settings, get_settings
from app.core.logging import log_upload
from app.core.security import sanitize_filename, validate_upload_size

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    safe_name = sanitize_filename(file.filename or "upload.bin")
    content = await file.read()
    validate_upload_size(len(content))

    upload_dir = Path(settings.data_dir) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Avoid overwriting another user's file once user scoping/auth is added.
    target = upload_dir / f"{uuid4().hex}_{safe_name}"
    target.write_bytes(content)
    log_upload(safe_name, len(content))

    return {"filename": safe_name, "stored_as": target.name, "status": "saved"}

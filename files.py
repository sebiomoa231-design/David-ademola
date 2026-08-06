from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.config import Settings, get_settings
from app.core.logging import log_upload
from app.core.security import sanitize_filename, validate_upload_size

router = APIRouter(prefix="/files", tags=["files"])
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    safe_name = sanitize_filename(file.filename or "upload.bin")
    content = await file.read()
    validate_upload_size(len(content))

    target = UPLOAD_DIR / safe_name
    target.write_bytes(content)
    log_upload(safe_name, len(content))

    return {"filename": safe_name, "status": "saved"}

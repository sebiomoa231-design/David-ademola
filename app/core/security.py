from __future__ import annotations

import re
from pathlib import Path

from fastapi import HTTPException, Request

from app.core.config import get_settings

_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")

_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 120
_request_log: dict[str, list[float]] = {}


def sanitize_filename(filename: str) -> str:
    """Strip path components and reject unsafe characters in an upload filename."""
    name = Path(filename).name
    if not name or not _SAFE_FILENAME_RE.match(name):
        raise HTTPException(status_code=400, detail="Invalid filename")
    return name


def validate_upload_size(size_bytes: int) -> None:
    settings = get_settings()
    if size_bytes > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds max upload size of {settings.max_upload_mb} MB",
        )


def sanitize_text(value: str, max_length: int = 20000) -> str:
    if len(value) > max_length:
        raise HTTPException(status_code=400, detail="Input exceeds maximum length")
    return value.strip()


def check_rate_limit(request: Request) -> None:
    """Simple in-memory sliding-window rate limit hook, keyed by client host."""
    import time

    client = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW_SECONDS

    history = [t for t in _request_log.get(client, []) if t > window_start]
    history.append(now)
    _request_log[client] = history

    if len(history) > _RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from app.core.config import PROJECT_ROOT


class JsonStorage:
    """Small JSON persistence layer used by the current single-instance backend."""

    def __init__(self, base_dir: str | None = None) -> None:
        configured = base_dir or os.getenv("DATA_DIR")
        self.base_dir = Path(configured or (PROJECT_ROOT / "data"))
        if not self.base_dir.is_absolute():
            self.base_dir = PROJECT_ROOT / self.base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self, name: str) -> Path:
        safe_name = Path(name).name
        return self.base_dir / f"{safe_name}.json"

    def read(self, name: str, default: Any) -> Any:
        path = self._path(name)
        if not path.exists():
            self.write(name, default)
            return default
        with self._lock:
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, TypeError):
                return default

    def write(self, name: str, value: Any) -> None:
        path = self._path(name)
        payload = json.dumps(
            value, indent=2, ensure_ascii=False, default=str
        )
        with self._lock:
            fd, temp_name = tempfile.mkstemp(
                prefix=f".{path.stem}.", suffix=".tmp", dir=self.base_dir
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temp_name, path)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)

    def append(
        self,
        name: str,
        item: Any,
        default: list[Any] | None = None,
    ) -> list[Any]:
        items = self.read(name, default or [])
        if not isinstance(items, list):
            items = list(default or [])
        items.append(item)
        self.write(name, items)
        return items

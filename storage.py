from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any


class JsonStorage:
    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self, name: str) -> Path:
        return self.base_dir / f"{name}.json"

    def read(self, name: str, default: Any) -> Any:
        path = self._path(name)
        if not path.exists():
            self.write(name, default)
            return default
        with self._lock:
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return default

    def write(self, name: str, value: Any) -> None:
        path = self._path(name)
        with self._lock:
            path.write_text(
                json.dumps(value, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )

    def append(self, name: str, item: Any, default: list[Any] | None = None) -> list[Any]:
        default = default or []
        items = self.read(name, default)
        if not isinstance(items, list):
            items = list(default)
        items.append(item)
        self.write(name, items)
        return items

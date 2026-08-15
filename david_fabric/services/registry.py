from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG = PROJECT_ROOT / "config" / "capabilities.yaml"


@lru_cache(maxsize=1)
def load_capabilities() -> list[dict[str, Any]]:
    with CONFIG.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    capabilities = data.get("capabilities", [])
    return [item for item in capabilities if isinstance(item, dict) and item.get("id")]


def get_capability(capability_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in load_capabilities() if item.get("id") == capability_id),
        None,
    )


def match_capabilities(text: str) -> list[dict[str, Any]]:
    """Return keyword-matched capabilities in deterministic score order."""

    normalized = text.casefold()
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for index, item in enumerate(load_capabilities()):
        keywords = [str(keyword).casefold() for keyword in item.get("keywords", [])]
        score = sum(1 for keyword in keywords if keyword and keyword in normalized)
        if score:
            scored.append((score, -index, item))
    scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [item for _, _, item in scored]

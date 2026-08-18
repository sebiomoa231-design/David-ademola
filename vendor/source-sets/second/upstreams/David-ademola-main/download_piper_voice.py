from __future__ import annotations

import hashlib
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE_DIR = ROOT / "voices"
MODEL = VOICE_DIR / "en_US-ryan-high.onnx"
CONFIG = VOICE_DIR / "en_US-ryan-high.onnx.json"

MODEL_URL = os.getenv(
    "PIPER_VOICE_URL",
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
    "en/en_US/ryan/high/en_US-ryan-high.onnx",
)
CONFIG_URL = os.getenv(
    "PIPER_VOICE_CONFIG_URL",
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
    "en/en_US/ryan/high/en_US-ryan-high.onnx.json",
)
EXPECTED_SHA256 = os.getenv(
    "PIPER_VOICE_SHA256",
    "b3990d7606e183ec8dbfba70a4607074f162de1a0c412e0180d1ff60bb154eca",
)


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".part")
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(destination)


def verify_sha256(path: Path, expected: str) -> None:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected:
        path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Piper voice SHA-256 mismatch: expected {expected}, got {actual}"
        )


def main() -> None:
    if not MODEL.exists():
        download(MODEL_URL, MODEL)
    verify_sha256(MODEL, EXPECTED_SHA256)

    if not CONFIG.exists():
        download(CONFIG_URL, CONFIG)

    print(f"Piper voice ready: {MODEL}")


if __name__ == "__main__":
    main()

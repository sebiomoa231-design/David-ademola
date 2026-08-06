from __future__ import annotations

import asyncio
import os
import tempfile


class PiperError(Exception):
    def __init__(self, message: str, stderr: str = "") -> None:
        self.stderr = stderr
        super().__init__(message)


class PiperTTSClient:
    """
    Wrapper around the local Piper TTS binary (https://github.com/rhasspy/piper).
    Piper runs entirely offline: text goes in via stdin, a WAV file comes out.
    No network call is made and no API key is used -- this matches the
    "offline architecture where possible" requirement in the original spec.

    Requires:
      - The `piper` executable installed and on PATH (or an explicit path
        via settings.piper_executable).
      - A downloaded voice model (.onnx) with its matching .onnx.json file
        in the same directory, e.g. en_US-ryan-high.onnx.
    """

    def __init__(self, executable: str, voice_model_path: str) -> None:
        self.executable = executable
        self.voice_model_path = self._resolve_path(voice_model_path)

    @staticmethod
    def _resolve_path(path: str) -> str:
        """Relative paths (e.g. 'voices/en_US-ryan-high.onnx') are resolved
        against the backend package root, so the app works the same whether
        it's launched from backend/ or from anywhere else."""
        if not path or os.path.isabs(path):
            return path
        backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(backend_root, path)

    def is_configured(self) -> bool:
        return bool(self.voice_model_path)

    async def synthesize(self, text: str) -> bytes:
        if not self.voice_model_path:
            raise PiperError("No Piper voice model configured (PIPER_VOICE_MODEL is empty).")

        if not os.path.isfile(self.voice_model_path):
            raise PiperError(
                f"Piper voice model not found at '{self.voice_model_path}'. "
                "Check the PIPER_VOICE_MODEL path in your .env."
            )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            out_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.executable,
                "--model", self.voice_model_path,
                "--output_file", out_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate(input=text.encode("utf-8"))

            if proc.returncode != 0:
                raise PiperError(
                    f"Piper exited with code {proc.returncode}.",
                    stderr=stderr.decode("utf-8", errors="replace"),
                )

            if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
                raise PiperError("Piper produced no audio output.", stderr=stderr.decode("utf-8", errors="replace"))

            with open(out_path, "rb") as f:
                return f.read()

        except FileNotFoundError as exc:
            raise PiperError(
                f"Piper executable '{self.executable}' not found. "
                "Install it from https://github.com/rhasspy/piper and/or set PIPER_EXECUTABLE to its full path."
            ) from exc
        finally:
            if os.path.isfile(out_path):
                os.remove(out_path)

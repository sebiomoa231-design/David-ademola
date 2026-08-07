from __future__ import annotations

import asyncio
import os
import shutil
import tempfile


class PiperError(Exception):
    def __init__(self, message: str, stderr: str = "") -> None:
        self.stderr = stderr
        super().__init__(message)


class PiperTTSClient:
    """Async wrapper around the Piper command-line text-to-speech engine."""

    def __init__(self, executable: str, voice_model_path: str) -> None:
        self.executable = executable
        self.voice_model_path = self._resolve_path(voice_model_path)

    @staticmethod
    def _resolve_path(path: str) -> str:
        if not path:
            return ""
        if os.path.isabs(path):
            return path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(project_root, path)

    def is_configured(self) -> bool:
        executable_ok = bool(shutil.which(self.executable) or os.path.isfile(self.executable))
        model_ok = bool(self.voice_model_path and os.path.isfile(self.voice_model_path))
        return executable_ok and model_ok

    async def synthesize(self, text: str) -> bytes:
        if not self.voice_model_path:
            raise PiperError("No Piper voice model configured.")
        if not os.path.isfile(self.voice_model_path):
            raise PiperError(
                f"Piper voice model not found at '{self.voice_model_path}'. "
                "Run scripts/download_piper_voice.py or configure PIPER_VOICE_MODEL."
            )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            out_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                self.executable,
                "--model",
                self.voice_model_path,
                "--output_file",
                out_path,
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
                raise PiperError(
                    "Piper produced no audio output.",
                    stderr=stderr.decode("utf-8", errors="replace"),
                )

            with open(out_path, "rb") as handle:
                return handle.read()

        except FileNotFoundError as exc:
            raise PiperError(
                f"Piper executable '{self.executable}' was not found."
            ) from exc
        finally:
            if os.path.isfile(out_path):
                os.remove(out_path)

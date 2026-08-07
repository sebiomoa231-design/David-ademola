from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProviderResult:
    provider: str
    text: str


class ProviderError(RuntimeError):
    """Raised when an upstream provider cannot complete a request."""


class BaseProvider:
    name: str = "base"

    async def generate(self, message: str) -> ProviderResult:
        raise ProviderError(f"{self.name} is not configured.")

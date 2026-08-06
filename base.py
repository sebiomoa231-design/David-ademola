from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProviderResult:
    provider: str
    text: str


class BaseProvider:
    name: str = "base"

    async def generate(self, message: str) -> ProviderResult:
        return ProviderResult(
            provider=self.name,
            text="Provider not configured. Using fallback response.",
        )

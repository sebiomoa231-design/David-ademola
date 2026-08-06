from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Capability(str, Enum):
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    VISION = "vision"


@dataclass
class ProviderRecord:
    """
    Describes one AI provider for the registry: what it can do, whether
    it's configured, and simple health/usage counters. Real latency and
    success-rate tracking would be wired up once actual provider calls
    exist; today the counters just reflect what's been observed in this
    process's lifetime.
    """

    name: str
    capabilities: list[Capability]
    configured: bool = False
    priority: int = 100
    healthy: bool = True
    total_requests: int = 0
    total_failures: int = 0

    @property
    def success_rate(self) -> float | None:
        if self.total_requests == 0:
            return None
        return round(1 - (self.total_failures / self.total_requests), 4)

    def record_success(self) -> None:
        self.total_requests += 1
        self.healthy = True

    def record_failure(self) -> None:
        self.total_requests += 1
        self.total_failures += 1
        # Mark unhealthy after repeated recent failures rather than one blip.
        if self.total_requests >= 3 and (self.success_rate or 0) < 0.34:
            self.healthy = False


class ProviderRegistry:
    """
    Central registry of known AI providers and what they can do.
    This does not call any provider itself -- AIRouter and future
    media-generation routers use it to decide who to call and in
    what order, based on capability + configured + health + priority.
    """

    def __init__(self) -> None:
        self._providers: dict[str, ProviderRecord] = {}

    def register(self, record: ProviderRecord) -> None:
        self._providers[record.name] = record

    def get(self, name: str) -> ProviderRecord | None:
        return self._providers.get(name)

    def all(self) -> list[ProviderRecord]:
        return list(self._providers.values())

    def for_capability(self, capability: Capability) -> list[ProviderRecord]:
        matches = [
            p for p in self._providers.values()
            if capability in p.capabilities and p.configured and p.healthy
        ]
        matches.sort(key=lambda p: p.priority)
        return matches

    def best_for(self, capability: Capability) -> ProviderRecord | None:
        matches = self.for_capability(capability)
        return matches[0] if matches else None


def build_default_registry(settings) -> ProviderRegistry:
    """Builds a registry reflecting which text providers currently have keys configured."""
    registry = ProviderRegistry()
    text_providers = [
        ("gemini", settings.gemini_api_key, 1),
        ("groq", settings.groq_api_key, 2),
        ("openrouter", settings.openrouter_api_key, 3),
        ("cloudflare", settings.cloudflare_api_key, 4),
        ("cerebras", settings.cerebras_api_key, 5),
        ("sambanova", settings.sambanova_api_key, 6),
        ("huggingface", settings.huggingface_api_key, 7),
    ]
    for name, key, priority in text_providers:
        registry.register(
            ProviderRecord(
                name=name,
                capabilities=[Capability.TEXT, Capability.CODE],
                configured=bool(key),
                priority=priority,
            )
        )

    # Media/voice provider slots exist so the registry has a place to
    # report status, even though no provider integration is wired in yet.
    for name, caps in [
        ("elevenlabs", [Capability.TEXT_TO_SPEECH]),
        ("assemblyai", [Capability.SPEECH_TO_TEXT]),
        ("stability", [Capability.IMAGE]),
        ("runway", [Capability.VIDEO]),
        ("fal", [Capability.IMAGE, Capability.VIDEO]),
    ]:
        registry.register(ProviderRecord(name=name, capabilities=caps, configured=False))

    return registry

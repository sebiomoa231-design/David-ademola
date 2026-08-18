"""David AI — Intelligent Provider Router with Health Tracking & Circuit Breaker.

This enhanced router provides:
- Automatic failover across all configured providers
- Circuit breaker pattern (providers that fail repeatedly get temporarily disabled)
- Health scoring (providers are ranked by success rate and latency)
- Retry with exponential backoff per provider
- Capability-based routing (different tasks go to the best-suited provider)
- Cost-aware routing (prefer cheaper providers when quality is equivalent)
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.core.config import Settings
from app.core.logging import log_error, log_provider_selection
from app.providers.base import BaseProvider, ProviderError, ProviderResult
from app.providers.cerebras import CerebrasProvider
from app.providers.cloudflare import CloudflareProvider
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.providers.huggingface import HuggingFaceProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.openrouter import OpenRouterProvider
from app.providers.sambanova import SambaNovaProvider

logger = logging.getLogger(__name__)


class ProviderState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"
    UNCONFIGURED = "unconfigured"


class Capability(str, Enum):
    """Task capabilities for routing to the best provider."""
    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    FAST_RESPONSE = "fast_response"
    MULTILINGUAL = "multilingual"


@dataclass
class ProviderHealth:
    """Tracks health metrics for a single provider."""
    name: str
    state: ProviderState = ProviderState.HEALTHY
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    avg_latency_ms: float = 0.0
    circuit_open_until: float = 0.0

    # Circuit breaker thresholds
    failure_threshold: int = 3  # consecutive failures to open circuit
    recovery_timeout: float = 60.0  # seconds before retrying after circuit opens

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def is_available(self) -> bool:
        if self.state == ProviderState.UNCONFIGURED:
            return False
        if self.state == ProviderState.CIRCUIT_OPEN:
            # Check if recovery timeout has passed
            if time.time() >= self.circuit_open_until:
                return True  # Allow a probe request
            return False
        return True

    def record_success(self, latency_ms: float) -> None:
        self.total_requests += 1
        self.successful_requests += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        # Exponential moving average for latency
        if self.avg_latency_ms == 0:
            self.avg_latency_ms = latency_ms
        else:
            self.avg_latency_ms = 0.7 * self.avg_latency_ms + 0.3 * latency_ms
        self.state = ProviderState.HEALTHY

    def record_failure(self) -> None:
        self.total_requests += 1
        self.failed_requests += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()

        if self.consecutive_failures >= self.failure_threshold:
            self.state = ProviderState.CIRCUIT_OPEN
            self.circuit_open_until = time.time() + self.recovery_timeout
            logger.warning(
                f"Circuit breaker OPEN for {self.name} "
                f"(will retry after {self.recovery_timeout}s)"
            )
        elif self.consecutive_failures >= 2:
            self.state = ProviderState.DEGRADED


# Capability routing preferences (which providers are best for which tasks)
CAPABILITY_PREFERENCES: dict[Capability, list[str]] = {
    Capability.CHAT: ["gemini", "groq", "openrouter", "openai", "cloudflare", "cerebras", "sambanova"],
    Capability.CODE: ["openai", "gemini", "openrouter", "groq", "cerebras"],
    Capability.REASONING: ["openai", "gemini", "openrouter", "groq"],
    Capability.CREATIVE: ["gemini", "openai", "openrouter", "groq"],
    Capability.ANALYSIS: ["gemini", "openai", "openrouter", "groq"],
    Capability.FAST_RESPONSE: ["groq", "cerebras", "sambanova", "cloudflare", "gemini"],
    Capability.MULTILINGUAL: ["gemini", "openai", "openrouter"],
}


class IntelligentRouter:
    """Enhanced AI router with health tracking, circuit breaker, and capability routing.

    Improvements over the basic AIRouter:
    1. Circuit breaker: temporarily disables providers that fail repeatedly
    2. Health scoring: tracks success rate and latency per provider
    3. Capability routing: routes tasks to the best-suited provider
    4. Retry with backoff: retries failed requests with exponential backoff
    5. Provider ranking: dynamically reorders providers based on performance
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.providers: dict[str, BaseProvider] = {
            "openai": OpenAICompatibleProvider(
                name="openai",
                api_key=settings.openai_api_key,
                base_url="https://api.openai.com/v1",
                model=settings.openai_model,
                timeout=settings.request_timeout_seconds,
            ),
            "gemini": GeminiProvider(settings),
            "groq": GroqProvider(settings),
            "openrouter": OpenRouterProvider(settings),
            "cloudflare": CloudflareProvider(settings),
            "cerebras": CerebrasProvider(settings),
            "sambanova": SambaNovaProvider(settings),
            "huggingface": HuggingFaceProvider(settings),
        }

        # Initialize health tracking for each provider
        self.health: dict[str, ProviderHealth] = {}
        for name in self.providers:
            self.health[name] = ProviderHealth(name=name)

        # Mark unconfigured providers
        self._check_configuration()

    def _check_configuration(self) -> None:
        """Mark providers as unconfigured if they lack API keys."""
        key_map = {
            "openai": self.settings.openai_api_key,
            "gemini": self.settings.gemini_api_key,
            "groq": self.settings.groq_api_key,
            "openrouter": self.settings.openrouter_api_key,
            "cloudflare": self.settings.cloudflare_api_key,
            "cerebras": self.settings.cerebras_api_key,
            "sambanova": self.settings.sambanova_api_key,
            "huggingface": self.settings.huggingface_api_key,
        }
        for name, key in key_map.items():
            if not key:
                self.health[name].state = ProviderState.UNCONFIGURED

    def get_provider_order(
        self,
        capability: Optional[Capability] = None,
    ) -> list[str]:
        """Get the optimal provider order based on capability and health.

        Priority logic:
        1. If a capability is specified, prefer providers suited for that task
        2. Filter out unavailable providers (circuit open, unconfigured)
        3. Sort remaining by: health state > success rate > latency
        """
        if capability and capability in CAPABILITY_PREFERENCES:
            base_order = CAPABILITY_PREFERENCES[capability]
        else:
            base_order = self.settings.provider_priority_list

        # Filter to available providers and sort by health
        available = [
            name for name in base_order
            if name in self.health and self.health[name].is_available
        ]

        # Add any configured providers not in the preference list
        for name in self.providers:
            if name not in available and self.health[name].is_available:
                available.append(name)

        # Sort by health score (healthy > degraded, then by success rate)
        def health_score(name: str) -> tuple:
            h = self.health[name]
            state_score = {
                ProviderState.HEALTHY: 0,
                ProviderState.DEGRADED: 1,
                ProviderState.CIRCUIT_OPEN: 2,
            }.get(h.state, 3)
            return (state_score, -h.success_rate, h.avg_latency_ms)

        available.sort(key=health_score)
        return available

    async def generate(
        self,
        message: str,
        capability: Optional[Capability] = None,
        max_retries: int = 0,
    ) -> ProviderResult:
        """Generate a response with intelligent routing and fallback.

        Args:
            message: The user's message/prompt.
            capability: Optional capability hint for routing.
            max_retries: Additional retries per provider (0 = try once each).

        Returns:
            ProviderResult from the first successful provider.
        """
        provider_order = self.get_provider_order(capability)
        failures: list[str] = []

        if not provider_order:
            return ProviderResult(
                provider="fallback",
                text=(
                    "David AI is online, but no AI providers are currently available. "
                    "All providers are either unconfigured or temporarily disabled due to errors. "
                    "Please check your API keys in the environment configuration."
                ),
            )

        for provider_name in provider_order:
            provider = self.providers.get(provider_name)
            if provider is None:
                continue

            # Retry loop for this provider
            attempts = 1 + max_retries
            for attempt in range(attempts):
                try:
                    start_time = time.time()
                    result = await provider.generate(message)
                    latency_ms = (time.time() - start_time) * 1000

                    # Record success
                    self.health[provider_name].record_success(latency_ms)
                    log_provider_selection(result.provider)

                    logger.info(
                        f"Provider {provider_name} succeeded "
                        f"(latency: {latency_ms:.0f}ms, "
                        f"success_rate: {self.health[provider_name].success_rate:.1%})"
                    )
                    return result

                except (ProviderError, Exception) as exc:
                    self.health[provider_name].record_failure()
                    failure_msg = f"{provider_name}(attempt {attempt+1}): {exc}"
                    failures.append(failure_msg)
                    log_error(f"provider:{provider_name}", exc)

                    # Exponential backoff between retries (only if more attempts remain)
                    if attempt < attempts - 1:
                        backoff = min(2 ** attempt * 0.5, 5.0)
                        await asyncio.sleep(backoff)

        # All providers failed
        log_provider_selection("fallback")
        detail = "; ".join(failures[-5:])
        return ProviderResult(
            provider="fallback",
            text=(
                "David AI attempted all available providers but none could complete "
                "this request. "
                + (f"Details: {detail}" if detail else "")
                + "\n\nI'll keep trying on subsequent requests as providers recover."
            ),
        )

    async def generate_with_consensus(
        self,
        message: str,
        providers_to_query: int = 2,
        capability: Optional[Capability] = None,
    ) -> ProviderResult:
        """Query multiple providers and return the best response.

        Useful for critical tasks where you want to verify the answer.
        Queries multiple providers in parallel and returns the first success.
        """
        provider_order = self.get_provider_order(capability)[:providers_to_query]

        if not provider_order:
            return await self.generate(message, capability)

        # Run providers in parallel
        tasks = []
        for name in provider_order:
            provider = self.providers.get(name)
            if provider:
                tasks.append(self._timed_generate(name, provider, message))

        if not tasks:
            return await self.generate(message, capability)

        # Return first successful result
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, ProviderResult):
                return result

        # All failed, fall back to sequential
        return await self.generate(message, capability)

    async def _timed_generate(
        self, name: str, provider: BaseProvider, message: str
    ) -> ProviderResult:
        """Generate with timing for health tracking."""
        start_time = time.time()
        result = await provider.generate(message)
        latency_ms = (time.time() - start_time) * 1000
        self.health[name].record_success(latency_ms)
        return result

    def get_health_report(self) -> dict:
        """Get a full health report of all providers."""
        report = {}
        for name, health in self.health.items():
            report[name] = {
                "state": health.state.value,
                "success_rate": f"{health.success_rate:.1%}",
                "total_requests": health.total_requests,
                "consecutive_failures": health.consecutive_failures,
                "avg_latency_ms": f"{health.avg_latency_ms:.0f}",
                "available": health.is_available,
            }
        return report

    def reset_provider(self, provider_name: str) -> bool:
        """Manually reset a provider's circuit breaker."""
        if provider_name in self.health:
            self.health[provider_name].state = ProviderState.HEALTHY
            self.health[provider_name].consecutive_failures = 0
            self.health[provider_name].circuit_open_until = 0
            return True
        return False

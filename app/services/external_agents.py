"""Secure bridge for consulting explicitly configured external AI agents.

Agents are configured only through the server environment. The frontend receives
metadata and redacted results; credentials never leave this module.
"""
from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.config import Settings, get_settings


_AGENT_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")


class ExternalAgentError(RuntimeError):
    def __init__(self, message: str, *, code: str = "external_agent_error", status_code: int = 502):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


@dataclass(frozen=True)
class ExternalAgentSpec:
    id: str
    label: str
    url: str
    protocol: str = "json_task"
    api_key_env: str = ""
    capabilities: tuple[str, ...] = ()
    enabled: bool = True

    @property
    def configured(self) -> bool:
        return self.enabled and bool(self.url and (not self.api_key_env or os.getenv(self.api_key_env)))

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "protocol": self.protocol,
            "capabilities": list(self.capabilities),
            "configured": self.configured,
            "status": "configured" if self.configured else "not_configured",
        }


class ExternalAgentRegistry:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._agents = self._load()

    def _load(self) -> tuple[ExternalAgentSpec, ...]:
        raw = self.settings.external_agents_json.strip()
        if not raw:
            return ()
        try:
            entries = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ExternalAgentError("External agent configuration is invalid JSON", code="external_agent_config_invalid", status_code=500) from exc
        if not isinstance(entries, list):
            raise ExternalAgentError("External agent configuration must be a JSON array", code="external_agent_config_invalid", status_code=500)
        agents: list[ExternalAgentSpec] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ExternalAgentError("Each external agent entry must be an object", code="external_agent_config_invalid", status_code=500)
            agent_id = str(entry.get("id", "")).strip().lower()
            url = str(entry.get("url", "")).strip()
            parsed = urlparse(url)
            if not _AGENT_ID.fullmatch(agent_id) or parsed.scheme != "https" or not parsed.netloc:
                raise ExternalAgentError("External agents require a valid id and HTTPS URL", code="external_agent_config_invalid", status_code=500)
            agents.append(ExternalAgentSpec(
                id=agent_id,
                label=str(entry.get("label") or agent_id),
                url=url,
                protocol=str(entry.get("protocol") or "json_task"),
                api_key_env=str(entry.get("api_key_env") or ""),
                capabilities=tuple(str(item) for item in entry.get("capabilities", []) if str(item).strip()),
                enabled=bool(entry.get("enabled", True)),
            ))
        return tuple(agents)

    def list(self) -> list[dict[str, Any]]:
        return [agent.public() for agent in self._agents]

    def get(self, agent_id: str) -> ExternalAgentSpec | None:
        return next((agent for agent in self._agents if agent.id == agent_id.strip().lower()), None)

    async def consult(self, agent_id: str, objective: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        agent = self.get(agent_id)
        if not agent:
            raise ExternalAgentError("External agent is not registered", code="external_agent_not_found", status_code=404)
        if not agent.configured:
            raise ExternalAgentError("External agent is not configured", code="external_agent_not_configured", status_code=503)
        objective = objective.strip()
        if not objective:
            raise ExternalAgentError("A consultation objective is required", code="external_agent_invalid_request", status_code=422)
        request_id = str(uuid.uuid4())
        payload = self._payload(agent, request_id, objective, context or {})
        headers = {"Content-Type": "application/json", "X-David-Agent-Request": request_id}
        if agent.api_key_env:
            headers["Authorization"] = f"Bearer {os.getenv(agent.api_key_env, '')}"
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.settings.external_agent_timeout_seconds, follow_redirects=True) as client:
                response = await client.post(agent.url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise ExternalAgentError("External agent consultation timed out", code="external_agent_timeout", status_code=504) from exc
        except httpx.HTTPError as exc:
            raise ExternalAgentError("External agent connection failed", code="external_agent_network_error", status_code=502) from exc
        if response.status_code >= 400:
            raise ExternalAgentError(f"External agent rejected the consultation ({response.status_code})", code="external_agent_rejected", status_code=502)
        try:
            data = response.json()
        except ValueError as exc:
            raise ExternalAgentError("External agent returned non-JSON data", code="external_agent_invalid_response", status_code=502) from exc
        return {
            "request_id": request_id,
            "agent_id": agent.id,
            "agent_label": agent.label,
            "protocol": agent.protocol,
            "status": "completed",
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "text": self._text(data),
            "metadata": {"http_status": response.status_code},
        }

    @staticmethod
    def _payload(agent: ExternalAgentSpec, request_id: str, objective: str, context: dict[str, Any]) -> dict[str, Any]:
        if agent.protocol == "openai_chat":
            return {"model": context.get("model") or "default", "messages": [{"role": "user", "content": objective}], "metadata": {"request_id": request_id, "source": "david_ai"}}
        return {"request_id": request_id, "source": "david_ai", "objective": objective, "context": context}

    @staticmethod
    def _text(data: Any) -> str:
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            for key in ("text", "output", "response", "content", "message"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value
            choices = data.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                message = choices[0].get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    return message["content"]
        raise ExternalAgentError("External agent returned no readable text", code="external_agent_empty_response", status_code=502)

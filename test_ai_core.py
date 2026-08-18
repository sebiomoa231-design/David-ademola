from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.models import ChatRequest, ChatResponse
from fastapi.testclient import TestClient
from main import app
from david_fabric.services.ai_core import AICoreService, CoreResult
from app.services.provider_registry import ProviderIntegrationError


class FakeSpec:
    def __init__(self, provider: str, capabilities: tuple[str, ...] = ("reasoning",)):
        self.id = provider
        self.status = "supported"
        self.capabilities = capabilities

    def configured(self, settings):
        return True


class FakeRegistry:
    def __init__(self, providers=("openai", "gemini")):
        self.providers = list(providers)

    def capability_candidates(self, capability, preferred=None):
        ordered = list(preferred or []) + [item for item in self.providers if item not in (preferred or [])]
        return [FakeSpec(item, (capability,)) for item in ordered]

    def list(self):
        return [{"id": item, "configured": True, "status": "supported", "capabilities": ["reasoning"]} for item in self.providers]


class FakeRouter:
    def __init__(self, handler, providers=("openai", "gemini")):
        self.registry = FakeRegistry(providers)
        self.handler = handler
        self.calls = []

    async def execute(self, capability, payload, preferred=None):
        provider = list(preferred or ["unknown"])[0]
        self.calls.append((capability, provider, payload))
        return await self.handler(capability, provider, payload)


class FakeMemory:
    def __init__(self, memories=None):
        self.memories = memories or []
        self.learned = []

    def relevant(self, query, limit=8):
        return self.memories[:limit]

    def learn_from_text(self, text, source="user"):
        self.learned.append((text, source))


class FakeConversations:
    def __init__(self):
        self.rows = {}
        self.messages = []

    def create(self, title):
        item = SimpleNamespace(id="conversation-1")
        self.rows[item.id] = item
        return item

    def get(self, conversation_id):
        return self.rows.get(conversation_id)

    def add_message(self, conversation_id, role, content):
        self.messages.append((conversation_id, role, content))
        return SimpleNamespace(id=conversation_id)

    def recent_messages(self, conversation_id, limit=12):
        return [SimpleNamespace(role=role, content=content, created_at=SimpleNamespace(isoformat=lambda: "2026-01-01T00:00:00+00:00")) for _, role, content in self.messages[-limit:]]


class FakeStore:
    def __init__(self):
        self.saved = []
        self.events = []

    def save(self, record):
        self.saved.append(record)
        return record

    def event(self, event_type, payload, **kwargs):
        self.events.append((event_type, payload, kwargs))
        return {"event_type": event_type}


class FakeOperatingSystem:
    def __init__(self, context=None):
        self.store = FakeStore()
        self._context = context or {"memories": [], "records": [], "confidence": 0.0}

    def context(self, query, **kwargs):
        return {"query": query, **self._context}

    def health(self):
        return {"status": "ok"}


@pytest.fixture
def service(tmp_path):
    settings = Settings(data_dir=str(tmp_path), provider_priority="openai,gemini", provider_max_retries=1)
    memory = FakeMemory([SimpleNamespace(model_dump=lambda mode="json": {"id": "m1", "content": "owner prefers concise answers"})])
    conversations = FakeConversations()
    operating_system = FakeOperatingSystem({"memories": [{"id": "os-m1"}], "records": [{"id": "task-1"}], "confidence": 0.8})

    async def handler(capability, provider, payload):
        return {"provider": provider, "model": "test-model", "text": "validated answer"}

    router = FakeRouter(handler)
    return AICoreService(settings, memory, conversations, operating_system, router)


def test_intent_classification_and_plan(service):
    intent = service.intent_classify("Please create an image of a mountain")
    assert intent.execution_capability == "image"
    plan = service.plan_only("Please debug the repository and run the tests")
    assert plan["intent"]["execution_capability"] == "coding"
    assert plan["plan"]["steps"]


def test_simple_orchestration_assembles_context_and_persists(service):
    result = asyncio.run(service.process("Summarize my current project", conversation_id=None))
    assert result.status == "completed"
    assert result.provider == "openai"
    assert result.reply == "validated answer"
    assert result.conversation_id == "conversation-1"
    assert result.routing["context"]["memory_count"] == 1
    assert result.routing["context"]["operating_records"] == 1
    assert service.memory.learned == [("Summarize my current project", "ai-core")]
    assert any(record["entity_type"] == "ai_core_run" for record in service.operating_system.store.saved)


def test_provider_failure_recovers_to_next_provider(tmp_path):
    settings = Settings(data_dir=str(tmp_path), provider_priority="openai,gemini", provider_max_retries=0)
    attempts = []

    async def handler(capability, provider, payload):
        attempts.append(provider)
        if provider == "openai":
            raise ProviderIntegrationError("temporary failure", code="provider_timeout", retryable=False)
        return {"provider": provider, "model": "fallback-model", "text": "fallback answer"}

    router = FakeRouter(handler)
    service = AICoreService(settings, FakeMemory(), FakeConversations(), FakeOperatingSystem(), router)
    result = asyncio.run(service.process("Answer this with provider fallback"))
    assert result.status == "completed"
    assert result.provider == "gemini"
    assert attempts == ["openai", "gemini"]
    assert "openai" in result.routing["fallbacks_used"]


def test_policy_gate_blocks_deployment_without_execution(service):
    result = asyncio.run(service.process("Deploy this service to production", requested_capability="deployment"))
    assert result.status == "blocked"
    assert result.provider == "policy"
    assert result.routing["policy"]["allowed"] is False
    assert not service.capability_router.calls
    assert "policy blocked" in result.reply


def test_failed_provider_does_not_fabricate_success(tmp_path):
    settings = Settings(data_dir=str(tmp_path), provider_priority="openai", provider_max_retries=0)

    async def handler(capability, provider, payload):
        raise ProviderIntegrationError("rejected", code="provider_request_rejected", retryable=False)

    service = AICoreService(settings, FakeMemory(), FakeConversations(), FakeOperatingSystem(), FakeRouter(handler, ("openai",)))
    result = asyncio.run(service.process("Generate an image", requested_capability="image"))
    assert result.status == "failed"
    assert result.provider == "unavailable"
    assert "No successful result was fabricated" in result.reply


def test_chat_response_contract_is_preserved(service):
    result = asyncio.run(service.process("Hello David"))
    response = ChatResponse(
        reply=result.reply,
        provider=result.provider,
        conversation_id=result.conversation_id,
        capability_routing=result.routing,
    )
    assert response.reply == "validated answer"
    assert response.provider == "openai"
    assert isinstance(response.capability_routing, dict)
    assert ChatResponse.model_validate(response.model_dump()).conversation_id == "conversation-1"


def test_chat_request_contract_remains_unchanged():
    request = ChatRequest(message="hello")
    assert request.conversation_id is None


def test_ai_core_routes_are_mounted():
    client = TestClient(app)
    assert client.get("/api/ai-core/health").status_code == 200
    assert client.get("/api/ai-core/status").status_code == 200
    assert client.get("/api/ai-core/capabilities").status_code == 200
    assert client.post("/api/ai-core/intent", json={"message": "summarize my project"}).status_code == 200
    assert client.post("/api/ai-core/plan", json={"message": "plan a coding task"}).status_code == 200

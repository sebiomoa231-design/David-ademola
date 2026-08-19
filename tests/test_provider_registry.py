import asyncio
import json

import pytest

from app.core.config import Settings
from app.services.provider_registry import CapabilityNotSupported, CapabilityRouter, ProviderNotConfigured, ProviderRegistry


class FakeResponse:
    def __init__(self, payload, status_code=200, content=b"", headers=None):
        self._payload = payload
        self.status_code = status_code
        self.content = content or json.dumps(payload).encode()
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        return self._payload


def test_reasoning_uses_openai_responses_without_leaking_secret(monkeypatch):
    seen = {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, headers=None, **kwargs):
            seen.update({"method": method, "url": url, "headers": headers or {}, "kwargs": kwargs})
            return FakeResponse({"output_text": "verified response", "id": "resp_test"})

    import app.services.provider_registry as module
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeClient)
    settings = Settings(_env_file=None, openai_api_key="TOP_SECRET", provider_priority="openai")
    result = asyncio.run(CapabilityRouter(settings).execute("reasoning", {"prompt": "hello"}))
    assert result["text"] == "verified response"
    assert seen["url"].endswith("/responses")
    assert "TOP_SECRET" not in json.dumps(result)
    assert "TOP_SECRET" in seen["headers"]["Authorization"]


def test_anthropic_messages_contract(monkeypatch):
    seen = {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, headers=None, **kwargs):
            seen.update({"method": method, "url": url, "headers": headers or {}, "kwargs": kwargs})
            return FakeResponse({"content": [{"type": "text", "text": "claude response"}]})

    import app.services.provider_registry as module
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeClient)
    settings = Settings(_env_file=None, anthropic_api_key="ANTHROPIC_SECRET", provider_priority="anthropic")
    result = asyncio.run(CapabilityRouter(settings).execute("reasoning", {"prompt": "hello"}))
    assert result["text"] == "claude response"
    assert seen["url"].endswith("/messages")
    assert seen["headers"]["x-api-key"] == "ANTHROPIC_SECRET"
    assert "ANTHROPIC_SECRET" not in json.dumps(result)


def test_openai_image_generation_returns_b64_payload(monkeypatch):
    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, **kwargs):
            assert url.endswith("/images/generations")
            assert kwargs["json"]["response_format"] == "b64_json"
            return FakeResponse({"data": [{"b64_json": "abc", "revised_prompt": "p"}]})

    import app.services.provider_registry as module
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeClient)
    settings = Settings(_env_file=None, openai_api_key="secret", provider_priority="openai")
    result = asyncio.run(CapabilityRouter(settings).execute("image", {"prompt": "a blue square"}))
    assert result["images"][0]["b64_json"] == "abc"


def test_gemini_video_returns_trackable_operation_and_polls(monkeypatch):
    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, **kwargs):
            if method == "POST":
                assert url.endswith("/models/veo-3.1-generate-preview:predictLongRunning")
                assert kwargs["json"]["parameters"]["aspectRatio"] == "16:9"
                return FakeResponse({"name": "models/veo-3.1-generate-preview/operations/test-1"})
            assert method == "GET"
            return FakeResponse({"done": True, "response": {"generateVideoResponse": {"generatedSamples": [{"video": {"uri": "https://generativelanguage.googleapis.com/v1beta/files/video-1"}}]}}})

    import app.services.provider_registry as module
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeClient)
    settings = Settings(_env_file=None, gemini_api_key="GEMINI_SECRET", provider_priority="gemini")
    router = CapabilityRouter(settings)
    started = asyncio.run(router.execute("video", {"prompt": "a calm orbital interface", "aspect_ratio": "16:9"}))
    assert started["status"] == "processing"
    completed = asyncio.run(router.video_operation(started["operation_name"]))
    assert completed["status"] == "completed"
    assert completed["video_uri"].startswith("https://generativelanguage.googleapis.com/")
    assert "GEMINI_SECRET" not in json.dumps(completed)


def test_gemini_image_accepts_reference_image(monkeypatch):
    seen = {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, **kwargs):
            seen.update(kwargs)
            return FakeResponse({"candidates": [{"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": "abc"}}]}}]})

    import app.services.provider_registry as module
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeClient)
    settings = Settings(_env_file=None, gemini_api_key="secret", provider_priority="gemini")
    result = asyncio.run(CapabilityRouter(settings).execute("image", {"prompt": "enhance", "image_base64": "ref", "image_mime_type": "image/png"}))
    assert result["images"][0]["data"] == "abc"
    assert seen["json"]["contents"][0]["parts"][1]["inlineData"]["data"] == "ref"


def test_registry_reports_configured_status_without_credentials():
    registry = ProviderRegistry(Settings(_env_file=None, openai_api_key="", anthropic_api_key="", gemini_api_key="", groq_api_key="", openrouter_api_key="", voyage_api_key="", elevenlabs_api_key="", runway_api_key="", luma_api_key="", v0_api_key="", render_api_key=""))
    statuses = {item["id"]: item for item in registry.list()}
    assert statuses["openai"]["configured"] is False
    assert statuses["github"]["status"] == "existing_integration"
    assert "api_key" not in json.dumps(statuses).lower()
    assert "secret" not in json.dumps(statuses).lower()


def test_unconfigured_and_unverified_capabilities_are_explicit():
    router = CapabilityRouter(Settings(_env_file=None, openai_api_key="", provider_priority="openai"))
    openai = router.registry.get("openai")
    router.registry._by_id = {"openai": openai}
    with pytest.raises(ProviderNotConfigured):
        asyncio.run(router.execute("reasoning", {"prompt": "hello"}))

    router = CapabilityRouter(Settings(_env_file=None, openai_api_key="", anthropic_api_key="", gemini_api_key="", groq_api_key="", openrouter_api_key="", runway_api_key="x", luma_api_key="", provider_priority="runway"))
    runway = router.registry.get("runway")
    router.registry._by_id = {"runway": runway}
    with pytest.raises(CapabilityNotSupported):
        asyncio.run(router.execute("video", {"prompt": "hello"}))

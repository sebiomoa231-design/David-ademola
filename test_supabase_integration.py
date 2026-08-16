from pathlib import Path

from app.core.config import Settings
from app.core.storage import JsonStorage
from app.models import MemoryCreate, ProjectCreate
from app.services.conversation_engine import ConversationEngine
from app.services.memory_engine import MemoryEngine
from app.services.project_service import ProjectService
from app.services.supabase_service import SupabasePersistence


def test_legacy_local_fallback_remains_available(tmp_path: Path):
    settings = Settings(data_dir=str(tmp_path), supabase_persistence_enabled=False)
    storage = JsonStorage(settings.data_dir)
    memory = MemoryEngine(storage, SupabasePersistence(settings))
    created = memory.add(MemoryCreate(content="David should preserve the local compatibility path"))
    assert memory.get(created.id).content.startswith("David should preserve")

    project = ProjectService(storage, SupabasePersistence(settings)).create(ProjectCreate(name="Fallback project"))
    assert project.name == "Fallback project"
    conversation = ConversationEngine(storage, SupabasePersistence(settings)).create("Fallback conversation")
    assert conversation.title == "Fallback conversation"


def test_supabase_adapter_keeps_secret_server_side_and_generates_private_urls(monkeypatch):
    calls = []

    class FakeResponse:
        def __init__(self, payload, status_code=200):
            self._payload = payload
            self.status_code = status_code
            self.text = "ok"
            self.content = b"{}"
            self.headers = {"content-type": "application/json"}

        def json(self):
            return self._payload

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def request(self, method, url, **kwargs):
            return fake_request(method, url, **kwargs)

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if "/storage/v1/object/sign/" in url:
            return FakeResponse({"signedURL": "/object/sign/Davidai/assets/test.png?token=temporary"})
        if "/rest/v1/david_assets" in url:
            return FakeResponse([{
                "id": "asset-1",
                "owner_id": "default-owner",
                "filename": "test.png",
                "storage_path": "assets/test.png",
                "content_type": "image/png",
                "size_bytes": 3,
                "kind": "image",
                "metadata": {},
                "favorite": False,
            }])
        return FakeResponse([])

    monkeypatch.setattr("app.services.supabase_service.httpx.Client", FakeClient)
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_secret_key="server-test-secret",
        supabase_persistence_enabled=True,
    )
    persistence = SupabasePersistence(settings)
    assets = persistence.list_assets()

    assert assets[0]["signed_url"].startswith("https://example.supabase.co/storage/v1/object/sign/")
    assert calls
    for _, url, kwargs in calls:
        assert "server-test-secret" not in url
        assert kwargs["headers"]["apikey"] == "server-test-secret"
        assert kwargs["headers"]["Authorization"] == "Bearer server-test-secret"

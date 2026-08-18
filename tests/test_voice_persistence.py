import base64
from types import SimpleNamespace

from fastapi.testclient import TestClient

from main import app
from voice import engine as live_engine
import voice


client = TestClient(app)


class FakeEngine:
    async def synthesize(self, text, language_mode):
        assert text == "Persist this response"
        return SimpleNamespace(
            audio_available=True,
            provider="elevenlabs",
            text_fallback=text,
            reason=None,
            audio_base64=base64.b64encode(b"ID3real-audio").decode("ascii"),
            audio_format="mp3",
        )


class FakePersistence:
    def __init__(self, _settings):
        pass

    def upload_asset(self, **kwargs):
        assert kwargs["content"] == b"ID3real-audio"
        assert kwargs["content_type"] == "audio/mpeg"
        assert kwargs["kind"] == "audio"
        return {
            "id": "asset-voice-1",
            "filename": kwargs["filename"],
            "content_type": "audio/mpeg",
            "kind": "audio",
            "signed_url": "https://storage.example/audio/asset-voice-1",
        }


def test_synthesize_can_persist_audio_without_changing_inline_contract(monkeypatch):
    monkeypatch.setattr(voice, "engine", FakeEngine())
    monkeypatch.setattr(voice, "SupabasePersistence", FakePersistence)
    response = client.post(
        "/api/voice/synthesize",
        json={"text": "Persist this response", "language_mode": "english", "persist": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["audio_available"] is True
    assert payload["audio_base64"]
    assert payload["persisted"] is True
    assert payload["audio_url"] == "https://storage.example/audio/asset-voice-1"
    assert payload["asset"]["kind"] == "audio"

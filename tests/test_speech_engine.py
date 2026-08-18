from types import SimpleNamespace

from fastapi.testclient import TestClient

from main import app
from app.api.routes import speech_engine


client = TestClient(app)


def test_speech_engine_status_hides_credentials(monkeypatch):
    monkeypatch.setattr(
        speech_engine,
        "get_settings",
        lambda: SimpleNamespace(
            elevenlabs_api_key="secret-value",
            elevenlabs_speech_engine_id="seng-test",
            elevenlabs_speech_engine_public_ws_url="wss://david.example/api/voice/speech-engine/ws",
        ),
    )
    response = client.get("/api/voice/speech-engine/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["configured"] is True
    assert payload["engine_id"] == "seng-test"
    assert payload["public_ws_url"].startswith("wss://")
    assert "secret-value" not in response.text


def test_speech_engine_status_reports_unconfigured_without_credentials(monkeypatch):
    monkeypatch.setattr(
        speech_engine,
        "get_settings",
        lambda: SimpleNamespace(
            elevenlabs_api_key="",
            elevenlabs_speech_engine_id="",
            elevenlabs_speech_engine_public_ws_url="",
        ),
    )
    response = client.get("/api/voice/speech-engine/status")
    assert response.status_code == 200
    assert response.json()["configured"] is False


def test_sdk_base_url_removes_v1_suffix():
    assert speech_engine.SpeechEngineBridge._sdk_base_url("https://api.elevenlabs.io/v1") == "https://api.elevenlabs.io"

import base64

from fastapi.testclient import TestClient

from main import app
from app.api.routes import voice_features


client = TestClient(app)


class FakeFeatures:
    configured = True

    async def search_voices(self, *, search, page_size):
        return {
            "voices": [{"voice_id": "voice-1", "name": search or "David"}],
            "has_more": False,
            "next_page_token": None,
            "total_count": 1,
        }

    async def text_to_sound_effects(self, **kwargs):
        assert kwargs["text"] == "thunder"
        return b"sound-effect"

    async def speech_to_speech(self, **kwargs):
        assert kwargs["voice_id"] == "voice-1"
        assert kwargs["audio_bytes"] == b"source"
        return b"converted"

    async def transcribe_advanced(self, **kwargs):
        assert kwargs["audio_bytes"] == b"source"
        return {
            "text": "hello David",
            "language_code": "eng",
            "language_probability": 0.99,
            "words": [],
        }


def test_voice_capabilities_report_optional_features(monkeypatch):
    monkeypatch.setattr(voice_features, "_features", FakeFeatures())
    response = client.get("/api/voice/capabilities")
    assert response.status_code == 200
    assert "speech_to_speech" in response.json()["capabilities"]


def test_voice_search_uses_server_side_provider(monkeypatch):
    monkeypatch.setattr(voice_features, "_features", FakeFeatures())
    response = client.get("/api/voice/voices?search=jarvis")
    assert response.status_code == 200
    assert response.json()["voices"][0]["name"] == "jarvis"


def test_sound_effect_returns_base64_audio(monkeypatch):
    monkeypatch.setattr(voice_features, "_features", FakeFeatures())
    response = client.post("/api/voice/sound-effects", json={"text": "thunder"})
    assert response.status_code == 200
    assert base64.b64decode(response.json()["audio_base64"]) == b"sound-effect"


def test_voice_changer_preserves_audio_contract(monkeypatch):
    monkeypatch.setattr(voice_features, "_features", FakeFeatures())
    response = client.post(
        "/api/voice/voice-changer",
        json={
            "audio_base64": base64.b64encode(b"source").decode("ascii"),
            "voice_id": "voice-1",
            "audio_format": "audio/webm;codecs=opus",
        },
    )
    assert response.status_code == 200
    assert base64.b64decode(response.json()["audio_base64"]) == b"converted"
    assert response.json()["audio_format"] == "mp3"


def test_advanced_transcription_returns_metadata(monkeypatch):
    monkeypatch.setattr(voice_features, "_features", FakeFeatures())
    response = client.post(
        "/api/voice/transcribe/advanced",
        json={
            "audio_base64": base64.b64encode(b"source").decode("ascii"),
            "audio_format": "wav",
            "diarize": True,
            "timestamps_granularity": "word",
            "keyterms": ["David"],
        },
    )
    assert response.status_code == 200
    assert response.json()["text"] == "hello David"
    assert response.json()["provider"] == "elevenlabs"


def test_invalid_audio_is_rejected_before_provider_call(monkeypatch):
    monkeypatch.setattr(voice_features, "_features", FakeFeatures())
    response = client.post(
        "/api/voice/voice-changer",
        json={"audio_base64": "not-base64", "voice_id": "voice-1"},
    )
    assert response.status_code == 400

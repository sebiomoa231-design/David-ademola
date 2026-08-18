import base64
from types import SimpleNamespace

from fastapi.testclient import TestClient

from main import app
import voice as voice_route


client = TestClient(app)


class FakeVoiceEngine:
    stt_provider = "elevenlabs"
    tts_provider = "elevenlabs"
    SUPPORTED_LANGUAGES = ("english", "yoruba")

    async def transcribe(self, audio_bytes, language_mode, filename, **kwargs):
        assert audio_bytes == b"audio"
        assert language_mode.value == "english"
        assert filename == "audio.webm"
        assert kwargs == {
            "tag_audio_events": True,
            "diarize": True,
            "timestamps_granularity": "word",
            "keyterms": ["David"],
            "num_speakers": 2,
        }
        return SimpleNamespace(
            text="hello David",
            language="eng",
            confidence=0.98,
            provider="elevenlabs",
            raw={
                "words": [{"text": "hello"}],
                "audio_events": [{"text": "(laughter)"}],
                "language_probability": 0.98,
            },
        )


def test_primary_transcribe_exposes_scribe_metadata(monkeypatch):
    monkeypatch.setattr(voice_route, "engine", FakeVoiceEngine())
    response = client.post(
        "/api/voice/transcribe",
        json={
            "audio_base64": base64.b64encode(b"audio").decode("ascii"),
            "language": "en",
            "audio_format": "audio/webm;codecs=opus",
            "tag_audio_events": True,
            "diarize": True,
            "timestamps_granularity": "word",
            "keyterms": ["David"],
            "num_speakers": 2,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["text"] == "hello David"
    assert payload["audio_events"][0]["text"] == "(laughter)"
    assert payload["language_probability"] == 0.98

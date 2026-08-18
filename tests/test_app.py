from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_is_honest_about_scaffold_mode():
    response = client.get("/api/readiness")
    assert response.status_code == 200
    assert response.json()["mode"] == "scaffold"


def test_voice_status_is_available_without_credentials():
    response = client.get("/api/voice/status")
    assert response.status_code == 200
    assert response.json()["tts_provider"] == "elevenlabs"

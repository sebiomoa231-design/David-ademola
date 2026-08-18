from fastapi.testclient import TestClient

from app.main import app
from main import app as render_entrypoint_app


client = TestClient(app)
render_entrypoint_client = TestClient(render_entrypoint_app)


def test_render_compatible_entrypoint_exposes_health_route():
    response = render_entrypoint_client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "david-ai-backend"


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

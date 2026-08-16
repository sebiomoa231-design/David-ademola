from app.core.config import Settings
from fastapi.testclient import TestClient

from main import app


def test_default_cors_origins_include_the_local_command_center() -> None:
    settings = Settings(_env_file=None)

    assert "http://127.0.0.1:3001" in settings.cors_origin_list
    assert "http://localhost:3001" in settings.cors_origin_list


def test_cors_origins_remain_explicit_and_configurable() -> None:
    settings = Settings(
        _env_file=None,
        cors_origins="https://command.example.com, https://preview.example.com",
    )

    assert settings.cors_origin_list == [
        "https://command.example.com",
        "https://preview.example.com",
    ]


def test_local_command_center_can_read_governed_agent_records() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/intelligence/health",
        headers={"Origin": "http://127.0.0.1:3001"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3001"

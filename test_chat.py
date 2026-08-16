from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_chat():
    res = client.post("/api/chat", json={"message": "Hello"})
    assert res.status_code == 200
    assert "reply" in res.json()
    assert res.json()["capability_routing"]["execution_started"] is False


def test_chat_exposes_routing_without_starting_a_side_effect():
    res = client.post("/api/chat", json={"message": "Build a website for my business"})
    assert res.status_code == 200
    routing = res.json()["capability_routing"]
    assert routing["execution_started"] is False
    assert routing["selected"]
    assert routing["selected"]["capability_id"] == "website-development"

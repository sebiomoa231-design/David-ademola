from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_chat():
    res = client.post("/api/chat", json={"message": "Hello"})
    assert res.status_code == 200
    assert "reply" in res.json()

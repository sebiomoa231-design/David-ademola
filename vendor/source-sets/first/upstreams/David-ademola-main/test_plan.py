from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_plan():
    res = client.post("/api/plan", json={"goal": "Launch a new personal website"})
    assert res.status_code == 200
    body = res.json()
    assert body["goal"]
    assert len(body["steps"]) > 0

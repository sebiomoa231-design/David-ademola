from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_add_and_list_memory():
    create_res = client.post(
        "/api/memory",
        json={"type": "preference", "content": "Likes dark blue UI", "source": "test"},
    )
    assert create_res.status_code == 200
    memory_id = create_res.json()["id"]

    list_res = client.get("/api/memory")
    assert list_res.status_code == 200
    assert any(m["id"] == memory_id for m in list_res.json())


def test_search_memory():
    client.post(
        "/api/memory",
        json={"type": "knowledge", "content": "David AI uses FastAPI", "source": "test"},
    )
    res = client.get("/api/memory/search", params={"q": "FastAPI"})
    assert res.status_code == 200

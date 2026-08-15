from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_list_agents():
    res = client.get("/api/agents")
    assert res.status_code == 200
    names = [a["name"] for a in res.json()]
    assert "website_agent" in names


def test_dispatch_planning_agent():
    res = client.post("/api/agents/dispatch", json={"agent_name": "planning_agent", "goal": "Launch a blog"})
    assert res.status_code == 200
    body = res.json()
    assert body["state"] == "completed"
    assert len(body["steps"]) > 0


def test_voice_status():
    res = client.get("/api/voice/status")
    assert res.status_code == 200
    assert "supported_languages" in res.json()


def test_knowledge_ingest_and_search():
    ingest_res = client.post(
        "/api/knowledge/ingest",
        json={"content": "David AI uses FastAPI and Next.js", "category": "architecture"},
    )
    assert ingest_res.status_code == 200

    search_res = client.get("/api/knowledge/search", params={"q": "FastAPI"})
    assert search_res.status_code == 200
    assert len(search_res.json()) >= 1

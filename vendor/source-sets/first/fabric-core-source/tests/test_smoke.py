from fastapi.testclient import TestClient
from david_fabric.main import app

client=TestClient(app)

def test_health():
    r=client.get("/api/health")
    assert r.status_code==200
    assert r.json()["component"]=="david-ai-intelligence-fabric"

def test_capabilities():
    r=client.get("/api/intelligence/capabilities")
    assert r.status_code==200
    assert len(r.json()["capabilities"]) >= 10

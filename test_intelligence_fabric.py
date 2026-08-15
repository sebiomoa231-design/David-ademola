from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_fabric_capabilities_and_adapters_are_exposed():
    capabilities = client.get("/api/intelligence/capabilities")
    assert capabilities.status_code == 200
    ids = {item["id"] for item in capabilities.json()["capabilities"]}
    assert {
        "david-core",
        "multi-agent",
        "playwright",
        "video",
        "automation",
        "browser-use",
        "coding",
        "image",
        "voice",
        "stt",
    } <= ids

    adapters = client.get("/api/intelligence/adapters")
    assert adapters.status_code == 200
    adapter_ids = {item["id"] for item in adapters.json()["adapters"]}
    assert {
        "agent-framework",
        "playwright",
        "wan2gp",
        "n8n",
        "browser-use",
        "openhands",
        "comfyui",
        "chatterbox",
        "faster-whisper",
    } <= adapter_ids


def test_fabric_goal_plan_run_and_approval_flow():
    created = client.post(
        "/api/intelligence/goals",
        json={
            "title": "Create a browser-assisted video workflow",
            "objective": "Use Playwright browser automation and Wan2GP video generation",
            "context": {"source": "regression-test"},
        },
    )
    assert created.status_code == 200
    goal = created.json()

    planned = client.post(f"/api/intelligence/goals/{goal['id']}/plan")
    assert planned.status_code == 200
    plan = planned.json()
    capabilities = [step["capability"] for step in plan["steps"]]
    assert "playwright" in capabilities
    assert "video" in capabilities

    run = client.post("/api/intelligence/runs", json={"goal_id": goal["id"]})
    assert run.status_code == 200
    run_id = run.json()["id"]

    authorized = client.post(
        f"/api/intelligence/runs/{run_id}/authorize",
        params={"capability": "video"},
    )
    assert authorized.status_code == 200
    assert authorized.json() == {"allowed": True, "capability": "video"}

    details = client.get(f"/api/intelligence/runs/{run_id}")
    assert details.status_code == 200
    assert {event["event_type"] for event in details.json()["events"]} >= {
        "run_created",
        "approval_granted",
    }


def test_legacy_health_route_remains_available():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_external_side_effect_adapters_are_fail_closed():
    created = client.post(
        "/api/intelligence/goals",
        json={"title": "Deploy workflow", "objective": "Automate deployment"},
    )
    assert created.status_code == 200
    run = client.post(
        "/api/intelligence/runs",
        json={"goal_id": created.json()["id"], "approved": True},
    )
    assert run.status_code == 200

    denied = client.post(
        f"/api/intelligence/runs/{run.json()['id']}/authorize",
        params={"capability": "deployment-coolify"},
    )
    assert denied.status_code == 403
    assert "disabled by policy" in denied.json()["detail"]

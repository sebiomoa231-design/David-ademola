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


def test_capability_contracts_expose_agents_tools_providers_and_readiness():
    response = client.get("/api/intelligence/capabilities")
    assert response.status_code == 200
    by_id = {item["id"]: item for item in response.json()["capabilities"]}
    for capability_id in {"browser-use", "coding", "image", "voice", "stt", "research", "qa", "background-jobs"}:
        item = by_id[capability_id]
        assert item["agent"]
        assert item["skill"]
        assert item["tool"]
        assert item["provider"]
        assert item["runtime"]
        assert item["inputs"]
        assert item["outputs"]
        assert item["readiness"]
        assert item["state"] in {
            "READY",
            "CONNECTED",
            "IMPLEMENTED",
            "UNAVAILABLE",
            "REQUIRES_EXTERNAL_SERVICE",
        }


def test_dynamic_routing_returns_primary_and_fallback_chain():
    response = client.post(
        "/api/intelligence/route",
        json={"objective": "research a website with browser automation"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["candidates"]
    assert payload["selected"]["agent"]
    assert payload["selected"]["tool"]
    assert payload["fallback_chain"]


def test_native_delegation_tracks_artifact_and_verification():
    goal = client.post(
        "/api/intelligence/goals",
        json={
            "title": "Evaluate a run",
            "objective": "Evaluate the output quality",
            "context": {"requested_capability": "evaluation"},
        },
    ).json()
    run = client.post("/api/intelligence/runs", json={"goal_id": goal["id"]}).json()
    result = client.post(f"/api/intelligence/runs/{run['id']}/execute", json={}).json()
    assert result["run"]["status"] == "delegated"
    assert result["artifacts"]
    assert result["verification"]["status"] == "passed"
    details = client.get(f"/api/intelligence/runs/{run['id']}").json()
    assert details["attempts"]
    assert details["artifacts"]
    assert details["verification"]["status"] == "passed"


def test_unconfigured_external_capability_fails_without_fake_success():
    goal = client.post(
        "/api/intelligence/goals",
        json={
            "title": "Generate an image",
            "objective": "Generate an image",
            "context": {"requested_capability": "image"},
        },
    ).json()
    run = client.post("/api/intelligence/runs", json={"goal_id": goal["id"]}).json()
    result = client.post(f"/api/intelligence/runs/{run['id']}/execute", json={}).json()
    assert result["run"]["status"] == "failed"
    assert result["artifacts"] == []
    assert result["verification"]["status"] == "failed"
    assert any(event["event_type"] == "execution_failed" for event in result["events"])


def test_fallback_uses_next_configured_candidate(monkeypatch):
    from david_fabric.core.config import settings
    import david_fabric.services.execution as execution

    monkeypatch.setattr(settings, "comfyui_url", "http://comfyui.test")
    monkeypatch.setattr(settings, "creative_backend_url", "http://creative.test")
    calls = []

    async def fake_invoke(adapter, **kwargs):
        calls.append(adapter.id)
        if adapter.id == "comfyui":
            raise RuntimeError("simulated GPU worker failure")
        return {"status": "fallback-ok", "adapter": adapter.id}

    monkeypatch.setattr(execution, "invoke_adapter", fake_invoke)
    goal = client.post(
        "/api/intelligence/goals",
        json={
            "title": "Create image with fallback",
            "objective": "Create an image",
            "context": {"requested_capability": "image"},
        },
    ).json()
    run = client.post("/api/intelligence/runs", json={"goal_id": goal["id"]}).json()
    result = client.post(f"/api/intelligence/runs/{run['id']}/execute", json={}).json()
    assert calls[:2] == ["comfyui", "creative-backend"]
    assert result["run"]["status"] == "completed"
    assert result["run"]["selected_capability"] == "creative-backend"
    assert result["verification"]["status"] == "passed"


def test_readiness_marks_missing_services_truthfully(monkeypatch):
    from david_fabric.core.config import settings

    monkeypatch.setattr(settings, "comfyui_url", "")
    response = client.get("/api/intelligence/readiness")
    assert response.status_code == 200
    payload = response.json()
    service = payload["services"]["comfyui"]
    assert service["status"] == "unconfigured"
    image = next(item for item in payload["capabilities"] if item["id"] == "image")
    assert image["available"] is False
    assert "REQUIRES_EXTERNAL_SERVICE" in image["readiness"]


def test_execution_approval_enforcement_blocks_side_effects():
    goal = client.post(
        "/api/intelligence/goals",
        json={
            "title": "Run an automation workflow",
            "objective": "Run automation",
            "context": {"requested_capability": "automation"},
        },
    ).json()
    run = client.post("/api/intelligence/runs", json={"goal_id": goal["id"]}).json()
    result = client.post(f"/api/intelligence/runs/{run['id']}/execute", json={}).json()
    assert result["run"]["status"] == "blocked"
    assert result["verification"]["status"] == "blocked"
    assert "approval" in result["verification"]["message"].lower() or "side effect" in result["verification"]["message"].lower()


def test_run_request_selects_requested_capability_and_exposes_native_target():
    goal = client.post(
        "/api/intelligence/goals",
        json={"title": "Run evaluation", "objective": "Run a general task"},
    ).json()
    run = client.post(
        "/api/intelligence/runs",
        json={"goal_id": goal["id"], "requested_capability": "evaluation"},
    ).json()
    result = client.post(f"/api/intelligence/runs/{run['id']}/execute", json={}).json()
    assert result["run"]["selected_capability"] == "evaluation"
    assert result["attempt"]["output"]["dispatch_target"] == "Fabric verification engine"
    assert result["verification"]["status"] == "passed"

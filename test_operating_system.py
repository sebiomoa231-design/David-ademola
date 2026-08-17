from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from david_fabric.services.operating_system import (
    OperatingSystem,
    OperatingSystemError,
    OwnerApprovalRequired,
    PolicyBlocked,
)
from storage import JsonStorage


def make_os(tmp_path: Path) -> OperatingSystem:
    return OperatingSystem(storage=JsonStorage(str(tmp_path)), remote_enabled=False)


def test_task_graph_runs_allowlisted_action_and_emits_events(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    task = system.tasks.create(title="Check system", action="system.health", actor="owner")
    result = system.run_task(task["id"])
    assert result["status"] == "COMPLETED"
    assert result["output"]["status"] == "ok"
    assert any(event["event_type"] == "TASK_COMPLETED" for event in system.store.events())


def test_unknown_task_action_fails_without_fake_success(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    task = system.tasks.create(title="Unknown", action="shell.execute", max_retries=0, actor="owner")
    result = system.run_task(task["id"])
    assert result["status"] == "DEAD_LETTER"
    assert "No allow-listed handler" in result["error"]
    assert result.get("output") is None


def test_dependency_cycle_is_rejected(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    first = system.tasks.create(title="First", action="system.health", actor="owner")
    second = system.tasks.create(title="Second", action="system.status", depends_on=[first["id"]], actor="owner")
    first["depends_on"] = [second["id"]]
    system.store.save(first)
    with pytest.raises(OperatingSystemError) as exc:
        system.tasks.create(title="Third", action="system.health", depends_on=[first["id"]], actor="owner")
    assert exc.value.code == "dependency_cycle"


def test_workflow_builds_sequential_task_graph_but_requires_approval(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    with pytest.raises(OwnerApprovalRequired):
        system.workflows.create(name="Health workflow", steps=[{"action": "system.health"}], actor="owner")
    workflow = system.workflows.create(name="Health workflow", steps=[{"action": "system.health"}], actor="owner", approved=True)
    run = system.workflows.run(workflow["id"], system.tasks.create, actor="owner", approved=True)
    assert run["status"] == "QUEUED"
    assert len(run["task_ids"]) == 1


def test_emergency_stop_blocks_task_run_and_resume_requires_approval(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    task = system.tasks.create(title="Check system", action="system.health", actor="owner")
    with pytest.raises(OwnerApprovalRequired):
        system.policy.set_emergency_stop(True, actor="owner")
    decision = system.policy.set_emergency_stop(True, actor="owner", approved=True)
    assert decision.allowed is True
    with pytest.raises(PolicyBlocked):
        system.run_task(task["id"])
    with pytest.raises(OwnerApprovalRequired):
        system.policy.set_emergency_stop(False, actor="owner")
    assert system.policy.set_emergency_stop(False, actor="owner", approved=True).allowed is True


def test_agent_dispatch_enforces_permissions_and_loop_limits(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    result = system.agents.dispatch(
        "monitoring-agent",
        "health_check",
        {},
        lambda action, payload: {"action": action, "payload": payload},
    )
    assert result["status"] == "COMPLETED"
    loop = system.agents.dispatch(
        "monitoring-agent",
        "health_check",
        {},
        lambda action, payload: {"action": action},
        chain=["monitoring-agent"],
    )
    assert loop["status"] == "LOOP_TERMINATED"


def test_proactive_scan_deduplicates_open_signals(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    task = system.tasks.create(title="Unknown", action="missing.action", max_retries=0, actor="owner")
    system.run_task(task["id"])
    first = system.proactive_scan()
    second = system.proactive_scan()
    assert first
    assert len(first) == len(second)
    assert len(system.notifications.notifications()) == 1


def test_research_rejects_untrusted_source_and_records_valid_evidence(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    with pytest.raises(OperatingSystemError):
        system.research.record("topic", [{"url": "javascript:alert(1)"}])
    record = system.research.record("topic", [{"url": "https://example.com/docs", "title": "Docs"}], findings=["Observed"], confidence=0.8)
    assert record["status"] == "RECORDED"
    assert record["sources"][0]["url"].startswith("https://")


def test_evolution_cannot_deploy_without_owner_approval(tmp_path: Path) -> None:
    system = make_os(tmp_path)
    evolution = system.evolutions.create("Improve planner", "Planner misses dependencies", actor="owner")
    with pytest.raises(OwnerApprovalRequired):
        system.evolutions.transition(evolution["id"], "DEPLOYED", actor="owner")
    approved = system.evolutions.transition(evolution["id"], "APPROVED", actor="owner", approved=True, evidence={"tests": ["pass"]})
    assert approved["owner_approval"] is True


def test_system_routes_are_mounted_and_return_truthful_state() -> None:
    from main import app

    paths = app.openapi()["paths"]
    assert "/api/system/health" in paths
    assert "/api/tasks" in paths
    assert "/api/evolutions" in paths

    with TestClient(app) as client:
        response = client.get("/api/system/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["workers"]["uncontrolled_background"] is False if "workers" in body else True

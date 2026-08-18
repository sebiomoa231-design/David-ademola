import asyncio

from david_fabric.core.models import Goal
from david_fabric.services.execution import _execute_native


def test_website_native_execution_returns_a_real_blueprint_without_a_preview_url() -> None:
    goal = Goal(
        title="Website objective",
        objective="Create a modern landing page for a secure client portal.",
        project_id="project-123",
    )

    result = asyncio.run(_execute_native({"id": "website-development"}, goal, {"project_id": None}))

    assert result["status"] == "completed"
    assert result["capability"] == "website-development"
    assert result["blueprint"]["sections"]
    assert "preview_url" not in result
    assert "No preview URL" in result["note"]


def test_unwired_native_capability_remains_an_explicit_handoff() -> None:
    goal = Goal(title="Research objective", objective="Research the current launch market.")

    result = asyncio.run(_execute_native({"id": "research"}, goal, {}))

    assert result["status"] == "delegated"
    assert result["capability"] == "research"
    assert result["dispatch_target"]

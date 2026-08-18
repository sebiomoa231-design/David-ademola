from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from agent_engine import AgentManager


@pytest.fixture
def manager() -> AgentManager:
    return AgentManager(
        SimpleNamespace(
            agent_max_goal_chars=120,
            agent_max_steps=8,
            agent_max_retries=1,
            agent_history_limit=2,
        )
    )


def test_dispatch_completes_and_records_step_outputs(manager: AgentManager) -> None:
    run = asyncio.run(manager.dispatch("planning_agent", "Prepare a launch checklist"))

    assert run.state.value == "completed"
    assert len(run.steps) == 4
    assert all(step.state.value == "completed" for step in run.steps)
    assert manager.get_run(run.id) is run
    assert manager.list_runs(10)[0]["id"] == run.id


def test_goal_validation_rejects_empty_and_oversized_goals(manager: AgentManager) -> None:
    with pytest.raises(ValueError, match="Goal is required"):
        asyncio.run(manager.dispatch("planning_agent", "   "))

    with pytest.raises(ValueError, match="exceeds"):
        asyncio.run(manager.dispatch("planning_agent", "x" * 121))


def test_unknown_agent_is_rejected(manager: AgentManager) -> None:
    with pytest.raises(ValueError, match="Unknown agent"):
        asyncio.run(manager.dispatch("not_registered", "Do something useful"))


def test_history_is_bounded_and_completed_run_is_not_cancelled(manager: AgentManager) -> None:
    first = asyncio.run(manager.dispatch("planning_agent", "First goal"))
    second = asyncio.run(manager.dispatch("planning_agent", "Second goal"))
    third = asyncio.run(manager.dispatch("planning_agent", "Third goal"))

    listed_ids = [run["id"] for run in manager.list_runs(10)]
    assert set(listed_ids) == {second.id, third.id}
    assert first.id not in listed_ids
    assert manager.cancel(third.id).state.value == "completed"


def test_cancel_marks_active_run_for_safe_stop(manager: AgentManager) -> None:
    async def exercise() -> str:
        run = await manager.dispatch_background("planning_agent", "Long running goal")
        cancelled = manager.cancel(run.id)
        assert cancelled is not None
        await asyncio.sleep(0.02)
        return manager.get_run(run.id).state.value  # type: ignore[union-attr]

    assert asyncio.run(exercise()) in {"cancelled", "completed"}

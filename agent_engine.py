"""Bounded and observable agent execution primitives for David AI.

The engine intentionally owns lifecycle semantics, not provider credentials or tool
implementations. Concrete agents can call real services while this module guarantees
that goals and plans remain bounded, failures are visible, and every run is serializable.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable
from uuid import uuid4


UTC = timezone.utc
MAX_GOAL_LENGTH = 12_000
DEFAULT_MAX_STEPS = 8
DEFAULT_MAX_RETRIES = 1
DEFAULT_MAX_GOAL_CHARS = 12_000


class ExecutionState(str, Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    WAITING = "waiting"
    EXECUTING = "executing"
    PAUSED = "paused"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentStep:
    id: str
    title: str
    state: ExecutionState = ExecutionState.QUEUED
    output: str | None = None
    error: str | None = None
    attempts: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "state": self.state.value,
            "output": self.output,
            "error": self.error,
            "attempts": self.attempts,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class AgentRun:
    id: str
    agent_name: str
    goal: str
    steps: list[AgentStep] = field(default_factory=list)
    state: ExecutionState = ExecutionState.QUEUED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    logs: list[str] = field(default_factory=list)
    error: str | None = None
    cancel_requested: bool = False

    def log(self, message: str) -> None:
        self.logs.append(message[:2_000])
        self.updated_at = datetime.now(UTC)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "goal": self.goal,
            "state": self.state.value,
            "steps": [step.as_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "logs": list(self.logs[-100:]),
            "error": self.error,
            "cancel_requested": self.cancel_requested,
        }


ProgressCallback = Callable[[AgentRun], Awaitable[None] | None]
CancelCheck = Callable[[], bool]


class BaseAgent:
    """Base class that supplies safe execution semantics for concrete agents."""

    name: str = "base_agent"
    description: str = "Base agent"
    capabilities: list[str] = []

    def plan_steps(self, goal: str) -> list[str]:
        return [f"Handle: {goal}"]

    async def execute_step(self, step: AgentStep, goal: str) -> AgentStep:
        step.state = ExecutionState.COMPLETED
        step.output = f"No execution adapter is registered for '{step.title}'."
        return step

    def create_run(
        self,
        goal: str,
        *,
        max_steps: int = DEFAULT_MAX_STEPS,
        max_goal_chars: int = DEFAULT_MAX_GOAL_CHARS,
    ) -> AgentRun:
        clean_goal = str(goal or "").strip()
        if not clean_goal:
            raise ValueError("Goal is required")
        goal_limit = max(1, int(max_goal_chars))
        if len(clean_goal) > goal_limit:
            raise ValueError(f"Goal exceeds the {goal_limit} character limit")
        run = AgentRun(id=str(uuid4()), agent_name=self.name, goal=clean_goal, state=ExecutionState.PLANNING)
        planned = [str(title).strip() for title in self.plan_steps(clean_goal) if str(title).strip()]
        run.steps = [AgentStep(id=str(uuid4()), title=title[:500]) for title in planned[:max(1, max_steps)]]
        if len(planned) > max_steps:
            run.log(f"Plan truncated to the configured maximum of {max_steps} steps.")
        run.log(f"Planned {len(run.steps)} step(s) for goal.")
        return run

    async def run(
        self,
        goal: str,
        *,
        run: AgentRun | None = None,
        max_steps: int = DEFAULT_MAX_STEPS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_goal_chars: int = DEFAULT_MAX_GOAL_CHARS,
        cancel_check: CancelCheck | None = None,
        on_update: ProgressCallback | None = None,
    ) -> AgentRun:
        run = run or self.create_run(goal, max_steps=max_steps, max_goal_chars=max_goal_chars)
        run.state = ExecutionState.EXECUTING
        run.log("Execution started.")
        retries = max(0, min(int(max_retries), 5))

        async def notify() -> None:
            if on_update:
                result = on_update(run)
                if asyncio.iscoroutine(result):
                    await result

        for step in run.steps:
            if cancel_check and cancel_check():
                run.cancel_requested = True
            if run.cancel_requested:
                step.state = ExecutionState.CANCELLED
                run.state = ExecutionState.CANCELLED
                run.log("Execution cancelled before the next step.")
                run.completed_at = datetime.now(UTC)
                await notify()
                return run

            step.state = ExecutionState.EXECUTING
            step.started_at = datetime.now(UTC)
            await notify()
            succeeded = False
            for attempt in range(retries + 1):
                step.attempts = attempt + 1
                try:
                    if attempt:
                        run.state = ExecutionState.RETRYING
                        run.log(f"Retrying step: {step.title} (attempt {attempt + 1}).")
                    else:
                        run.state = ExecutionState.EXECUTING
                    result = await self.execute_step(step, run.goal)
                    if result.state == ExecutionState.CANCELLED:
                        run.cancel_requested = True
                        break
                    if result.state == ExecutionState.FAILED:
                        raise RuntimeError(result.error or f"Step failed: {step.title}")
                    step.state = ExecutionState.COMPLETED
                    step.completed_at = datetime.now(UTC)
                    run.log(f"Completed step: {step.title}.")
                    succeeded = True
                    break
                except Exception as exc:  # pragma: no cover - defensive branch covered by tests with a failing agent
                    step.error = str(exc)[:1_000]
                    run.log(f"Step attempt failed: {step.title} ({step.error}).")
                    if attempt >= retries:
                        break
            if run.cancel_requested:
                step.state = ExecutionState.CANCELLED
                run.state = ExecutionState.CANCELLED
                run.log("Execution cancelled by request.")
                run.completed_at = datetime.now(UTC)
                await notify()
                return run
            if not succeeded:
                step.state = ExecutionState.FAILED
                run.state = ExecutionState.FAILED
                run.error = step.error or f"Step failed: {step.title}"
                run.log("Execution stopped after an unrecoverable step failure.")
                run.completed_at = datetime.now(UTC)
                await notify()
                return run
            await notify()

        run.state = ExecutionState.COMPLETED
        run.completed_at = datetime.now(UTC)
        run.log("Execution completed successfully.")
        await notify()
        return run


class WebsiteAgent(BaseAgent):
    name = "website_agent"
    description = "Plans website generation and clearly reports provider-bound execution steps"
    capabilities = ["website_generation", "deployment"]

    def plan_steps(self, goal: str) -> list[str]:
        return [
            "Analyze requirements",
            "Generate site structure",
            "Generate components and styles",
            "Run build verification",
            "Request deployment approval",
        ]

    async def execute_step(self, step: AgentStep, goal: str) -> AgentStep:
        step.output = {
            "step": step.title,
            "goal": goal[:500],
            "status": "planned",
            "next": "Connect a configured website provider before generating or deploying artifacts.",
        }
        step.state = ExecutionState.COMPLETED
        return step


class PlanningAgent(BaseAgent):
    name = "planning_agent"
    description = "Breaks a stated goal into bounded milestones and ordered steps"
    capabilities = ["planning", "goal_decomposition"]

    def plan_steps(self, goal: str) -> list[str]:
        return ["Clarify goal", "Break into milestones", "Order steps by dependency", "Define success criteria"]

    async def execute_step(self, step: AgentStep, goal: str) -> AgentStep:
        step.output = f"{step.title} completed for: {goal[:500]}"
        step.state = ExecutionState.COMPLETED
        return step


class AgentManager:
    """Registry and lifecycle manager for bounded agent runs.

    Runs are retained in process memory for compatibility with the existing app. The
    manager exposes an explicit history limit and stable serialization so a persistent
    store can be added later without changing the HTTP contract.
    """

    def __init__(self, settings: Any | None = None) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._runs: dict[str, AgentRun] = {}
        self._tasks: dict[str, asyncio.Task[AgentRun]] = {}
        self._cancel_requested: set[str] = set()
        self._max_goal_chars = max(1, int(getattr(settings, "agent_max_goal_chars", DEFAULT_MAX_GOAL_CHARS)))
        self._max_steps = max(1, int(getattr(settings, "agent_max_steps", DEFAULT_MAX_STEPS)))
        self._max_retries = max(0, int(getattr(settings, "agent_max_retries", DEFAULT_MAX_RETRIES)))
        self._history_limit = max(1, int(getattr(settings, "agent_history_limit", 100)))
        self.register(WebsiteAgent())
        self.register(PlanningAgent())

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def list_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": agent.name, "description": agent.description, "capabilities": list(agent.capabilities)}
            for agent in self._agents.values()
        ]

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        bounded = max(1, min(int(limit), self._history_limit))
        runs = sorted(self._runs.values(), key=lambda item: item.created_at, reverse=True)
        return [run.as_dict() for run in runs[:bounded]]

    def get_run(self, run_id: str) -> AgentRun | None:
        return self._runs.get(run_id)

    def all_runs(self) -> list[AgentRun]:
        return list(self._runs.values())

    def _remember(self, run: AgentRun) -> None:
        self._runs[run.id] = run
        ordered = sorted(self._runs.values(), key=lambda item: item.created_at, reverse=True)
        for stale in ordered[self._history_limit :]:
            self._runs.pop(stale.id, None)

    async def _execute(self, agent: BaseAgent, run: AgentRun) -> AgentRun:
        try:
            result = await agent.run(
                run.goal,
                run=run,
                max_steps=self._max_steps,
                max_retries=self._max_retries,
                max_goal_chars=self._max_goal_chars,
                cancel_check=lambda: run.id in self._cancel_requested,
            )
            return result
        finally:
            self._cancel_requested.discard(run.id)
            self._tasks.pop(run.id, None)
            self._remember(run)

    async def dispatch(self, agent_name: str, goal: str) -> AgentRun:
        agent = self._agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        run = agent.create_run(goal, max_steps=self._max_steps, max_goal_chars=self._max_goal_chars)
        self._remember(run)
        return await self._execute(agent, run)

    async def dispatch_background(self, agent_name: str, goal: str) -> AgentRun:
        agent = self._agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        run = agent.create_run(goal, max_steps=self._max_steps, max_goal_chars=self._max_goal_chars)
        self._remember(run)
        task = asyncio.create_task(self._execute(agent, run), name=f"david-agent-{run.id}")
        self._tasks[run.id] = task
        return run

    def cancel(self, run_id: str) -> AgentRun | None:
        run = self._runs.get(run_id)
        if not run:
            return None
        if run.state in {ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED}:
            return run
        self._cancel_requested.add(run_id)
        run.cancel_requested = True
        run.log("Cancellation requested.")
        return run

    async def shutdown(self) -> None:
        tasks = list(self._tasks.values())
        for run_id in list(self._tasks):
            self.cancel(run_id)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()
        self._cancel_requested.clear()

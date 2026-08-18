from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


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


@dataclass
class AgentRun:
    id: str
    agent_name: str
    goal: str
    steps: list[AgentStep] = field(default_factory=list)
    state: ExecutionState = ExecutionState.QUEUED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    logs: list[str] = field(default_factory=list)


class BaseAgent:
    """
    Base class for a David AI agent. Concrete agents (WebsiteAgent,
    PlanningAgent, etc.) override `plan_steps()` to break a goal into
    named steps and `execute_step()` to actually perform each step.
    This base only handles bookkeeping (run state, logs) so agents
    stay small and focused.
    """

    name: str = "base_agent"
    description: str = "Base agent"
    capabilities: list[str] = []

    def plan_steps(self, goal: str) -> list[str]:
        """Returns an ordered list of step titles for the given goal.
        Concrete agents override this; the default is a single step."""
        return [f"Handle: {goal}"]

    async def execute_step(self, step: AgentStep, goal: str) -> AgentStep:
        """Executes one step. The base implementation is a no-op that
        marks the step complete; real agents override this to call
        actual services (website engine, content engine, etc.)."""
        step.state = ExecutionState.COMPLETED
        step.output = f"No execution logic implemented yet for '{step.title}'."
        return step

    async def run(self, goal: str) -> AgentRun:
        run = AgentRun(id=str(uuid4()), agent_name=self.name, goal=goal, state=ExecutionState.PLANNING)
        run.logs.append(f"Planning steps for goal: {goal}")

        for title in self.plan_steps(goal):
            run.steps.append(AgentStep(id=str(uuid4()), title=title))

        run.state = ExecutionState.EXECUTING
        for step in run.steps:
            try:
                await self.execute_step(step, goal)
                run.logs.append(f"Completed step: {step.title}")
            except Exception as exc:  # pragma: no cover - defensive
                step.state = ExecutionState.FAILED
                step.error = str(exc)
                run.logs.append(f"Failed step: {step.title} ({exc})")
                run.state = ExecutionState.FAILED
                run.updated_at = datetime.utcnow()
                return run

        run.state = ExecutionState.COMPLETED
        run.updated_at = datetime.utcnow()
        return run


class WebsiteAgent(BaseAgent):
    name = "website_agent"
    description = "Plans and (eventually) executes website generation and deployment"
    capabilities = ["website_generation", "deployment"]

    def plan_steps(self, goal: str) -> list[str]:
        return [
            "Analyze requirements",
            "Generate site structure",
            "Generate components and styles",
            "Run build verification",
            "Deploy (requires configured deployment provider)",
        ]


class PlanningAgent(BaseAgent):
    name = "planning_agent"
    description = "Breaks a stated goal into milestones and ordered steps"
    capabilities = ["planning"]

    def plan_steps(self, goal: str) -> list[str]:
        return ["Clarify goal", "Break into milestones", "Order steps by dependency"]


class AgentManager:
    """
    Registers agents, starts runs, and keeps a history of runs in
    memory (per-process). A production version would persist runs via
    JsonStorage the same way other services do; kept in-memory here
    since agent runs are inherently ephemeral until execution logic
    for each agent is implemented against real services.
    """

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._runs: dict[str, AgentRun] = {}
        self.register(WebsiteAgent())
        self.register(PlanningAgent())

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def list_agents(self) -> list[dict]:
        return [
            {"name": a.name, "description": a.description, "capabilities": a.capabilities}
            for a in self._agents.values()
        ]

    async def dispatch(self, agent_name: str, goal: str) -> AgentRun:
        agent = self._agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        run = await agent.run(goal)
        self._runs[run.id] = run
        return run

    def get_run(self, run_id: str) -> AgentRun | None:
        return self._runs.get(run_id)

    def all_runs(self) -> list[AgentRun]:
        return list(self._runs.values())

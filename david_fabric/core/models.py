from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


READINESS_STATES = {
    "IMPLEMENTED",
    "CONNECTED",
    "CONFIGURED",
    "HEALTHY",
    "READY",
    "UNAVAILABLE",
    "REQUIRES_EXTERNAL_SERVICE",
    "REQUIRES_CREDENTIAL",
    "REQUIRES_GPU",
    "REQUIRES_APPROVAL",
}


class GoalCreate(BaseModel):
    title: str
    objective: str
    project_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class Goal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    objective: str
    project_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    status: str = "created"
    created_at: str = Field(default_factory=now)


class PlanStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    capability: str
    depends_on: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    status: str = "planned"
    agent: str | None = None
    skill: str | None = None
    tool: str | None = None
    provider: str | None = None
    adapter: str | None = None
    fallback_capabilities: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    readiness: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GoalPlan(BaseModel):
    goal_id: str
    steps: list[PlanStep]
    generated_at: str = Field(default_factory=now)


class RunCreate(BaseModel):
    goal_id: str
    approved: bool = False
    objective: str | None = None
    requested_capability: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)


class Run(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal_id: str
    status: str = "queued"
    approved: bool = False
    objective: str | None = None
    requested_capability: str | None = None
    selected_capability: str | None = None
    selected_agent: str | None = None
    selected_tool: str | None = None
    selected_provider: str | None = None
    attempts: list[str] = Field(default_factory=list)
    failure_reason: str | None = None
    created_at: str = Field(default_factory=now)
    completed_at: str | None = None


class CapabilitySelectionRequest(BaseModel):
    objective: str = Field(min_length=1)
    requested_capability: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class CapabilityCandidate(BaseModel):
    capability_id: str
    name: str
    category: str | None = None
    score: int = 0
    agent: str | None = None
    skill: str | None = None
    tool: str | None = None
    provider: str | None = None
    adapter: str | None = None
    mode: str | None = None
    readiness: list[str] = Field(default_factory=list)
    state: str = "UNAVAILABLE"
    available: bool = False
    reason: str | None = None
    fallback_capabilities: list[str] = Field(default_factory=list)


class CapabilitySelectionResponse(BaseModel):
    objective: str
    candidates: list[CapabilityCandidate]
    selected: CapabilityCandidate | None = None
    fallback_chain: list[str] = Field(default_factory=list)


class GovernedRequest(BaseModel):
    """A natural-language request that is planned before any action can run."""

    objective: str = Field(min_length=1, max_length=4000)
    title: str | None = Field(default=None, max_length=160)
    requested_capability: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    execute: bool = False
    approved: bool = False
    input: dict[str, Any] = Field(default_factory=dict)


class GovernedRequestResponse(BaseModel):
    status: str
    route: CapabilitySelectionResponse
    goal: Goal | None = None
    plan: GoalPlan | None = None
    run: Run | None = None
    result: "RunResult | None" = None


class ExecutionRequest(BaseModel):
    objective: str | None = None
    requested_capability: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    approved: bool = False


class ExecutionAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    capability_id: str
    agent: str | None = None
    tool: str | None = None
    provider: str | None = None
    adapter: str | None = None
    status: str = "queued"
    readiness: list[str] = Field(default_factory=list)
    error: str | None = None
    output: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now)
    finished_at: str | None = None


class Artifact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    attempt_id: str | None = None
    name: str
    kind: str
    uri: str | None = None
    content_type: str | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now)


class Verification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    attempt_id: str | None = None
    status: str = "pending"
    checks: list[dict[str, Any]] = Field(default_factory=list)
    message: str | None = None
    created_at: str = Field(default_factory=now)


class RunResult(BaseModel):
    run: Run
    attempt: ExecutionAttempt | None = None
    artifacts: list[Artifact] = Field(default_factory=list)
    verification: Verification | None = None
    events: list[dict[str, Any]] = Field(default_factory=list)

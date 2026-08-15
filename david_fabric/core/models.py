from typing import Any, Literal
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat()

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
    metadata: dict[str, Any] = Field(default_factory=dict)

class GoalPlan(BaseModel):
    goal_id: str
    steps: list[PlanStep]
    generated_at: str = Field(default_factory=now)

class RunCreate(BaseModel):
    goal_id: str
    approved: bool = False

class Run(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal_id: str
    status: str = "queued"
    approved: bool = False
    created_at: str = Field(default_factory=now)

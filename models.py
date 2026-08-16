from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

MemoryType = Literal[
    "preference",
    "instruction",
    "decision",
    "project",
    "knowledge",
    "experience",
    "task",
    "conversation",
    "general",
]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: Optional[str] = None
    provider: str = "fallback"


class MemoryCreate(BaseModel):
    type: MemoryType = "general"
    content: str
    confidence: float = 0.8
    importance: float = 0.6
    source: str = "user"
    tags: list[str] = Field(default_factory=list)


class MemoryItem(MemoryCreate):
    id: str
    status: Literal["active", "archived"] = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    goals: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    milestones: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class ProjectItem(ProjectCreate):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(BaseModel):
    project_id: str = ""
    title: str
    notes: str = ""
    status: Literal["todo", "doing", "done"] = "todo"


class TaskItem(TaskCreate):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationItem(BaseModel):
    id: str
    title: str
    messages: list[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlanRequest(BaseModel):
    goal: str
    context: str = ""


class PlanStep(BaseModel):
    id: str
    title: str
    description: str
    depends_on: list[str] = Field(default_factory=list)


class PlanResponse(BaseModel):
    goal: str
    milestones: list[str]
    steps: list[PlanStep]
    estimated_phases: int


class AssetItem(BaseModel):
    id: str
    owner_id: str = "default-owner"
    project_id: Optional[str] = None
    filename: str
    storage_path: str
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    kind: Literal["image", "video", "audio", "document", "website", "other"] = "other"
    metadata: dict = Field(default_factory=dict)
    favorite: bool = False
    signed_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GenerationCreate(BaseModel):
    project_id: Optional[str] = None
    asset_id: Optional[str] = None
    kind: Literal["image", "video", "audio", "document", "website", "other"] = "other"
    prompt: str = ""
    provider: str = "unknown"
    status: str = "completed"
    output: str = ""
    metadata: dict = Field(default_factory=dict)


class GenerationItem(GenerationCreate):
    id: str
    owner_id: str = "default-owner"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FavoriteRequest(BaseModel):
    favorite: bool = True


class SupabaseStatus(BaseModel):
    configured: bool
    database_enabled: bool
    storage_bucket: str
    migration_required: bool = False

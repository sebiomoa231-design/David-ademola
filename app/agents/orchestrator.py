"""David AI — Multi-Agent Orchestration System.

Master orchestrator that delegates work to specialized sub-agents,
manages sub-tasks, and coordinates complex multi-step workflows.

Sub-agents:
- Research Agent: web search, fact-checking, data gathering
- Coding Agent: code generation, debugging, deployment
- Creative Agent: content creation, image/video/audio generation
- Communication Agent: email, social media, notifications
- Planning Agent: goal decomposition, scheduling, project management
- Memory Agent: knowledge retrieval, context assembly, learning
- System Agent: diagnostics, provider health, self-monitoring
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Specialized roles for sub-agents."""
    MASTER = "master_orchestrator"
    RESEARCH = "research_agent"
    CODING = "coding_agent"
    CREATIVE = "creative_agent"
    COMMUNICATION = "communication_agent"
    PLANNING = "planning_agent"
    MEMORY = "memory_agent"
    SYSTEM = "system_agent"


class TaskStatus(str, Enum):
    """Status of a sub-task."""
    QUEUED = "queued"
    PLANNED = "planned"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Priority levels for sub-tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class SubTask:
    """A unit of work delegated to a sub-agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_task_id: Optional[str] = None
    agent_role: AgentRole = AgentRole.MASTER
    objective: str = ""
    context: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.QUEUED
    priority: TaskPriority = TaskPriority.NORMAL
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    dependencies: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at) * 1000
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "parent_task_id": self.parent_task_id,
            "agent_role": self.agent_role.value,
            "objective": self.objective,
            "status": self.status.value,
            "priority": self.priority.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "dependencies": self.dependencies,
        }


@dataclass
class AgentPlan:
    """A plan decomposed into ordered sub-tasks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    objective: str = ""
    tasks: list[SubTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PLANNED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objective": self.objective,
            "status": self.status.value,
            "total_tasks": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            "tasks": [t.to_dict() for t in self.tasks],
        }


class SubAgent:
    """Base class for specialized sub-agents."""

    def __init__(self, role: AgentRole, ai_router=None):
        self.role = role
        self.ai_router = ai_router
        self.active_tasks: list[SubTask] = []
        self.completed_tasks: list[SubTask] = []

    @property
    def name(self) -> str:
        return self.role.value.replace("_", " ").title()

    @property
    def is_busy(self) -> bool:
        return any(t.status == TaskStatus.RUNNING for t in self.active_tasks)

    async def execute(self, task: SubTask) -> SubTask:
        """Execute a sub-task. Override in specialized agents."""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()

        try:
            if self.ai_router is None:
                task.error = f"{self.name} has no AI router configured."
                task.status = TaskStatus.FAILED
                return task

            # Build a contextual prompt for the sub-agent
            prompt = self._build_prompt(task)
            result = await self.ai_router.generate(prompt)

            task.result = result.text
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.metadata["provider_used"] = result.provider

        except Exception as exc:
            task.error = str(exc)
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            logger.error(f"{self.name} failed task {task.id}: {exc}")

        self.completed_tasks.append(task)
        return task

    def _build_prompt(self, task: SubTask) -> str:
        """Build a role-specific prompt for the AI provider."""
        role_instructions = AGENT_SYSTEM_PROMPTS.get(self.role, "")
        context_str = ""
        if task.context:
            context_str = f"\n\nContext: {task.context}"

        return f"{role_instructions}\n\nTask: {task.objective}{context_str}"

    def get_status(self) -> dict:
        return {
            "role": self.role.value,
            "name": self.name,
            "is_busy": self.is_busy,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
        }


# System prompts for each specialized agent
AGENT_SYSTEM_PROMPTS = {
    AgentRole.RESEARCH: (
        "You are David AI's Research Agent. Your role is to gather information, "
        "verify facts, search for data, and provide well-sourced answers. "
        "Be thorough, cite sources when possible, and flag uncertainty."
    ),
    AgentRole.CODING: (
        "You are David AI's Coding Agent. Your role is to write, debug, review, "
        "and deploy code. Follow best practices, write clean and documented code, "
        "and explain your implementation decisions."
    ),
    AgentRole.CREATIVE: (
        "You are David AI's Creative Agent. Your role is to generate creative content "
        "including writing, marketing copy, social media posts, scripts, and creative "
        "briefs. Be original, engaging, and aligned with David's brand voice."
    ),
    AgentRole.COMMUNICATION: (
        "You are David AI's Communication Agent. Your role is to draft emails, "
        "compose messages, manage social media content, and handle notifications. "
        "Be professional, clear, and context-aware."
    ),
    AgentRole.PLANNING: (
        "You are David AI's Planning Agent. Your role is to break down complex goals "
        "into actionable steps, create project plans, set milestones, and manage "
        "dependencies. Be structured and realistic about timelines."
    ),
    AgentRole.MEMORY: (
        "You are David AI's Memory Agent. Your role is to retrieve relevant context, "
        "manage knowledge, identify patterns in past interactions, and maintain "
        "David's personal knowledge base. Be precise and relevant."
    ),
    AgentRole.SYSTEM: (
        "You are David AI's System Agent. Your role is to monitor system health, "
        "diagnose issues, check provider status, and maintain the AI operating system. "
        "Be technical, precise, and proactive about potential issues."
    ),
}


class MasterOrchestrator:
    """The Master Orchestrator coordinates all sub-agents.

    It receives high-level objectives, decomposes them into sub-tasks,
    assigns them to the appropriate sub-agents, manages dependencies,
    and synthesizes final results.
    """

    def __init__(self, ai_router=None):
        self.ai_router = ai_router
        self.agents: dict[AgentRole, SubAgent] = {
            role: SubAgent(role=role, ai_router=ai_router)
            for role in AgentRole
            if role != AgentRole.MASTER
        }
        self.plans: list[AgentPlan] = []
        self.task_history: list[SubTask] = []

    def detect_required_agents(self, message: str) -> list[AgentRole]:
        """Detect which sub-agents are needed based on the user's message."""
        message_lower = message.lower()
        required = []

        # Research indicators
        research_keywords = ["search", "find", "look up", "research", "what is", "who is",
                           "when did", "how does", "explain", "tell me about", "information"]
        if any(kw in message_lower for kw in research_keywords):
            required.append(AgentRole.RESEARCH)

        # Coding indicators
        code_keywords = ["code", "program", "build", "develop", "debug", "fix bug",
                        "deploy", "api", "function", "script", "database", "github"]
        if any(kw in message_lower for kw in code_keywords):
            required.append(AgentRole.CODING)

        # Creative indicators
        creative_keywords = ["create", "design", "write", "generate", "content",
                           "video", "image", "audio", "music", "brand", "logo"]
        if any(kw in message_lower for kw in creative_keywords):
            required.append(AgentRole.CREATIVE)

        # Communication indicators
        comm_keywords = ["email", "send", "message", "notify", "social media",
                        "post", "tweet", "youtube", "tiktok", "gmail"]
        if any(kw in message_lower for kw in comm_keywords):
            required.append(AgentRole.COMMUNICATION)

        # Planning indicators
        plan_keywords = ["plan", "schedule", "organize", "project", "milestone",
                        "deadline", "timeline", "roadmap", "strategy", "goal"]
        if any(kw in message_lower for kw in plan_keywords):
            required.append(AgentRole.PLANNING)

        # Memory indicators
        memory_keywords = ["remember", "recall", "last time", "previously",
                         "you said", "i told you", "my preference", "history"]
        if any(kw in message_lower for kw in memory_keywords):
            required.append(AgentRole.MEMORY)

        # System indicators
        system_keywords = ["status", "health", "diagnostic", "provider", "system",
                         "performance", "error", "monitor", "check"]
        if any(kw in message_lower for kw in system_keywords):
            required.append(AgentRole.SYSTEM)

        # Default to research if nothing detected
        if not required:
            required.append(AgentRole.RESEARCH)

        return required

    async def process(self, message: str, context: Optional[dict] = None) -> dict:
        """Process a user message through the orchestration system.

        1. Detect intent and required agents
        2. Create a plan with sub-tasks
        3. Execute sub-tasks (respecting dependencies)
        4. Synthesize results
        5. Return unified response
        """
        context = context or {}

        # Step 1: Detect required agents
        required_agents = self.detect_required_agents(message)
        logger.info(f"Orchestrator: detected agents needed: {[a.value for a in required_agents]}")

        # Step 2: Create plan
        plan = AgentPlan(objective=message)

        # Create sub-tasks for each required agent
        for i, agent_role in enumerate(required_agents):
            task = SubTask(
                parent_task_id=plan.id,
                agent_role=agent_role,
                objective=message,
                context=context,
                priority=TaskPriority.NORMAL if i > 0 else TaskPriority.HIGH,
            )
            plan.tasks.append(task)

        self.plans.append(plan)

        # Step 3: Execute sub-tasks
        plan.status = TaskStatus.RUNNING
        results = await self._execute_plan(plan)

        # Step 4: Synthesize results
        plan.status = TaskStatus.COMPLETED
        response = self._synthesize_results(plan, results)

        return response

    async def _execute_plan(self, plan: AgentPlan) -> list[SubTask]:
        """Execute all tasks in a plan, handling dependencies and parallelism."""
        completed = []

        # Group tasks by dependency level (tasks without deps run in parallel)
        independent_tasks = [t for t in plan.tasks if not t.dependencies]
        dependent_tasks = [t for t in plan.tasks if t.dependencies]

        # Execute independent tasks in parallel
        if independent_tasks:
            parallel_results = await asyncio.gather(
                *[self._execute_task(task) for task in independent_tasks],
                return_exceptions=True,
            )
            for result in parallel_results:
                if isinstance(result, SubTask):
                    completed.append(result)

        # Execute dependent tasks sequentially
        for task in dependent_tasks:
            # Check if dependencies are met
            dep_ids = set(task.dependencies)
            completed_ids = {t.id for t in completed if t.status == TaskStatus.COMPLETED}
            if dep_ids.issubset(completed_ids):
                result = await self._execute_task(task)
                completed.append(result)
            else:
                task.status = TaskStatus.BLOCKED
                task.error = "Dependencies not met"
                completed.append(task)

        self.task_history.extend(completed)
        return completed

    async def _execute_task(self, task: SubTask) -> SubTask:
        """Execute a single sub-task using the appropriate agent."""
        agent = self.agents.get(task.agent_role)
        if agent is None:
            task.status = TaskStatus.FAILED
            task.error = f"No agent available for role: {task.agent_role.value}"
            return task

        return await agent.execute(task)

    def _synthesize_results(self, plan: AgentPlan, results: list[SubTask]) -> dict:
        """Combine results from multiple sub-agents into a unified response."""
        successful_results = [t for t in results if t.status == TaskStatus.COMPLETED]
        failed_results = [t for t in results if t.status == TaskStatus.FAILED]

        # Combine successful results
        if successful_results:
            # If only one agent responded, use its result directly
            if len(successful_results) == 1:
                combined_text = successful_results[0].result or ""
            else:
                # Multiple agents: combine their outputs
                parts = []
                for task in successful_results:
                    if task.result:
                        parts.append(task.result)
                combined_text = "\n\n".join(parts)
        else:
            combined_text = "I wasn't able to complete this request. All sub-agents encountered errors."

        # Build response metadata
        agents_used = [t.agent_role.value for t in results]
        providers_used = [t.metadata.get("provider_used", "unknown") for t in successful_results]

        return {
            "text": combined_text,
            "plan_id": plan.id,
            "objective": plan.objective,
            "agents_used": agents_used,
            "providers_used": providers_used,
            "tasks_completed": len(successful_results),
            "tasks_failed": len(failed_results),
            "total_tasks": len(results),
            "task_details": [t.to_dict() for t in results],
        }

    def get_status(self) -> dict:
        """Get the orchestrator's current status."""
        return {
            "agents": {
                role.value: agent.get_status()
                for role, agent in self.agents.items()
            },
            "active_plans": len([p for p in self.plans if p.status == TaskStatus.RUNNING]),
            "total_plans": len(self.plans),
            "total_tasks_processed": len(self.task_history),
        }

    def get_agent_status(self, role: AgentRole) -> Optional[dict]:
        """Get status for a specific agent."""
        agent = self.agents.get(role)
        if agent:
            return agent.get_status()
        return None

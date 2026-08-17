"""Governed operating-system services for David AI.

This module is intentionally additive. It reuses the existing JSON storage,
Supabase persistence, provider registry, and memory engine while supplying the
missing durable concepts required by the Phase 6–8 operating-system contract:
tasks, objectives, agents, workflows, events, signals, notifications,
resource observations, circuit breakers, policy decisions, and controlled
Evolution records.

The module never executes arbitrary code from a request. Task actions are
allow-listed and high-risk actions are blocked until owner approval is present.
"""
from __future__ import annotations

import os
import resource
import shutil
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.services.provider_registry import ProviderRegistry
from app.services.supabase_service import SupabasePersistence
from memory_engine import MemoryEngine
from storage import JsonStorage


UTC = timezone.utc

TASK_STATUSES = {
    "QUEUED", "RUNNING", "RETRYING", "COMPLETED", "FAILED", "CANCELLED",
    "DEAD_LETTER", "PAUSED", "BLOCKED",
}
EVENT_TYPES = {
    "TASK_CREATED", "TASK_STARTED", "TASK_COMPLETED", "TASK_FAILED",
    "TASK_PAUSED", "TASK_RESUMED", "TASK_CANCELLED", "PROVIDER_FAILED",
    "DEPLOYMENT_FAILED", "EVOLUTION_CREATED", "EVOLUTION_COMPLETED",
    "EVOLUTION_FAILED", "SECURITY_ALERT", "MEMORY_UPDATED",
    "CAPABILITY_GAP_DETECTED", "SIGNAL_CREATED", "NOTIFICATION_CREATED",
    "AGENT_STARTED", "AGENT_COMPLETED", "AGENT_FAILED", "WORKFLOW_STARTED",
    "WORKFLOW_COMPLETED", "WORKFLOW_FAILED", "JOB_DEAD_LETTERED",
    "SYSTEM_STOPPED", "SYSTEM_RESUMED", "RESOURCE_LIMIT_REACHED",
    "CIRCUIT_OPENED", "CIRCUIT_CLOSED", "APPROVAL_GRANTED", "APPROVAL_REJECTED",
}
TRUST_LEVELS = {"UNTRUSTED", "LIMITED", "STANDARD", "PRIVILEGED", "OWNER_APPROVED"}
HEALTH_STATES = {"ACTIVE", "ON_TRACK", "AT_RISK", "BLOCKED", "INACTIVE", "COMPLETED", "ABANDONED"}


class OperatingSystemError(RuntimeError):
    def __init__(self, message: str, *, code: str = "operating_system_error", status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class PolicyBlocked(OperatingSystemError):
    def __init__(self, message: str = "Policy blocked this action") -> None:
        super().__init__(message, code="policy_blocked", status_code=403)


class OwnerApprovalRequired(PolicyBlocked):
    def __init__(self, action: str) -> None:
        super().__init__(f"Owner approval is required for {action}")
        self.code = "owner_approval_required"


class ResourceLimitReached(OperatingSystemError):
    def __init__(self, message: str = "Operation exceeded a configured resource limit") -> None:
        super().__init__(message, code="resource_limit_reached", status_code=429)


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    actor: str
    risk: str
    allowed: bool
    requires_approval: bool
    reason: str
    emergency_stop: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "actor": self.actor,
            "risk": self.risk,
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reason": self.reason,
            "emergency_stop": self.emergency_stop,
        }


class OperatingStore:
    """Typed-record persistence with explicit local/remote modes.

    Supabase is used only when the existing persistence flag is enabled. Local
    JSON is a real development/test fallback and never silently replaces an
    enabled remote database after a remote write/read error.
    """

    def __init__(self, storage: JsonStorage | None = None, settings: Settings | None = None, *, remote_enabled: bool | None = None) -> None:
        self.storage = storage or JsonStorage()
        self.settings = settings or get_settings()
        self.persistence = SupabasePersistence(self.settings)
        self.remote_enabled = self.persistence.database_enabled if remote_enabled is None else bool(remote_enabled)
        self._lock = threading.RLock()

    def _client(self) -> Any | None:
        if not self.remote_enabled:
            return None
        return self.persistence.require_database()

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    def init(self) -> None:
        for name in ("operating_records", "operating_events", "operating_audit"):
            self.storage.read(name, [])

    def _local_records(self) -> list[dict[str, Any]]:
        value = self.storage.read("operating_records", [])
        return value if isinstance(value, list) else []

    def save(self, record: dict[str, Any]) -> dict[str, Any]:
        item = dict(record)
        item.setdefault("id", str(uuid4()))
        item.setdefault("created_at", self._now())
        item["updated_at"] = self._now()
        client = self._client()
        if client is not None:
            payload = {
                "id": item["id"],
                "owner_id": "default-owner",
                "entity_type": item["entity_type"],
                "status": item.get("status"),
                "project_id": item.get("project_id"),
                "parent_id": item.get("parent_id"),
                "name": item.get("name"),
                "payload": item,
                "due_at": item.get("due_at"),
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
            }
            client.upsert("david_operating_records", payload, "id")
            return item
        with self._lock:
            rows = self._local_records()
            replaced = False
            for index, current in enumerate(rows):
                if isinstance(current, dict) and current.get("id") == item["id"]:
                    rows[index] = item
                    replaced = True
                    break
            if not replaced:
                rows.append(item)
            self.storage.write("operating_records", rows)
        return item

    def get(self, record_id: str) -> dict[str, Any] | None:
        client = self._client()
        if client is not None:
            rows = client.select("david_operating_records", {"select": "payload", "id": f"eq.{record_id}", "limit": "1"})
            return dict((rows[0] or {}).get("payload") or {}) if rows else None
        return next((dict(row) for row in self._local_records() if isinstance(row, dict) and row.get("id") == record_id), None)

    def list(self, entity_type: str | None = None, *, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        client = self._client()
        if client is not None:
            params: dict[str, str] = {"select": "payload", "limit": str(limit), "order": "updated_at.desc"}
            if entity_type:
                params["entity_type"] = f"eq.{entity_type}"
            if status:
                params["status"] = f"eq.{status}"
            rows = client.select("david_operating_records", params)
            return [dict(row.get("payload") or {}) for row in rows if isinstance(row, dict)]
        rows = [row for row in self._local_records() if isinstance(row, dict)]
        if entity_type:
            rows = [row for row in rows if row.get("entity_type") == entity_type]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        rows.sort(key=lambda row: str(row.get("updated_at") or row.get("created_at") or ""), reverse=True)
        return rows[:limit]

    def delete(self, record_id: str) -> bool:
        client = self._client()
        if client is not None:
            return bool(client.delete("david_operating_records", {"id": f"eq.{record_id}"}))
        with self._lock:
            rows = self._local_records()
            remaining = [row for row in rows if row.get("id") != record_id]
            if len(remaining) == len(rows):
                return False
            self.storage.write("operating_records", remaining)
            return True

    def event(self, event_type: str, payload: dict[str, Any], *, actor: str = "david", correlation: dict[str, Any] | None = None) -> dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise OperatingSystemError("Unsupported event type", code="invalid_event_type", status_code=422)
        event = {
            "id": str(uuid4()),
            "event_type": event_type,
            "payload": dict(payload),
            "actor": actor,
            "correlation": dict(correlation or {}),
            "created_at": self._now(),
        }
        client = self._client()
        if client is not None:
            client.insert("david_operating_events", {"id": event["id"], "owner_id": "default-owner", **event})
        else:
            self.storage.append("operating_events", event, [])
        return event

    def events(self, *, event_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        client = self._client()
        if client is not None:
            params: dict[str, str] = {"select": "*", "limit": str(limit), "order": "created_at.desc"}
            if event_type:
                params["event_type"] = f"eq.{event_type}"
            return client.select("david_operating_events", params)
        rows = self.storage.read("operating_events", [])
        rows = rows if isinstance(rows, list) else []
        if event_type:
            rows = [row for row in rows if row.get("event_type") == event_type]
        return list(reversed(rows[-limit:]))

    def audit(self, action: str, *, actor: str, decision: PolicyDecision, result: str, payload: dict[str, Any] | None = None, correlation: dict[str, Any] | None = None) -> dict[str, Any]:
        item = {
            "id": str(uuid4()),
            "action": action,
            "actor": actor,
            "policy_decision": decision.as_dict(),
            "result": result,
            "payload": dict(payload or {}),
            "correlation": dict(correlation or {}),
            "created_at": self._now(),
        }
        client = self._client()
        if client is not None:
            client.insert("david_operating_audit", {"id": item["id"], "owner_id": "default-owner", **item})
        else:
            self.storage.append("operating_audit", item, [])
        return item

    def audits(self, limit: int = 100) -> list[dict[str, Any]]:
        client = self._client()
        if client is not None:
            return client.select("david_operating_audit", {"select": "*", "limit": str(max(1, min(int(limit), 500))), "order": "created_at.desc"})
        rows = self.storage.read("operating_audit", [])
        return list(reversed(rows[-max(1, min(int(limit), 500)):])) if isinstance(rows, list) else []


class PolicyEngine:
    """Central policy-as-data gate for every privileged operation."""

    DEFAULTS: dict[str, dict[str, Any]] = {
        "task.create": {"risk": "low", "approval": False},
        "task.run": {"risk": "low", "approval": False},
        "task.cancel": {"risk": "medium", "approval": False},
        "workflow.run": {"risk": "medium", "approval": True},
        "evolution.create": {"risk": "medium", "approval": False},
        "evolution.approve": {"risk": "high", "approval": True},
        "deployment.create": {"risk": "high", "approval": True},
        "deployment.rollback": {"risk": "high", "approval": True},
        "automation.create": {"risk": "medium", "approval": True},
        "automation.run": {"risk": "medium", "approval": True},
        "agent.secret_access": {"risk": "critical", "approval": True},
        "agent.modify_permissions": {"risk": "critical", "approval": True},
        "system.stop": {"risk": "high", "approval": True},
        "system.resume": {"risk": "high", "approval": True},
    }

    def __init__(self, store: OperatingStore) -> None:
        self.store = store
        self._state = {"emergency_stop": False, "autonomous_mode": False}

    def snapshot(self) -> dict[str, Any]:
        return {"rules": self.DEFAULTS, **self._state}

    def set_emergency_stop(self, enabled: bool, *, actor: str, approved: bool = False) -> PolicyDecision:
        action = "system.stop" if enabled else "system.resume"
        decision = self.require(action, actor=actor, approved=approved)
        self._state["emergency_stop"] = bool(enabled)
        self.store.event("SYSTEM_STOPPED" if enabled else "SYSTEM_RESUMED", {"enabled": enabled}, actor=actor)
        return decision

    def set_autonomous_mode(self, enabled: bool, *, actor: str, approved: bool = False) -> PolicyDecision:
        decision = self.require("automation.run", actor=actor, approved=approved)
        self._state["autonomous_mode"] = bool(enabled)
        return decision

    def evaluate(self, action: str, *, actor: str, approved: bool = False, risk: str | None = None, resource: str | None = None) -> PolicyDecision:
        rule = dict(self.DEFAULTS.get(action, {"risk": "medium", "approval": True}))
        resolved_risk = risk or str(rule.get("risk", "medium"))
        requires = bool(rule.get("approval")) or resolved_risk in {"high", "critical"}
        if self._state.get("emergency_stop") and action not in {"system.resume", "system.stop"}:
            return PolicyDecision(action, actor, resolved_risk, False, requires, "Emergency stop is active", True)
        if requires and not approved:
            return PolicyDecision(action, actor, resolved_risk, False, True, "Owner approval is required")
        if actor.startswith("agent:") and resolved_risk in {"high", "critical"} and not approved:
            return PolicyDecision(action, actor, resolved_risk, False, True, "Agent cannot perform a high-risk action without owner approval")
        return PolicyDecision(action, actor, resolved_risk, True, requires, "Policy allows the action")

    def require(self, action: str, *, actor: str, approved: bool = False, risk: str | None = None) -> PolicyDecision:
        decision = self.evaluate(action, actor=actor, approved=approved, risk=risk)
        if not decision.allowed:
            self.store.audit(action, actor=actor, decision=decision, result="blocked")
            if decision.requires_approval:
                raise OwnerApprovalRequired(action)
            raise PolicyBlocked(decision.reason)
        self.store.audit(action, actor=actor, decision=decision, result="allowed")
        return decision


class TaskManager:
    def __init__(self, store: OperatingStore, policy: PolicyEngine, events: OperatingStore) -> None:
        self.store = store
        self.policy = policy
        self.events = events

    def list(self, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.list("task", status=status, limit=limit)

    def get(self, task_id: str) -> dict[str, Any] | None:
        return self.store.get(task_id)

    def _detect_cycle(self, task_id: str, dependencies: list[str]) -> bool:
        graph: dict[str, list[str]] = {row["id"]: list(row.get("depends_on") or []) for row in self.list(limit=500)}
        graph[task_id] = list(dependencies)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> bool:
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            for dep in graph.get(node, []):
                if visit(dep):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        return visit(task_id)

    def create(self, *, title: str, action: str, payload: dict[str, Any] | None = None, depends_on: list[str] | None = None, project_id: str | None = None, objective_id: str | None = None, due_at: str | None = None, max_retries: int = 3, risk: str = "low", actor: str = "owner", approved: bool = False) -> dict[str, Any]:
        self.policy.require("task.create", actor=actor, approved=approved, risk=risk)
        dependencies = list(dict.fromkeys(depends_on or []))
        for dep in dependencies:
            if not self.get(dep):
                raise OperatingSystemError(f"Task dependency does not exist: {dep}", code="missing_dependency", status_code=422)
        task_id = str(uuid4())
        if self._detect_cycle(task_id, dependencies):
            raise OperatingSystemError("Task dependency cycle detected", code="dependency_cycle", status_code=422)
        task = {
            "id": task_id,
            "entity_type": "task",
            "title": title.strip(),
            "name": title.strip(),
            "action": action.strip(),
            "payload": dict(payload or {}),
            "depends_on": dependencies,
            "project_id": project_id,
            "objective_id": objective_id,
            "due_at": due_at,
            "max_retries": max(0, min(int(max_retries), 10)),
            "attempts": 0,
            "status": "BLOCKED" if dependencies else "QUEUED",
            "checkpoint": None,
            "output": None,
            "error": None,
            "risk": risk,
            "created_at": self.store._now(),
        }
        item = self.store.save(task)
        self.events.event("TASK_CREATED", {"task_id": task_id, "action": action}, actor=actor, correlation={"task_id": task_id})
        return item

    def _dependencies_ready(self, task: dict[str, Any]) -> bool:
        for dep_id in task.get("depends_on") or []:
            dep = self.get(dep_id)
            if not dep or dep.get("status") != "COMPLETED":
                return False
        return True

    def checkpoint(self, task_id: str, checkpoint: dict[str, Any], *, actor: str = "owner") -> dict[str, Any]:
        task = self.get(task_id)
        if not task:
            raise OperatingSystemError("Task not found", code="not_found", status_code=404)
        task["checkpoint"] = dict(checkpoint)
        task["updated_by"] = actor
        return self.store.save(task)

    def transition(self, task_id: str, status: str, *, actor: str = "owner", reason: str | None = None, approved: bool = False) -> dict[str, Any]:
        status = status.upper()
        if status not in TASK_STATUSES:
            raise OperatingSystemError("Invalid task status", code="invalid_status", status_code=422)
        task = self.get(task_id)
        if not task:
            raise OperatingSystemError("Task not found", code="not_found", status_code=404)
        if status in {"CANCELLED", "PAUSED"}:
            self.policy.require("task.cancel", actor=actor, approved=approved, risk=task.get("risk"))
        task["status"] = status
        if reason:
            task["reason"] = reason
        saved = self.store.save(task)
        event_map = {"PAUSED": "TASK_PAUSED", "QUEUED": "TASK_RESUMED", "CANCELLED": "TASK_CANCELLED"}
        if status in event_map:
            self.events.event(event_map[status], {"task_id": task_id, "reason": reason}, actor=actor, correlation={"task_id": task_id})
        return saved

    def run(self, task_id: str, executor: Callable[[str, dict[str, Any]], dict[str, Any]], *, actor: str = "owner", approved: bool = False) -> dict[str, Any]:
        task = self.get(task_id)
        if not task:
            raise OperatingSystemError("Task not found", code="not_found", status_code=404)
        if task.get("status") in {"COMPLETED", "CANCELLED", "DEAD_LETTER"}:
            return task
        if self.policy.snapshot().get("emergency_stop"):
            raise PolicyBlocked("Emergency stop is active")
        if not self._dependencies_ready(task):
            task["status"] = "BLOCKED"
            task["reason"] = "Dependencies are not complete"
            return self.store.save(task)
        self.policy.require("task.run", actor=actor, approved=approved, risk=task.get("risk"))
        task["status"] = "RUNNING"
        task["attempts"] = int(task.get("attempts") or 0) + 1
        task["started_at"] = self.store._now()
        self.store.save(task)
        self.events.event("TASK_STARTED", {"task_id": task_id, "attempt": task["attempts"]}, actor=actor, correlation={"task_id": task_id})
        try:
            result = executor(str(task.get("action")), dict(task.get("payload") or {}))
            if not isinstance(result, dict):
                raise OperatingSystemError("Task handler returned an invalid result", code="invalid_handler_result", status_code=500)
        except Exception as exc:
            task["error"] = str(exc)[:500]
            task["status"] = "RETRYING" if task["attempts"] <= int(task.get("max_retries") or 0) else "DEAD_LETTER"
            self.store.save(task)
            self.events.event("JOB_DEAD_LETTERED" if task["status"] == "DEAD_LETTER" else "TASK_FAILED", {"task_id": task_id, "error": task["error"], "status": task["status"]}, actor=actor, correlation={"task_id": task_id})
            return task
        task["status"] = "COMPLETED"
        task["output"] = result
        task["completed_at"] = self.store._now()
        self.store.save(task)
        self.events.event("TASK_COMPLETED", {"task_id": task_id, "output": {"keys": sorted(result.keys())}}, actor=actor, correlation={"task_id": task_id})
        return task


DEFAULT_AGENTS = (
    {"agent_id": "david-orchestrator", "name": "David Orchestrator", "purpose": "Coordinates governed tasks and agent handoffs", "permissions": ["plan", "delegate", "validate", "observe"], "tools": ["task-graph", "event-bus", "policy-engine"], "model": "native", "version": "1.0", "risk_level": "standard", "trust_level": "STANDARD"},
    {"agent_id": "research-agent", "name": "Research Agent", "purpose": "Reads approved sources and records evidence", "permissions": ["research", "read_approved_sources", "analyze", "observe"], "tools": ["research-registry", "capability-registry"], "model": "provider-router", "version": "1.0", "risk_level": "low", "trust_level": "LIMITED"},
    {"agent_id": "coding-agent", "name": "Coding Agent", "purpose": "Proposes sandbox-scoped code changes", "permissions": ["sandbox_write", "run_tests", "read_repo", "propose_patch"], "tools": ["sandbox", "test-runner", "git"], "model": "provider-router", "version": "1.0", "risk_level": "medium", "trust_level": "LIMITED"},
    {"agent_id": "testing-agent", "name": "Testing Agent", "purpose": "Runs approved tests and validates outputs", "permissions": ["run_tests", "read_artifacts", "observe"], "tools": ["test-runner", "verification"], "model": "native", "version": "1.0", "risk_level": "low", "trust_level": "STANDARD"},
    {"agent_id": "security-agent", "name": "Security Agent", "purpose": "Reviews permissions, dependencies, and secret boundaries", "permissions": ["security_scan", "read_audit", "observe"], "tools": ["security-policy", "audit-log"], "model": "native", "version": "1.0", "risk_level": "standard", "trust_level": "STANDARD"},
    {"agent_id": "deployment-agent", "name": "Deployment Agent", "purpose": "Prepares and monitors deployments; cannot deploy without approval", "permissions": ["prepare_deployment", "read_deployment", "rollback_proposal", "observe"], "tools": ["github", "render", "rollback"], "model": "native", "version": "1.0", "risk_level": "high", "trust_level": "LIMITED"},
    {"agent_id": "monitoring-agent", "name": "Monitoring Agent", "purpose": "Observes health, resources, providers, and incidents", "permissions": ["observe", "health_check", "create_signal"], "tools": ["health", "resource-monitor", "event-bus"], "model": "native", "version": "1.0", "risk_level": "low", "trust_level": "STANDARD"},
    {"agent_id": "data-agent", "name": "Data Agent", "purpose": "Analyzes permitted records without secret access", "permissions": ["read_project_data", "analyze", "observe"], "tools": ["memory", "project-health"], "model": "provider-router", "version": "1.0", "risk_level": "low", "trust_level": "LIMITED"},
)


class AgentRegistry:
    def __init__(self, store: OperatingStore, policy: PolicyEngine, events: OperatingStore) -> None:
        self.store = store
        self.policy = policy
        self.events = events
        for agent in DEFAULT_AGENTS:
            existing = self.store.list("agent", limit=500)
            if not any(item.get("agent_id") == agent["agent_id"] for item in existing):
                self.store.save({"id": agent["agent_id"], "entity_type": "agent", "status": "ACTIVE", "health": "unknown", "last_used": None, "success_rate": None, **agent})

    def list(self) -> list[dict[str, Any]]:
        return self.store.list("agent", limit=100)

    def get(self, agent_id: str) -> dict[str, Any] | None:
        for agent in self.list():
            if agent.get("agent_id") == agent_id or agent.get("id") == agent_id:
                return agent
        return None

    def select(self, capability: str, *, preferred: str | None = None) -> dict[str, Any]:
        agents = self.list()
        if preferred:
            candidate = self.get(preferred)
            if candidate and candidate.get("status") == "ACTIVE":
                return candidate
        for agent in agents:
            permissions = set(agent.get("permissions") or [])
            if capability in permissions or "observe" in permissions:
                return agent
        raise OperatingSystemError("No suitable agent is registered", code="agent_unavailable", status_code=503)

    def dispatch(self, agent_id: str, action: str, payload: dict[str, Any], executor: Callable[[str, dict[str, Any]], dict[str, Any]], *, actor: str = "owner", approved: bool = False, chain: list[str] | None = None, max_calls: int = 8, max_depth: int = 4) -> dict[str, Any]:
        agent = self.get(agent_id)
        if not agent:
            raise OperatingSystemError("Agent not found", code="agent_not_found", status_code=404)
        chain = list(chain or [])
        if len(chain) >= max_depth or len(chain) >= max_calls or agent_id in chain:
            self.events.event("AGENT_FAILED", {"agent_id": agent_id, "reason": "loop_limit"}, actor=actor)
            return {"status": "LOOP_TERMINATED", "agent_id": agent_id, "chain": chain}
        if action in {"deployment.create", "deployment.rollback", "agent.secret_access", "agent.modify_permissions"}:
            self.policy.require(action, actor=f"agent:{agent_id}", approved=approved)
        required_permission = action.split(".", 1)[0]
        permissions = set(agent.get("permissions") or [])
        if required_permission not in permissions and action not in permissions and "observe" not in permissions:
            self.events.event("AGENT_FAILED", {"agent_id": agent_id, "reason": "permission_denied", "action": action}, actor=actor)
            raise PolicyBlocked(f"Agent {agent_id} lacks permission for {action}")
        run_id = str(uuid4())
        run = {"id": run_id, "entity_type": "agent_run", "agent_id": agent_id, "action": action, "status": "RUNNING", "chain": chain + [agent_id], "attempts": 1, "created_at": self.store._now()}
        self.store.save(run)
        self.events.event("AGENT_STARTED", {"run_id": run_id, "agent_id": agent_id, "action": action}, actor=actor, correlation={"agent_id": agent_id})
        try:
            output = executor(action, payload)
            run.update({"status": "COMPLETED", "output": output, "completed_at": self.store._now()})
            self.events.event("AGENT_COMPLETED", {"run_id": run_id, "agent_id": agent_id}, actor=actor, correlation={"agent_id": agent_id})
        except Exception as exc:
            run.update({"status": "FAILED", "error": str(exc)[:500], "completed_at": self.store._now()})
            self.events.event("AGENT_FAILED", {"run_id": run_id, "agent_id": agent_id, "error": str(exc)[:300]}, actor=actor, correlation={"agent_id": agent_id})
        self.store.save(run)
        return run


class ObjectiveManager:
    def __init__(self, store: OperatingStore, policy: PolicyEngine) -> None:
        self.store = store
        self.policy = policy

    def list(self) -> list[dict[str, Any]]:
        return self.store.list("objective", limit=100)

    def create(self, title: str, description: str, *, priority: int = 50, resources: list[str] | None = None, deadline: str | None = None, actor: str = "owner", approved: bool = False) -> dict[str, Any]:
        self.policy.require("task.create", actor=actor, approved=approved)
        resources = list(dict.fromkeys(resources or []))
        conflicts = self.conflicts(resources)
        item = self.store.save({"id": str(uuid4()), "entity_type": "objective", "title": title.strip(), "name": title.strip(), "description": description.strip(), "priority": max(0, min(int(priority), 100)), "resources": resources, "deadline": deadline, "status": "ACTIVE", "conflicts": conflicts, "created_at": self.store._now()})
        return item

    def conflicts(self, resources: list[str]) -> list[dict[str, Any]]:
        wanted = set(resources)
        conflicts: list[dict[str, Any]] = []
        for objective in self.list():
            if objective.get("status") not in {"ACTIVE", "AT_RISK"}:
                continue
            overlap = wanted.intersection(objective.get("resources") or [])
            if overlap:
                conflicts.append({"objective_id": objective.get("id"), "resources": sorted(overlap), "resolution": "prioritize_or_ask_owner"})
        return conflicts

    def milestone(self, objective_id: str, title: str, *, due_at: str | None = None) -> dict[str, Any]:
        if not any(item.get("id") == objective_id for item in self.list()):
            raise OperatingSystemError("Objective not found", code="not_found", status_code=404)
        return self.store.save({"id": str(uuid4()), "entity_type": "milestone", "objective_id": objective_id, "title": title.strip(), "name": title.strip(), "due_at": due_at, "status": "QUEUED", "created_at": self.store._now()})


class WorkflowManager:
    def __init__(self, store: OperatingStore, policy: PolicyEngine) -> None:
        self.store = store
        self.policy = policy

    def list(self) -> list[dict[str, Any]]:
        return self.store.list("workflow", limit=100)

    def create(self, name: str, steps: list[dict[str, Any]], *, version: int = 1, owner_approval: bool = True, actor: str = "owner", approved: bool = False) -> dict[str, Any]:
        if not steps:
            raise OperatingSystemError("Workflow requires at least one step", code="invalid_workflow", status_code=422)
        self.policy.require("automation.create", actor=actor, approved=approved)
        allowed = [{"action": str(step.get("action") or "").strip(), "payload": dict(step.get("payload") or {}), "risk": str(step.get("risk") or "low")} for step in steps]
        if any(not step["action"] for step in allowed):
            raise OperatingSystemError("Workflow steps require actions", code="invalid_workflow", status_code=422)
        return self.store.save({"id": str(uuid4()), "entity_type": "workflow", "name": name.strip(), "version": max(1, int(version)), "steps": allowed, "owner_approval": bool(owner_approval), "status": "ACTIVE", "created_at": self.store._now()})

    def run(self, workflow_id: str, task_creator: Callable[..., dict[str, Any]], *, actor: str = "owner", approved: bool = False) -> dict[str, Any]:
        workflow = self.store.get(workflow_id)
        if not workflow or workflow.get("entity_type") != "workflow":
            raise OperatingSystemError("Workflow not found", code="not_found", status_code=404)
        self.policy.require("workflow.run", actor=actor, approved=approved)
        task_ids: list[str] = []
        previous: str | None = None
        for step in workflow.get("steps") or []:
            task = task_creator(title=f"{workflow['name']}: {step['action']}", action=step["action"], payload=step.get("payload"), depends_on=[previous] if previous else [], risk=step.get("risk", "low"), actor=actor, approved=approved)
            task_ids.append(task["id"])
            previous = task["id"]
        run = self.store.save({"id": str(uuid4()), "entity_type": "workflow_run", "workflow_id": workflow_id, "status": "QUEUED", "task_ids": task_ids, "created_at": self.store._now()})
        return run


class Scheduler:
    def __init__(self, store: OperatingStore, policy: PolicyEngine) -> None:
        self.store = store
        self.policy = policy

    def list(self) -> list[dict[str, Any]]:
        return self.store.list("schedule", limit=100)

    def create(self, name: str, action: str, *, interval_seconds: int | None = None, cron: str | None = None, enabled: bool = True, actor: str = "owner", approved: bool = False) -> dict[str, Any]:
        if not interval_seconds and not cron:
            raise OperatingSystemError("Schedule requires interval_seconds or cron", code="invalid_schedule", status_code=422)
        self.policy.require("automation.create", actor=actor, approved=approved)
        next_run = datetime.now(UTC) + timedelta(seconds=max(1, int(interval_seconds or 3600))) if interval_seconds else None
        return self.store.save({"id": str(uuid4()), "entity_type": "schedule", "name": name.strip(), "action": action.strip(), "interval_seconds": interval_seconds, "cron": cron, "enabled": bool(enabled), "next_run_at": next_run.isoformat() if next_run else None, "created_at": self.store._now()})

    def due(self, now: datetime | None = None) -> list[dict[str, Any]]:
        current = now or datetime.now(UTC)
        due: list[dict[str, Any]] = []
        for schedule in self.list():
            if not schedule.get("enabled") or not schedule.get("next_run_at"):
                continue
            try:
                if datetime.fromisoformat(schedule["next_run_at"]) <= current:
                    due.append(schedule)
            except (TypeError, ValueError):
                continue
        return due


class ResearchRegistry:
    def __init__(self, store: OperatingStore) -> None:
        self.store = store

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.list("research", limit=limit)

    def record(self, topic: str, sources: list[dict[str, Any]], *, findings: list[str] | None = None, confidence: float | None = None, license_notes: list[str] | None = None, actor: str = "owner") -> dict[str, Any]:
        clean_sources = []
        for source in sources:
            url = str(source.get("url") or "").strip()
            if not url or not (url.startswith("https://") or url.startswith("http://")):
                raise OperatingSystemError("Research sources must contain valid HTTP(S) URLs", code="invalid_source", status_code=422)
            clean_sources.append({"url": url, "title": str(source.get("title") or ""), "publisher": str(source.get("publisher") or ""), "retrieved_at": source.get("retrieved_at") or datetime.now(UTC).isoformat()})
        return self.store.save({"id": str(uuid4()), "entity_type": "research", "topic": topic.strip(), "sources": clean_sources, "findings": list(findings or []), "confidence": confidence, "license_notes": list(license_notes or []), "status": "RECORDED", "created_at": self.store._now(), "actor": actor})

    def gap(self, capability: str, evidence: dict[str, Any], *, severity: str = "medium", actor: str = "david") -> dict[str, Any]:
        item = self.store.save({"id": str(uuid4()), "entity_type": "capability_gap", "capability": capability, "evidence": dict(evidence), "severity": severity, "status": "OPEN", "created_at": self.store._now(), "actor": actor})
        self.store.event("CAPABILITY_GAP_DETECTED", {"gap_id": item["id"], "capability": capability}, actor=actor)
        return item


class NotificationManager:
    def __init__(self, store: OperatingStore) -> None:
        self.store = store

    def signals(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.list("signal", limit=limit)

    def notifications(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.list("notification", limit=limit)

    def signal(self, kind: str, reason: str, evidence: dict[str, Any], *, severity: str = "info", importance: int = 50, urgency: int = 50, confidence: float = 0.5, recommendation: str | None = None, level: int = 1, actor: str = "david") -> dict[str, Any]:
        fingerprint = f"{kind}:{reason}:{sorted(evidence.items())}"
        existing = next((item for item in self.signals(500) if item.get("fingerprint") == fingerprint and item.get("status") == "OPEN"), None)
        if existing:
            return existing
        signal = self.store.save({"id": str(uuid4()), "entity_type": "signal", "kind": kind, "reason": reason, "evidence": dict(evidence), "recommendation": recommendation, "severity": severity, "importance": importance, "urgency": urgency, "confidence": confidence, "level": max(0, min(4, int(level))), "fingerprint": fingerprint, "status": "OPEN", "created_at": self.store._now(), "actor": actor})
        self.store.event("SIGNAL_CREATED", {"signal_id": signal["id"], "kind": kind}, actor=actor)
        notification = self.store.save({"id": str(uuid4()), "entity_type": "notification", "signal_id": signal["id"], "title": reason, "message": recommendation or reason, "severity": severity, "status": "UNREAD", "created_at": self.store._now()})
        self.store.event("NOTIFICATION_CREATED", {"notification_id": notification["id"], "signal_id": signal["id"]}, actor=actor)
        return signal


class ResourceMonitor:
    def __init__(self, store: OperatingStore) -> None:
        self.store = store

    def observe(self, *, task_id: str | None = None, actor: str = "monitoring-agent") -> dict[str, Any]:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        disk = shutil.disk_usage(Path(get_settings().data_dir))
        observation = self.store.save({"id": str(uuid4()), "entity_type": "resource_observation", "cpu_user_seconds": usage.ru_utime, "cpu_system_seconds": usage.ru_stime, "memory_max_rss": usage.ru_maxrss, "storage_total": disk.total, "storage_used": disk.used, "storage_free": disk.free, "task_id": task_id, "created_at": self.store._now(), "status": "RECORDED", "actor": actor})
        return observation


class CircuitBreaker:
    def __init__(self, store: OperatingStore, *, threshold: int = 3, cooldown_seconds: int = 60) -> None:
        self.store = store
        self.threshold = max(1, threshold)
        self.cooldown_seconds = max(1, cooldown_seconds)

    def state(self, name: str) -> dict[str, Any]:
        item = next((row for row in self.store.list("circuit_breaker", limit=500) if row.get("name") == name), None)
        if not item:
            return {"name": name, "state": "CLOSED", "failures": 0, "opened_at": None}
        if item.get("state") == "OPEN" and item.get("opened_at"):
            try:
                if datetime.fromisoformat(item["opened_at"]) + timedelta(seconds=self.cooldown_seconds) <= datetime.now(UTC):
                    item["state"] = "HALF_OPEN"
                    self.store.save(item)
            except (ValueError, TypeError):
                pass
        return item

    def allow(self, name: str) -> bool:
        return self.state(name).get("state") in {"CLOSED", "HALF_OPEN"}

    def success(self, name: str) -> dict[str, Any]:
        item = self.state(name)
        item.update({"id": item.get("id") or str(uuid4()), "entity_type": "circuit_breaker", "name": name, "state": "CLOSED", "failures": 0, "opened_at": None, "updated_at": self.store._now()})
        self.store.save(item)
        self.store.event("CIRCUIT_CLOSED", {"name": name}, actor="david")
        return item

    def failure(self, name: str, error: str) -> dict[str, Any]:
        item = self.state(name)
        failures = int(item.get("failures") or 0) + 1
        opened = failures >= self.threshold
        item.update({"id": item.get("id") or str(uuid4()), "entity_type": "circuit_breaker", "name": name, "state": "OPEN" if opened else "CLOSED", "failures": failures, "last_error": error[:300], "opened_at": self.store._now() if opened else item.get("opened_at"), "updated_at": self.store._now()})
        self.store.save(item)
        if opened:
            self.store.event("CIRCUIT_OPENED", {"name": name, "error": error[:300]}, actor="david")
        return item


class EvolutionManager:
    """Controlled software-change lifecycle; no production mutation is automatic."""

    STATES = {"PROPOSED", "PLANNED", "SANDBOX", "TESTING", "SECURITY_REVIEW", "APPROVAL_REQUIRED", "APPROVED", "COMMITTED", "DEPLOYED", "MONITORING", "ROLLED_BACK", "FAILED", "CANCELLED"}

    def __init__(self, store: OperatingStore, policy: PolicyEngine, events: OperatingStore) -> None:
        self.store = store
        self.policy = policy
        self.events = events

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.list("evolution", limit=limit)

    def create(self, title: str, problem: str, *, scope: list[str] | None = None, risk: str = "medium", actor: str = "owner") -> dict[str, Any]:
        item = self.store.save({"id": str(uuid4()), "entity_type": "evolution", "title": title.strip(), "problem": problem.strip(), "scope": list(scope or []), "risk": risk, "state": "PROPOSED", "status": "ACTIVE", "attempts": 0, "owner_approval": False, "created_at": self.store._now(), "actor": actor})
        self.events.event("EVOLUTION_CREATED", {"evolution_id": item["id"], "risk": risk}, actor=actor, correlation={"evolution_id": item["id"]})
        return item

    def transition(self, evolution_id: str, state: str, *, actor: str = "owner", approved: bool = False, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
        if state not in self.STATES:
            raise OperatingSystemError("Invalid evolution state", code="invalid_state", status_code=422)
        item = self.store.get(evolution_id)
        if not item or item.get("entity_type") != "evolution":
            raise OperatingSystemError("Evolution not found", code="not_found", status_code=404)
        if state in {"APPROVED", "DEPLOYED", "ROLLED_BACK"}:
            self.policy.require("evolution.approve" if state == "APPROVED" else "deployment.create", actor=actor, approved=approved, risk=item.get("risk", "medium"))
        item["state"] = state
        item.setdefault("evidence", {})
        if evidence:
            item["evidence"].update(evidence)
        if state == "APPROVED":
            item["owner_approval"] = True
        if state == "FAILED":
            item["failure_reason"] = (evidence or {}).get("reason")
            self.events.event("EVOLUTION_FAILED", {"evolution_id": evolution_id, "reason": item.get("failure_reason")}, actor=actor, correlation={"evolution_id": evolution_id})
        if state == "DEPLOYED":
            self.events.event("EVOLUTION_COMPLETED", {"evolution_id": evolution_id}, actor=actor, correlation={"evolution_id": evolution_id})
        return self.store.save(item)


class OperatingSystem:
    def __init__(self, *, storage: JsonStorage | None = None, settings: Settings | None = None, remote_enabled: bool | None = None) -> None:
        self.settings = settings or get_settings()
        self.store = OperatingStore(storage=storage, settings=self.settings, remote_enabled=remote_enabled)
        self.store.init()
        self.policy = PolicyEngine(self.store)
        self.tasks = TaskManager(self.store, self.policy, self.store)
        self.agents = AgentRegistry(self.store, self.policy, self.store)
        self.objectives = ObjectiveManager(self.store, self.policy)
        self.workflows = WorkflowManager(self.store, self.policy)
        self.scheduler = Scheduler(self.store, self.policy)
        self.research = ResearchRegistry(self.store)
        self.notifications = NotificationManager(self.store)
        self.resources = ResourceMonitor(self.store)
        self.circuits = CircuitBreaker(self.store)
        self.evolutions = EvolutionManager(self.store, self.policy, self.store)
        self.providers = ProviderRegistry(self.settings)
        self.memory = MemoryEngine(JsonStorage(self.settings.data_dir), SupabasePersistence(self.settings))
        self._handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            "system.health": lambda _payload: self.health(),
            "system.status": lambda _payload: self.status(),
            "provider.health": lambda _payload: {"providers": self.providers.list()},
            "capability.discover": lambda _payload: {"providers": self.providers.list(), "capabilities": sorted({cap for row in self.providers.list() for cap in row.get("capabilities", [])})},
            "resource.observe": lambda payload: self.resources.observe(task_id=payload.get("task_id")),
            "memory.context": lambda payload: self.context(str(payload.get("query") or ""), project_id=payload.get("project_id"), task_id=payload.get("task_id")),
            "notifications.process": lambda _payload: {"notifications": self.notifications.notifications()},
        }
        self.last_known_good = self.store.list("production_version", limit=1)

    def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        handler = self._handlers.get(action)
        if handler is None:
            raise OperatingSystemError(f"No allow-listed handler for {action}", code="unknown_action", status_code=422)
        return handler(payload)

    def run_task(self, task_id: str, *, actor: str = "owner", approved: bool = False) -> dict[str, Any]:
        return self.tasks.run(task_id, lambda action, payload: self.execute(action, payload), actor=actor, approved=approved)

    def context(self, query: str, *, project_id: str | None = None, task_id: str | None = None, limit: int = 8) -> dict[str, Any]:
        memories = []
        if query.strip():
            try:
                memories = [item.model_dump(mode="json") for item in self.memory.relevant(query, limit=max(1, min(limit, 20)))]
            except Exception:
                memories = []
        relevant_records = []
        if project_id:
            relevant_records.extend(self.store.list("task", limit=100))
            relevant_records = [item for item in relevant_records if item.get("project_id") == project_id]
        if task_id:
            task = self.store.get(task_id)
            if task:
                relevant_records.insert(0, task)
        return {"query": query, "project_id": project_id, "task_id": task_id, "memories": memories, "records": relevant_records[:limit], "confidence": 0.7 if memories or relevant_records else 0.0}

    def project_health(self, project_id: str) -> dict[str, Any]:
        tasks = [item for item in self.store.list("task", limit=500) if item.get("project_id") == project_id]
        if not tasks:
            return {"project_id": project_id, "state": "INACTIVE", "evidence": {"tasks": 0}, "next_action": None}
        statuses = {item.get("status") for item in tasks}
        if statuses.issubset({"COMPLETED"}):
            state = "COMPLETED"
        elif "BLOCKED" in statuses or "DEAD_LETTER" in statuses:
            state = "BLOCKED"
        elif statuses.intersection({"RUNNING", "QUEUED", "RETRYING"}):
            state = "ACTIVE"
        else:
            state = "AT_RISK"
        next_task = next((item for item in tasks if item.get("status") in {"QUEUED", "RETRYING", "BLOCKED"}), None)
        result = {"project_id": project_id, "state": state, "evidence": {"tasks": len(tasks), "statuses": sorted(str(item) for item in statuses)}, "next_action": next_task.get("title") if next_task else None, "updated_at": self.store._now()}
        self.store.save({"id": f"project-health:{project_id}", "entity_type": "project_health", **result})
        return result

    def proactive_scan(self) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        failed = [task for task in self.tasks.list(limit=500) if task.get("status") in {"FAILED", "DEAD_LETTER", "BLOCKED"}]
        if failed:
            signals.append(self.notifications.signal("task_failure", f"{len(failed)} task(s) need attention", {"task_ids": [task.get("id") for task in failed[:20]]}, severity="warning", importance=80, urgency=70, confidence=1.0, recommendation="Review the blocked or dead-letter tasks and resume or replan them."))
        gaps = self.store.list("capability_gap", status="OPEN", limit=50)
        if gaps:
            signals.append(self.notifications.signal("capability_gap", f"{len(gaps)} capability gap(s) remain open", {"gap_ids": [gap.get("id") for gap in gaps[:20]]}, severity="info", importance=60, urgency=40, confidence=1.0, recommendation="Review evidence and create a governed evolution proposal."))
        return signals

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "service": "David AI operating system", "persistence": {"mode": "supabase" if self.store.remote_enabled else "json", "database_enabled": self.store.remote_enabled}, "policy": {"emergency_stop": self.policy.snapshot()["emergency_stop"], "autonomous_mode": self.policy.snapshot()["autonomous_mode"]}, "provider_count": len(self.providers.list())}

    def status(self) -> dict[str, Any]:
        records = self.store.list(limit=500)
        by_type: dict[str, int] = {}
        for record in records:
            entity_type = str(record.get("entity_type") or "unknown")
            by_type[entity_type] = by_type.get(entity_type, 0) + 1
        return {
            "version": os.getenv("DAVID_VERSION", "1.5-final"),
            "health": self.health(),
            "workers": {"mode": "controlled_on_demand", "active": 0, "uncontrolled_background": False},
            "providers": self.providers.list(),
            "tasks": {"active": len([row for row in self.tasks.list(limit=500) if row.get("status") in {"QUEUED", "RUNNING", "RETRYING", "BLOCKED"}]), "total": by_type.get("task", 0)},
            "objectives": {"active": len([row for row in self.objectives.list() if row.get("status") == "ACTIVE"]), "total": by_type.get("objective", 0)},
            "agents": {"active": len([row for row in self.agents.list() if row.get("status") == "ACTIVE"]), "total": by_type.get("agent", 0)},
            "workflows": {"active": len([row for row in self.workflows.list() if row.get("status") == "ACTIVE"]), "total": by_type.get("workflow", 0)},
            "evolutions": {"active": len([row for row in self.evolutions.list() if row.get("status") == "ACTIVE"]), "total": by_type.get("evolution", 0)},
            "integrations": {"github": bool(self.settings.github_is_configured), "supabase": bool(self.settings.supabase_database_is_configured), "render": bool(self.settings.render_api_key and self.settings.render_owner_id)},
            "incidents": self.store.list("incident", status="OPEN", limit=50),
            "capability_gaps": self.store.list("capability_gap", status="OPEN", limit=50),
            "resources": self.resources.observe(),
            "record_counts": by_type,
            "last_known_good_version": self.last_known_good[0] if self.last_known_good else None,
            "open_policy": self.policy.snapshot(),
        }


_OS_CACHE: OperatingSystem | None = None
_OS_LOCK = threading.Lock()


def get_operating_system() -> OperatingSystem:
    global _OS_CACHE
    if _OS_CACHE is None:
        with _OS_LOCK:
            if _OS_CACHE is None:
                _OS_CACHE = OperatingSystem()
    return _OS_CACHE


def reset_operating_system_for_tests() -> None:
    global _OS_CACHE
    with _OS_LOCK:
        _OS_CACHE = None

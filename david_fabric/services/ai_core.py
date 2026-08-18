"""David AI Core orchestration boundary.

The service is intentionally additive: it coordinates existing David services and
never implements a second provider, credential, storage, or tool system. Every
provider call is bounded, policy-checked, validated, and represented truthfully.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.core.storage import JsonStorage
from app.providers.ai_router import AIRouter
from app.services.conversation_engine import ConversationEngine
from app.services.memory_engine import MemoryEngine
from app.services.provider_registry import (
    CapabilityNotSupported,
    CapabilityRouter,
    ProviderIntegrationError,
    ProviderNotConfigured,
)
from app.services.supabase_service import SupabasePersistence
from david_fabric.core.models import Goal, GoalPlan
from david_fabric.services.planner import create_plan
from david_fabric.services.registry import list_enriched_capabilities, match_capabilities
from david_fabric.services.operating_system import OperatingSystem, get_operating_system
from david_fabric.services.policy import authorize, requires_approval


UTC = timezone.utc
_SECRET_NAME_RE = re.compile(r"(?i)(api[_ -]?key|secret|token|password|credential|private[_ -]?key)")
_SECRET_VALUE_RE = re.compile(r"(?i)(?:api[_ -]?key|secret|token|password|credential|private[_ -]?key)\s*[:=]\s*[^\s,;]+")
_BEARER_RE = re.compile(r"(?i)\b(?:bearer\s+)?(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{20,})\b")


@dataclass(frozen=True)
class IntentProfile:
    """Deterministic intent envelope used before any external provider call."""

    name: str
    execution_capability: str
    confidence: float
    complexity: str
    requires_approval: bool
    signals: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "execution_capability": self.execution_capability,
            "confidence": self.confidence,
            "complexity": self.complexity,
            "requires_approval": self.requires_approval,
            "signals": list(self.signals),
        }


@dataclass
class CoreResult:
    reply: str
    provider: str
    conversation_id: str | None
    routing: dict[str, Any]
    status: str = "completed"
    output: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "reply": self.reply,
            "provider": self.provider,
            "conversation_id": self.conversation_id,
            "capability_routing": self.routing,
            "status": self.status,
            "output": self.output,
        }


class AICoreService:
    """Central request pipeline for chat and explicit AI Core API calls."""

    _ID_TO_EXECUTION: dict[str, str] = {
        "david-core": "reasoning",
        "coding": "reasoning",
        "browser-use": "reasoning",
        "playwright": "reasoning",
        "research": "reasoning",
        "multi-agent": "reasoning",
        "stateful-agents": "reasoning",
        "creative-backend": "image",
        "image": "image",
        "voice": "tts",
        "david-voice-backend": "tts",
        "stt": "stt",
        "video": "video",
        "website": "website",
        "website-development": "website",
        "deployment": "deployment",
        "automation": "automation",
    }

    _EXECUTION_TO_PROVIDER_CAPABILITY: dict[str, str] = {
        "reasoning": "reasoning",
        "image": "image",
        "tts": "tts",
        "stt": "stt",
        "video": "video",
        "website": "website",
        "deployment": "deployment",
        "embeddings": "embeddings",
    }

    def __init__(
        self,
        settings: Settings | None = None,
        memory: MemoryEngine | None = None,
        conversations: ConversationEngine | None = None,
        operating_system: OperatingSystem | None = None,
        capability_router: CapabilityRouter | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.memory = memory or MemoryEngine(JsonStorage(self.settings.data_dir), SupabasePersistence(self.settings))
        self.conversations = conversations or ConversationEngine(JsonStorage(self.settings.data_dir), SupabasePersistence(self.settings))
        self.operating_system = operating_system or get_operating_system()
        self.capability_router = capability_router or CapabilityRouter(self.settings)

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _safe_text(value: Any, limit: int = 8000) -> str:
        text = str(value or "")
        return _SECRET_VALUE_RE.sub("[REDACTED]", _BEARER_RE.sub("[REDACTED]", text))[:limit]

    @classmethod
    def _safe_value(cls, value: Any, depth: int = 0) -> Any:
        if depth > 4:
            return "[TRUNCATED]"
        if isinstance(value, str):
            return cls._safe_text(value, 2000)
        if isinstance(value, (bytes, bytearray)):
            return {"type": "bytes", "size_bytes": len(value)}
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            for key, item in value.items():
                key_text = str(key)
                if _SECRET_NAME_RE.search(key_text):
                    result[key_text] = "[REDACTED]"
                else:
                    result[key_text] = cls._safe_value(item, depth + 1)
            return result
        if isinstance(value, (list, tuple)):
            return [cls._safe_value(item, depth + 1) for item in list(value)[:30]]
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        return cls._safe_text(value, 2000)

    def intent_classify(self, message: str, requested_capability: str | None = None) -> IntentProfile:
        text = self._safe_text(message, 12000).casefold()
        requested = (requested_capability or "").strip().casefold()
        signals: list[str] = []

        explicit: list[tuple[str, str, tuple[str, ...]]] = [
            ("deployment", "deployment", ("deploy", "release", "publish", "ship to production", "rollback")),
            ("automation", "automation", ("automate", "automation", "webhook", "schedule", "workflow")),
            ("video_generation", "video", ("video", "animation", "text-to-video", "image-to-video")),
            ("image_generation", "image", ("image", "picture", "illustration", "logo", "artwork", "draw")),
            ("speech_to_text", "stt", ("transcribe", "transcription", "speech to text", "audio to text", "whisper")),
            ("text_to_speech", "tts", ("text to speech", "tts", "voiceover", "narrate", "speak aloud", "voice")),
            ("website", "website", ("website", "web app", "landing page", "frontend", "react app")),
            ("coding", "coding", ("code", "coding", "debug", "repository", "github", "implement", "test", "bug")),
            ("research", "research", ("research", "investigate", "compare", "find sources", "browse the web")),
        ]
        selected: tuple[str, str] | None = None
        if requested:
            requested_map = {
                "reasoning": ("reasoning", "reasoning"),
                "david-core": ("reasoning", "reasoning"),
                "image": ("image_generation", "image"),
                "video": ("video_generation", "video"),
                "tts": ("text_to_speech", "tts"),
                "stt": ("speech_to_text", "stt"),
                "website": ("website", "website"),
                "deployment": ("deployment", "deployment"),
                "automation": ("automation", "automation"),
                "coding": ("coding", "coding"),
            }
            if requested in requested_map:
                selected = requested_map[requested]
                signals.append(f"requested:{requested}")
        if selected is None:
            for name, capability, keywords in explicit:
                hits = [keyword for keyword in keywords if keyword in text]
                if hits:
                    selected = (name, capability)
                    signals.extend(hits[:4])
                    break
        if selected is None:
            selected = ("general_reasoning", "reasoning")
            signals.append("default_reasoning")

        compound_markers = (" and ", " then ", " after ", " also ", "workflow", "step by step", "multiple")
        complexity = "multi_step" if any(marker in text for marker in compound_markers) else "single_step"
        if len(text.split()) > 80:
            complexity = "multi_step"
        needs_approval = selected[1] in {"deployment", "automation"} or any(word in text for word in ("delete", "purchase", "publish"))
        confidence = 0.92 if signals and signals != ["default_reasoning"] else 0.58
        return IntentProfile(selected[0], selected[1], confidence, complexity, needs_approval, signals)

    def capability_match(self, message: str, *, requested_capability: str | None = None) -> list[dict[str, Any]]:
        candidates = match_capabilities(message, requested_capability=requested_capability)
        intent = self.intent_classify(message, requested_capability)
        mapped = intent.execution_capability
        if mapped not in {"reasoning", "image", "video", "tts", "stt", "website", "deployment", "automation"}:
            mapped = "reasoning"
        synthetic = {
            "id": mapped,
            "name": mapped.replace("_", " ").title(),
            "category": mapped,
            "state": "READY" if mapped == "reasoning" else "REGISTERED",
            "available": mapped == "reasoning",
            "reason": "AI Core provider adapter" if mapped == "reasoning" else "provider capability boundary",
            "fallback_capabilities": [],
            "permissions": ["read"],
            "keywords": [],
        }
        if not candidates or not any(self._ID_TO_EXECUTION.get(str(item.get("id")), str(item.get("id"))) == mapped for item in candidates):
            candidates.insert(0, synthetic)
        return candidates[:8]

    def context_assemble(
        self,
        message: str,
        *,
        conversation_id: str | None = None,
        project_id: str | None = None,
        task_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        safe_request_context = self._safe_value(context or {})
        try:
            memories = [item.model_dump(mode="json") for item in self.memory.relevant(message, limit=8)]
        except Exception:
            memories = []
        try:
            operating_context = self.operating_system.context(message, project_id=project_id, task_id=task_id, limit=8)
        except Exception:
            operating_context = {"query": message, "project_id": project_id, "task_id": task_id, "memories": [], "records": [], "confidence": 0.0}
        messages: list[dict[str, Any]] = []
        if conversation_id:
            try:
                messages = [
                    {"role": item.role, "content": self._safe_text(item.content, 4000), "created_at": item.created_at.isoformat()}
                    for item in self.conversations.recent_messages(conversation_id, limit=12)
                ]
            except Exception:
                messages = []
        return {
            "request": self._safe_text(message, 12000),
            "conversation_id": conversation_id,
            "project_id": project_id,
            "task_id": task_id,
            "request_context": safe_request_context,
            "memories": self._safe_value(memories),
            "operating_context": self._safe_value(operating_context),
            "conversation_messages": messages,
            "confidence": max(float(operating_context.get("confidence", 0.0) or 0.0), 0.7 if memories else 0.0),
        }

    def make_plan(
        self,
        message: str,
        intent: IntentProfile | None = None,
        *,
        context: dict[str, Any] | None = None,
        project_id: str | None = None,
        task_id: str | None = None,
    ) -> tuple[Goal, GoalPlan]:
        profile = intent or self.intent_classify(message)
        goal = Goal(
            title=message[:160] or "David AI request",
            objective=self._safe_text(message, 12000),
            project_id=project_id,
            context={
                **self._safe_value(context or {}),
                "requested_capability": profile.execution_capability,
                "intent": profile.as_dict(),
                "task_id": task_id,
            },
        )
        return goal, create_plan(goal)

    def _provider_chain(self, capability: str, preferred: Iterable[str] | None = None) -> list[str]:
        try:
            specs = self.capability_router.registry.capability_candidates(capability, preferred)
        except Exception:
            return []
        return [spec.id for spec in specs if spec.configured(self.settings) and spec.status not in {"frontend_key_only"}]

    def _record_event(self, event_type: str, payload: dict[str, Any], run_id: str) -> None:
        try:
            self.operating_system.store.event(event_type, self._safe_value(payload), correlation={"ai_core_run_id": run_id})
        except Exception:
            pass

    def _record(self, run_id: str, record_type: str, payload: dict[str, Any], *, status: str) -> None:
        try:
            self.operating_system.store.save({
                "id": f"{run_id}:{record_type}:{uuid4()}",
                "entity_type": f"ai_core_{record_type}",
                "status": status,
                "parent_id": run_id,
                "name": run_id,
                "payload": self._safe_value(payload),
            })
        except Exception:
            pass

    def _policy_gate(self, capability: str, approved: bool, run_id: str) -> tuple[bool, str, dict[str, Any]]:
        allowed, reason = authorize(capability, approved=approved)
        decision = {"capability": capability, "allowed": allowed, "requires_approval": requires_approval(capability), "reason": reason}
        self._record(run_id, "policy", decision, status="ALLOWED" if allowed else "BLOCKED")
        self._record_event("APPROVAL_GRANTED" if allowed and decision["requires_approval"] else "APPROVAL_REJECTED" if not allowed else "TASK_STARTED", decision, run_id)
        return allowed, reason, decision

    @staticmethod
    def _validate(capability: str, output: dict[str, Any]) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        text = output.get("text")
        if capability in {"reasoning", "stt"}:
            checks.append({"name": "non_empty_text", "passed": bool(str(text or "").strip())})
        elif capability == "image":
            checks.append({"name": "image_payload_present", "passed": bool(output.get("images"))})
        elif capability == "tts":
            checks.append({"name": "audio_payload_present", "passed": isinstance(output.get("audio_bytes"), (bytes, bytearray)) and bool(output.get("audio_bytes"))})
        elif capability == "embeddings":
            checks.append({"name": "embedding_payload_present", "passed": bool(output.get("embeddings"))})
        else:
            checks.append({"name": "adapter_returned_output", "passed": bool(output)})
        passed = all(item["passed"] for item in checks)
        return {"status": "passed" if passed else "failed", "passed": passed, "checks": checks, "message": "Output passed validation" if passed else "Provider returned no usable output"}

    @staticmethod
    def _public_output(output: dict[str, Any]) -> dict[str, Any]:
        public: dict[str, Any] = {}
        for key in ("provider", "model", "text", "usage", "content_type", "revised_prompt"):
            if key in output and key != "text" or key == "text" and output.get(key):
                public[key] = output[key]
        if isinstance(output.get("images"), list):
            public["images"] = [
                {k: item.get(k) for k in ("mime_type", "content_type", "revised_prompt") if item.get(k)}
                for item in output["images"] if isinstance(item, dict)
            ]
            public["image_count"] = len(output["images"])
        if isinstance(output.get("audio_bytes"), (bytes, bytearray)):
            public["audio_size_bytes"] = len(output["audio_bytes"])
        if isinstance(output.get("embeddings"), list):
            public["embedding_count"] = len(output["embeddings"])
            public["embedding_dimensions"] = len(output["embeddings"][0]) if output["embeddings"] and isinstance(output["embeddings"][0], list) else None
        return AICoreService._safe_value(public)

    async def _execute_provider_chain(
        self,
        capability: str,
        payload: dict[str, Any],
        providers: list[str],
        run_id: str,
    ) -> tuple[dict[str, Any] | None, str | None, list[dict[str, Any]], dict[str, Any] | None]:
        attempts: list[dict[str, Any]] = []
        max_retries = max(0, min(int(getattr(self.settings, "provider_max_retries", 1)), 5))
        for provider in providers:
            for retry_index in range(max_retries + 1):
                attempt = {"provider": provider, "retry": retry_index, "capability": capability, "started_at": self._now()}
                try:
                    output = await self.capability_router.execute(capability, payload, preferred=[provider])
                    validation = self._validate(capability, output)
                    attempt.update({"status": "completed" if validation["passed"] else "invalid", "validation": validation})
                    attempts.append(attempt)
                    self._record(run_id, "step", attempt, status="COMPLETED" if validation["passed"] else "FAILED")
                    if validation["passed"]:
                        return output, provider, attempts, validation
                    if retry_index >= max_retries:
                        break
                except ProviderIntegrationError as exc:
                    safe_error = {"code": exc.code, "message": str(exc), "retryable": bool(exc.retryable), "status_code": exc.status_code}
                    attempt.update({"status": "failed", "error": safe_error})
                    attempts.append(attempt)
                    self._record(run_id, "fallback", attempt, status="FAILED")
                    self._record_event("PROVIDER_FAILED", {"provider": provider, "error": safe_error}, run_id)
                    if not exc.retryable or retry_index >= max_retries:
                        break
                except Exception as exc:
                    safe_error = {"code": "provider_unexpected_error", "message": self._safe_text(exc, 300), "retryable": False}
                    attempt.update({"status": "failed", "error": safe_error})
                    attempts.append(attempt)
                    self._record(run_id, "fallback", attempt, status="FAILED")
                    self._record_event("PROVIDER_FAILED", {"provider": provider, "error": safe_error}, run_id)
                    break
        return None, None, attempts, None

    async def process(
        self,
        message: str,
        *,
        conversation_id: str | None = None,
        project_id: str | None = None,
        task_id: str | None = None,
        context: dict[str, Any] | None = None,
        requested_capability: str | None = None,
        approved: bool = False,
        preferred_providers: list[str] | None = None,
    ) -> CoreResult:
        clean_message = self._safe_text(message, 12000).strip()
        if not clean_message:
            return CoreResult("Please provide a request for David to process.", "validation", conversation_id, {"validation_result": {"status": "failed", "message": "message is required"}}, "failed")

        run_id = str(uuid4())
        intent = self.intent_classify(clean_message, requested_capability)
        candidates = self.capability_match(clean_message, requested_capability=requested_capability)
        assembled = self.context_assemble(clean_message, conversation_id=conversation_id, project_id=project_id, task_id=task_id, context=context)
        goal, goal_plan = self.make_plan(clean_message, intent, context=assembled, project_id=project_id, task_id=task_id)
        first_step = goal_plan.steps[0] if goal_plan.steps else None
        requested_execution = intent.execution_capability
        execution_capability = self._ID_TO_EXECUTION.get(str(first_step.capability), requested_execution) if first_step else requested_execution
        if requested_execution in {"image", "video", "tts", "stt", "website", "deployment", "automation"}:
            execution_capability = requested_execution
        execution_capability = self._EXECUTION_TO_PROVIDER_CAPABILITY.get(execution_capability, "reasoning")
        policy_capability = intent.execution_capability if intent.execution_capability in {"deployment", "automation", "website", "video", "image", "tts", "stt", "reasoning"} else execution_capability

        self._record(run_id, "run", {"message": clean_message, "intent": intent.as_dict(), "project_id": project_id, "task_id": task_id}, status="RUNNING")
        allowed, policy_reason, policy_decision = self._policy_gate(policy_capability, approved, run_id)
        selected_candidate = next((item for item in candidates if item.get("available")), candidates[0] if candidates else None)
        selected_id = str(selected_candidate.get("id")) if selected_candidate else execution_capability
        fallback_chain = []
        if selected_candidate:
            fallback_chain.extend(str(item) for item in selected_candidate.get("fallback_capabilities", []))
            fallback_chain.extend(str(item.get("id")) for item in candidates if str(item.get("id")) != selected_id and str(item.get("id")) not in fallback_chain)
        routing: dict[str, Any] = {
            "run_id": run_id,
            "intent": intent.as_dict(),
            "selected_capability": execution_capability,
            "selected": self._route_candidate(selected_candidate) if selected_candidate else None,
            "fallback_chain": fallback_chain,
            "candidates": [self._safe_value(item) for item in candidates],
            "plan": self._safe_value({"goal_id": goal.id, "steps": [step.model_dump(mode="json") for step in goal_plan.steps]}),
            "context": {"memory_count": len(assembled.get("memories", [])), "conversation_messages": len(assembled.get("conversation_messages", [])), "operating_records": len(assembled.get("operating_context", {}).get("records", []))},
            "policy": policy_decision,
            "provider_chain": [],
            "fallbacks_used": [],
            "attempts": [],
            "validation_result": None,
            "execution_started": False,
        }
        if not allowed:
            routing["validation_result"] = {"status": "blocked", "message": policy_reason}
            self._record(run_id, "run", routing, status="BLOCKED")
            reply = f"I did not execute this request because policy blocked {policy_capability}: {policy_reason}"
            conversation_id = self._persist_conversation(conversation_id, clean_message, reply)
            self._persist_memory(clean_message, run_id)
            return CoreResult(reply, "policy", conversation_id, routing, "blocked")

        providers = self._provider_chain(execution_capability, preferred_providers)
        routing["provider_chain"] = providers
        routing["execution_started"] = True
        provider_payload: dict[str, Any]
        if execution_capability == "reasoning":
            provider_payload = {"prompt": self._build_reasoning_prompt(clean_message, assembled, intent, goal_plan), "model": None}
        elif execution_capability == "image":
            provider_payload = {"prompt": clean_message}
        elif execution_capability == "tts":
            provider_payload = {"text": clean_message}
        elif execution_capability == "stt":
            provider_payload = dict(self._safe_value(context or {}))
        else:
            provider_payload = {"prompt": clean_message}

        output, provider, attempts, validation = await self._execute_provider_chain(execution_capability, provider_payload, providers, run_id)
        routing["attempts"] = self._safe_value(attempts)
        routing["fallbacks_used"] = [item["provider"] for item in attempts if item.get("status") in {"failed", "invalid"}]
        routing["validation_result"] = validation
        status = "completed"
        reply: str
        public_output: dict[str, Any]
        if output is not None and validation and validation.get("passed"):
            public_output = self._public_output(output)
            reply = self._reply_from_output(execution_capability, output, provider or "provider")
        elif execution_capability == "reasoning":
            # Preserve the existing AIRouter as a final, clearly-labelled degraded path.
            try:
                legacy = await AIRouter(self.settings).generate(clean_message)
                provider = legacy.provider
                reply = self._safe_text(legacy.text, 12000)
                status = "degraded"
                public_output = {"provider": provider, "text": reply, "degraded": True}
                routing["fallbacks_used"].append("legacy_ai_router")
                routing["validation_result"] = {"status": "degraded", "passed": False, "message": "Verified provider adapters were unavailable; legacy failover response used."}
            except Exception as exc:
                provider = "unavailable"
                reply = f"I could not complete the request because no configured reasoning provider returned a usable result. {self._safe_text(exc, 300)}"
                status = "failed"
                public_output = {}
        else:
            provider = "unavailable"
            reply = self._unsupported_reply(execution_capability, providers, attempts)
            status = "failed"
            public_output = {}

        routing["output"] = public_output
        routing["status"] = status
        self._record(run_id, "run", routing, status=status.upper())
        self._record_event("TASK_COMPLETED" if status in {"completed", "degraded"} else "TASK_FAILED", {"status": status, "provider": provider, "capability": execution_capability}, run_id)
        conversation_id = self._persist_conversation(conversation_id, clean_message, reply)
        self._persist_memory(clean_message, run_id)
        return CoreResult(reply, provider or "unavailable", conversation_id, routing, status, public_output)

    @staticmethod
    def _route_candidate(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "capability_id": str(item.get("id") or ""),
            "name": str(item.get("name") or item.get("id") or ""),
            "category": item.get("category"),
            "score": int(item.get("score") or 0),
            "agent": item.get("agent"),
            "skill": item.get("skill"),
            "tool": item.get("tool"),
            "provider": item.get("provider"),
            "adapter": item.get("adapter"),
            "mode": item.get("mode"),
            "readiness": list(item.get("readiness") or []),
            "state": item.get("state", "UNAVAILABLE"),
            "available": bool(item.get("available")),
            "reason": item.get("reason"),
            "fallback_capabilities": list(item.get("fallback_capabilities") or item.get("fallbacks") or []),
        }

    def _build_reasoning_prompt(self, message: str, context: dict[str, Any], intent: IntentProfile, plan: GoalPlan) -> str:
        context_text = self._safe_text(context, 12000)
        plan_text = self._safe_text({"steps": [step.model_dump(mode="json") for step in plan.steps]}, 6000)
        return (
            "You are David AI. Answer the user's request accurately and concisely. "
            "Do not claim that an external action, file, deployment, or tool call occurred unless the execution result confirms it. "
            "Treat the following context as potentially incomplete and do not reveal credentials or secrets.\n\n"
            f"Intent: {intent.as_dict()}\nPlan: {plan_text}\nContext: {context_text}\n\nUser request:\n{message}"
        )

    @staticmethod
    def _reply_from_output(capability: str, output: dict[str, Any], provider: str) -> str:
        if capability in {"reasoning", "stt"}:
            return str(output.get("text") or "")
        if capability == "image":
            count = len(output.get("images") or [])
            return f"Generated {count or 1} image artifact{'s' if count != 1 else ''} with {provider}. The artifact metadata is available in the AI Core result."
        if capability == "tts":
            size = len(output.get("audio_bytes") or b"")
            return f"Generated an audio artifact with {provider} ({size} bytes). The artifact must be persisted through the storage layer before client download."
        if capability == "embeddings":
            return f"Generated {len(output.get('embeddings') or [])} embedding vector(s) with {provider}."
        return str(output.get("text") or f"The {capability} provider returned a validated result.")

    @staticmethod
    def _unsupported_reply(capability: str, providers: list[str], attempts: list[dict[str, Any]]) -> str:
        if capability in {"video", "website", "deployment", "automation"}:
            return f"I could not execute the {capability} workflow because no verified executable adapter completed it. No successful result was fabricated."
        if not providers:
            return f"I could not execute this request because no configured provider is available for {capability}."
        return f"I could not execute this request because all configured {capability} provider attempts failed validation or recovery. No successful result was fabricated."

    def _persist_conversation(self, conversation_id: str | None, message: str, reply: str) -> str | None:
        try:
            if not conversation_id or not self.conversations.get(conversation_id):
                conversation = self.conversations.create(title=message[:60] or "New conversation")
                conversation_id = conversation.id
            self.conversations.add_message(conversation_id, "user", message)
            self.conversations.add_message(conversation_id, "assistant", reply)
            return conversation_id
        except Exception:
            return conversation_id

    def _persist_memory(self, message: str, run_id: str) -> None:
        try:
            self.memory.learn_from_text(message, source="ai-core")
            self._record_event("MEMORY_UPDATED", {"source": "ai-core", "message_length": len(message)}, run_id)
        except Exception:
            pass

    def plan_only(self, message: str, *, requested_capability: str | None = None, context: dict[str, Any] | None = None, project_id: str | None = None, task_id: str | None = None) -> dict[str, Any]:
        intent = self.intent_classify(message, requested_capability)
        assembled = self.context_assemble(message, project_id=project_id, task_id=task_id, context=context)
        goal, plan = self.make_plan(message, intent, context=assembled, project_id=project_id, task_id=task_id)
        return {"intent": intent.as_dict(), "goal": goal.model_dump(mode="json"), "plan": plan.model_dump(mode="json"), "capabilities": [self._safe_value(item) for item in self.capability_match(message, requested_capability=requested_capability)]}

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "service": "David AI Core", "pipeline": ["intent", "capability", "context", "plan", "provider", "policy", "execution", "validation", "fallback", "result", "memory"], "provider_count": len(self.capability_router.registry.list())}

    def status(self) -> dict[str, Any]:
        try:
            os_health = self.operating_system.health()
        except Exception:
            os_health = {"status": "unknown"}
        return {"health": self.health(), "operating_system": os_health, "configured_providers": [row["id"] for row in self.capability_router.registry.list() if row.get("configured")], "secret_exposure": False}


__all__ = ["AICoreService", "CoreResult", "IntentProfile"]

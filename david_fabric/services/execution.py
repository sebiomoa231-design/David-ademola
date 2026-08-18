from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from david_fabric.core.models import (
    Artifact,
    ExecutionAttempt,
    Goal,
    GoalPlan,
    Run,
    RunResult,
    Verification,
)
from david_fabric.services.adapters import (
    adapter_for_capability,
    invoke_adapter,
    readiness_for_adapter,
)
from david_fabric.services.policy import authorize
from david_fabric.services.registry import enrich_capability, get_capability
from david_fabric.storage import db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


NATIVE_TARGETS = {
    "david-core": "/api/chat or the existing David orchestration surface",
    "research": "/api/knowledge/search and the browser/research route boundary",
    "website-development": "/api/website",
    "audio": "/api/voice or the existing creative/media route boundary",
    "marketing": "native marketing workflow boundary",
    "web-automation": "browser router boundary",
    "mcp-tools": "controlled MCP/API tool boundary",
    "background-jobs": "Fabric run queue and workflow boundary",
    "evaluation": "Fabric verification engine",
    "artifact-generation": "Fabric artifact store",
    "qa": "Fabric QA and verification boundary",
}


async def _execute_native(
    capability: dict[str, Any],
    goal: Goal,
    input_data: dict[str, Any],
) -> dict[str, Any]:
    """Invoke supported David-native services without creating a parallel executor.

    The Fabric is only the governed lifecycle. A native capability must call an
    established David service, return its real response, and retain that result
    as provenance. Native surfaces without an executable service remain an
    explicit handoff rather than a fabricated completion.
    """

    capability_id = str(capability.get("id"))
    if capability_id == "david-core":
        from ai_router import AIRouter
        from app.core.config import get_settings

        result = await AIRouter(get_settings()).generate(goal.objective)
        if result.provider == "fallback":
            raise RuntimeError(result.text)
        return {
            "status": "completed",
            "control_plane": "david-ai",
            "capability": capability_id,
            "provider": result.provider,
            "reply": result.text,
        }

    if capability_id == "website-development":
        from app.core.config import get_settings
        from app.services.supabase_service import SupabasePersistence
        from app.services.website_engine import WebsiteEngine

        blueprint = WebsiteEngine().generate(goal.objective)
        persistence = SupabasePersistence(get_settings())
        generation_id: str | None = None
        if persistence.database_enabled:
            stored = persistence.create_generation(
                {
                    "project_id": input_data.get("project_id") or goal.project_id,
                    "kind": "website",
                    "prompt": goal.objective,
                    "provider": "website-engine",
                    "status": "completed",
                    "output": json.dumps(blueprint),
                    "metadata": {
                        "section_count": len(blueprint.get("sections", [])),
                        "source": "intelligence-fabric",
                    },
                }
            )
            generation_id = str(stored.get("id"))
        return {
            "status": "completed",
            "control_plane": "david-ai",
            "capability": capability_id,
            "generation_id": generation_id,
            "blueprint": blueprint,
            "note": "Generated a structured website blueprint. No preview URL or external deployment was fabricated.",
        }

    return {
        "status": "delegated",
        "control_plane": "david-ai",
        "capability": capability_id,
        "objective": goal.objective,
        "dispatch_target": NATIVE_TARGETS.get(capability_id, "existing David API or registered native handler"),
        "next": "existing David API or registered native handler",
    }


def _save_verification(
    run_id: str,
    attempt_id: str | None,
    *,
    status: str,
    checks: list[dict[str, Any]],
    message: str,
) -> Verification:
    verification = Verification(
        run_id=run_id,
        attempt_id=attempt_id,
        status=status,
        checks=checks,
        message=message,
    )
    db.save_verification(verification)
    db.add_event(run_id, "verification_recorded", verification.model_dump(mode="json"))
    return verification


def _artifact_for_output(
    run_id: str,
    attempt_id: str,
    output: dict[str, Any],
    *,
    kind: str,
) -> Artifact:
    artifact = Artifact(
        run_id=run_id,
        attempt_id=attempt_id,
        name=f"{kind}-{attempt_id}.json",
        kind=kind,
        uri=f"fabric://runs/{run_id}/attempts/{attempt_id}/output",
        content_type="application/json",
        metadata={"inline_output": output},
    )
    db.save_artifact(artifact)
    return artifact


def _failed_result(run: Run, reason: str) -> RunResult:
    run.status = "failed"
    run.failure_reason = reason
    run.completed_at = _now()
    db.save_run(run)
    verification = _save_verification(
        run.id,
        None,
        status="failed",
        checks=[{"name": "execution", "passed": False, "reason": reason}],
        message=reason,
    )
    return RunResult(
        run=run,
        artifacts=[],
        verification=verification,
        events=db.get_events(run.id),
    )


async def execute_goal(
    goal: Goal,
    run: Run,
    plan: GoalPlan,
    *,
    input_data: dict[str, Any] | None = None,
) -> RunResult:
    """Execute a plan with bounded fallback and no fake success states."""

    if not plan.steps:
        return _failed_result(run, "Plan contains no executable steps.")

    step = plan.steps[0]
    candidates = [step.capability, *step.fallback_capabilities]
    max_attempts = max(1, min(len(candidates), 3))
    artifacts: list[Artifact] = []
    last_error = "No candidate capability was executable."

    for candidate_id in candidates[:max_attempts]:
        raw = get_capability(candidate_id)
        if not raw:
            last_error = f"Capability '{candidate_id}' is not registered."
            db.add_event(run.id, "capability_unavailable", {"capability": candidate_id, "reason": last_error})
            continue
        capability = enrich_capability(raw)
        allowed, reason = authorize(candidate_id, approved=run.approved)
        attempt = ExecutionAttempt(
            run_id=run.id,
            capability_id=candidate_id,
            agent=capability.get("agent"),
            tool=capability.get("tool"),
            provider=capability.get("provider"),
            adapter=capability.get("adapter"),
            status="running" if allowed else "blocked",
            readiness=list(capability.get("readiness", [])),
        )
        db.save_attempt(attempt)
        run.attempts.append(attempt.id)
        db.add_event(
            run.id,
            "capability_selected",
            {
                "capability": candidate_id,
                "state": capability.get("state"),
                "readiness": capability.get("readiness", []),
                "fallback": candidate_id != step.capability,
            },
        )

        if not allowed:
            attempt.error = reason
            db.save_attempt(attempt)
            db.add_event(run.id, "approval_blocked", {"capability": candidate_id, "reason": reason})
            run.status = "blocked"
            run.failure_reason = reason
            run.completed_at = _now()
            db.save_run(run)
            verification = _save_verification(
                run.id,
                attempt.id,
                status="blocked",
                checks=[{"name": "approval", "passed": False, "reason": reason}],
                message=reason,
            )
            return RunResult(run=run, attempt=attempt, artifacts=[], verification=verification, events=db.get_events(run.id))

        adapter = adapter_for_capability(candidate_id, capability)
        try:
            if adapter and adapter.url():
                output = await invoke_adapter(
                    adapter,
                    run_id=run.id,
                    objective=goal.objective,
                    input_data=input_data or {},
                )
                kind = "service-result"
                attempt.status = "completed"
                run.status = "completed"
                verification_message = "External service returned a valid execution envelope."
            elif str(capability.get("mode", "")).lower() == "native":
                output = await _execute_native(capability, goal, input_data or {})
                delegated = output.get("status") == "delegated"
                kind = "dispatch" if delegated else "service-result"
                attempt.status = "delegated" if delegated else "completed"
                run.status = "delegated" if delegated else "completed"
                verification_message = "Native David handoff was recorded; no task-specific artifact was fabricated." if delegated else "Established David-native service returned a real execution result."
            else:
                raise RuntimeError(capability.get("reason") or "Capability requires an unavailable external service.")

            attempt.output = output
            attempt.finished_at = _now()
            db.save_attempt(attempt)
            run.selected_capability = candidate_id
            run.selected_agent = capability.get("agent")
            run.selected_tool = capability.get("tool")
            run.selected_provider = capability.get("provider")
            run.failure_reason = None
            run.completed_at = _now()
            db.save_run(run)
            db.add_event(run.id, "execution_completed", {"capability": candidate_id, "status": attempt.status})
            artifact = _artifact_for_output(run.id, attempt.id, output, kind=kind)
            artifacts.append(artifact)
            verification = _save_verification(
                run.id,
                attempt.id,
                status="passed",
                checks=[
                    {"name": "execution_envelope", "passed": isinstance(output, dict)},
                    {"name": "artifact_recorded", "passed": True},
                ],
                message=verification_message,
            )
            return RunResult(
                run=run,
                attempt=attempt,
                artifacts=artifacts,
                verification=verification,
                events=db.get_events(run.id),
            )
        except Exception as exc:
            last_error = str(exc)[:240]
            attempt.status = "failed"
            attempt.error = last_error
            attempt.finished_at = _now()
            db.save_attempt(attempt)
            db.add_event(
                run.id,
                "execution_failed",
                {"capability": candidate_id, "error": last_error},
            )
            continue

    return _failed_result(run, last_error)

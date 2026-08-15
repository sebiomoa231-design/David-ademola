from __future__ import annotations

from typing import Any

from david_fabric.core.models import Artifact, ExecutionAttempt, Verification
from david_fabric.storage import db


def verify_attempt(
    attempt: ExecutionAttempt,
    artifacts: list[Artifact],
    *,
    expected_output_kinds: list[str] | None = None,
) -> Verification:
    checks: list[dict[str, Any]] = []
    envelope_passed = attempt.status in {"completed", "delegated"} and isinstance(attempt.output, dict)
    checks.append({"name": "execution_status", "passed": envelope_passed, "status": attempt.status})
    output_passed = bool(attempt.output)
    checks.append({"name": "output_envelope", "passed": output_passed})
    artifact_passed = any(artifact.attempt_id == attempt.id for artifact in artifacts)
    checks.append({"name": "artifact_tracking", "passed": artifact_passed})
    if expected_output_kinds:
        expected_passed = any(artifact.kind in expected_output_kinds for artifact in artifacts)
        checks.append({"name": "expected_output_kind", "passed": expected_passed, "expected": expected_output_kinds})
    passed = all(bool(check.get("passed")) for check in checks)
    verification = Verification(
        run_id=attempt.run_id,
        attempt_id=attempt.id,
        status="passed" if passed else "failed",
        checks=checks,
        message="All execution and artifact checks passed." if passed else "One or more execution checks failed.",
    )
    db.save_verification(verification)
    db.add_event(attempt.run_id, "verification_completed", verification.model_dump(mode="json"))
    return verification


def verify_failure(attempt: ExecutionAttempt) -> Verification:
    verification = Verification(
        run_id=attempt.run_id,
        attempt_id=attempt.id,
        status="failed",
        checks=[
            {"name": "failure_recorded", "passed": attempt.status == "failed"},
            {"name": "error_reason", "passed": bool(attempt.error)},
        ],
        message=attempt.error or "Execution failed without a recorded reason.",
    )
    db.save_verification(verification)
    db.add_event(attempt.run_id, "failure_verified", verification.model_dump(mode="json"))
    return verification

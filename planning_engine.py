from __future__ import annotations

import re
from uuid import uuid4

from app.models import PlanRequest, PlanResponse, PlanStep

_PHASE_TEMPLATES = [
    ("Discovery", "Clarify the goal, constraints, and success criteria."),
    ("Design", "Outline the approach, architecture, or structure needed."),
    ("Build", "Implement the core pieces required to reach the goal."),
    ("Verify", "Test, review, and confirm the result meets the goal."),
    ("Launch", "Ship, deploy, or deliver the finished result."),
]


class PlanningEngine:
    """
    Produces structured plans (milestones + ordered steps with
    dependencies) for a stated goal. Returns JSON-friendly objects
    rather than prose, so results can drive UI directly.
    """

    def create_plan(self, request: PlanRequest) -> PlanResponse:
        goal = request.goal.strip() or "Untitled goal"
        word_count = len(re.findall(r"\w+", goal))
        complexity_phases = min(5, max(2, 2 + word_count // 8))

        phases = _PHASE_TEMPLATES[:complexity_phases]
        steps: list[PlanStep] = []
        previous_id: str | None = None

        for phase_name, phase_description in phases:
            step_id = str(uuid4())
            steps.append(
                PlanStep(
                    id=step_id,
                    title=f"{phase_name}: {goal}",
                    description=phase_description,
                    depends_on=[previous_id] if previous_id else [],
                )
            )
            previous_id = step_id

        milestones = [f"{name} complete" for name, _ in phases]

        return PlanResponse(
            goal=goal,
            milestones=milestones,
            steps=steps,
            estimated_phases=len(phases),
        )

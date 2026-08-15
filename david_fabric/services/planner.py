from david_fabric.core.models import Goal, GoalPlan, PlanStep
from david_fabric.services.registry import get_capability, match_capabilities


DEFAULT_CAPABILITY_ID = "david-core"


def create_plan(goal: Goal) -> GoalPlan:
    matches = match_capabilities(f"{goal.title} {goal.objective}")
    selected: list[str] = []
    for item in matches:
        capability_id = str(item["id"])
        if capability_id not in selected:
            selected.append(capability_id)

    if not selected:
        selected = [DEFAULT_CAPABILITY_ID]

    steps: list[PlanStep] = []
    previous_id: str | None = None
    for capability_id in selected:
        source = get_capability(capability_id) or {"id": capability_id}
        step = PlanStep(
            title=f"{source.get('name', capability_id)} for goal",
            capability=capability_id,
            depends_on=[previous_id] if previous_id else [],
            requires_approval=bool(source.get("requires_approval", False)),
            metadata={
                "category": source.get("category"),
                "mode": source.get("mode"),
                "source": source.get("source"),
            },
        )
        steps.append(step)
        previous_id = step.id

    return GoalPlan(goal_id=goal.id, steps=steps)

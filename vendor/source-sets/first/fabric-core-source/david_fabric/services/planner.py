from david_fabric.services.registry import match_capabilities
from david_fabric.core.models import GoalPlan, PlanStep

DEFAULT_CAPABILITIES = [
    ("research", "research", False),
    ("browser", "browser", False),
    ("coding", "coding", False),
    ("website", "website", True),
    ("marketing", "marketing", False),
    ("image", "image", False),
    ("video", "video", False),
    ("voice", "voice", False),
    ("deployment", "deployment", True),
    ("automation", "automation", True),
    ("qa", "qa", False),
]

def create_plan(goal):
    matches = match_capabilities(goal.objective)
    selected = []
    for item in matches:
        if item["id"] not in selected:
            selected.append(item["id"])
    if not selected:
        selected = ["research"]
    steps=[]
    prev=None
    for i, cid in enumerate(selected, 1):
        cap = next((x for x in match_capabilities(cid) if x["id"]==cid), None)
        source = cap or {}
        step=PlanStep(
            title=f"{source.get('name', cid)} for goal",
            capability=cid,
            depends_on=[prev] if prev else [],
            requires_approval=bool(source.get("requires_approval", False)),
            metadata={"source": source.get("source")}
        )
        steps.append(step)
        prev=step.id
    return GoalPlan(goal_id=goal.id, steps=steps)

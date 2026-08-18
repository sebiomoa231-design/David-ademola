from fastapi import APIRouter

from app.models import PlanRequest, PlanResponse
from app.services.planning_engine import PlanningEngine

router = APIRouter(prefix="/plan", tags=["plan"])
engine = PlanningEngine()


@router.post("", response_model=PlanResponse)
def create_plan(payload: PlanRequest) -> PlanResponse:
    return engine.create_plan(payload)

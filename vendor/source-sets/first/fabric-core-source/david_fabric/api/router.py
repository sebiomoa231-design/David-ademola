from fastapi import APIRouter, HTTPException
from david_fabric.core.models import GoalCreate, Goal, GoalPlan, RunCreate, Run
from david_fabric.storage import db
from david_fabric.services.registry import load_capabilities, get_capability
from david_fabric.services.planner import create_plan
from david_fabric.services.health import service_health
from david_fabric.services.policy import authorize

api_router=APIRouter(prefix="/api")

@api_router.get("/health")
async def health():
    return {"status":"ok","component":"david-ai-intelligence-fabric","services":await service_health()}

@api_router.get("/intelligence/capabilities")
def capabilities():
    return {"capabilities":load_capabilities()}

@api_router.get("/intelligence/capabilities/{capability_id}")
def capability(capability_id:str):
    item=get_capability(capability_id)
    if not item: raise HTTPException(404,"Capability not found")
    return item

@api_router.post("/goals", response_model=Goal)
def create_goal(payload:GoalCreate):
    goal=Goal(**payload.model_dump())
    db.save_goal(goal)
    return goal

@api_router.post("/goals/{goal_id}/plan", response_model=GoalPlan)
def plan_goal(goal_id:str):
    row=db.get_goal(goal_id)
    if not row: raise HTTPException(404,"Goal not found")
    goal=Goal(id=row["id"],title=row["title"],objective=row["objective"],
              project_id=row["project_id"],context=__import__("json").loads(row["context_json"]),
              status=row["status"],created_at=row["created_at"])
    plan=create_plan(goal)
    db.save_plan(plan)
    return plan

@api_router.get("/goals/{goal_id}/plan")
def get_goal_plan(goal_id:str):
    plan=db.get_plan(goal_id)
    if not plan: raise HTTPException(404,"Plan not found")
    return plan

@api_router.post("/runs", response_model=Run)
def create_run(payload:RunCreate):
    if not db.get_goal(payload.goal_id): raise HTTPException(404,"Goal not found")
    run=Run(goal_id=payload.goal_id, approved=payload.approved)
    db.save_run(run)
    db.add_event(run.id,"run_created",{"goal_id":run.goal_id})
    return run

@api_router.post("/runs/{run_id}/authorize")
def authorize_run(run_id:str, capability:str):
    run=db.get_run(run_id)
    if not run: raise HTTPException(404,"Run not found")
    allowed,reason=authorize(capability,approved=True)
    if not allowed: raise HTTPException(403,reason)
    db.add_event(run_id,"approval_granted",{"capability":capability})
    return {"allowed":True,"capability":capability}

@api_router.get("/runs/{run_id}")
def get_run(run_id:str):
    run=db.get_run(run_id)
    if not run: raise HTTPException(404,"Run not found")
    return {"run":run,"events":db.get_events(run_id)}

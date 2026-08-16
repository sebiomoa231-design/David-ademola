from fastapi import APIRouter

from agents import router as agents_router
from github import router as github_router
from auth import router as auth_router
from chat import router as chat_router
from conversations import router as conversations_router
from david_fabric.api.router import fabric_router
from files import router as files_router
from health import router as health_router
from knowledge import router as knowledge_router
from library import router as library_router
from memory import router as memory_router
from plan import router as plan_router
from projects import router as projects_router
from settings import router as settings_router
from voice import router as voice_router
from website import router as website_router


api_router = APIRouter(prefix="/api")

for router in (
    health_router,
    auth_router,
    chat_router,
    conversations_router,
    files_router,
    knowledge_router,
    library_router,
    memory_router,
    plan_router,
    projects_router,
    settings_router,
    voice_router,
    website_router,
    agents_router,
    github_router,
):
    api_router.include_router(router)

# David remains the only mounted control plane. The Fabric contributes
# additive capabilities, planning, run tracking, approval policy, and adapter
# health without replacing any legacy route.
api_router.include_router(fabric_router)

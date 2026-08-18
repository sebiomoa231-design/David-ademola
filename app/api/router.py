from fastapi import APIRouter

from agents import router as agents_router
from app.api.routes.integrations import router as integrations_router
from app.api.routes.voice_features import router as voice_features_router
from app.api.routes.speech_engine import router as speech_engine_router
from app.api.routes.orchestrator import router as orchestrator_router
from github import router as github_router
from auth import router as auth_router
from chat import router as chat_router
from conversations import router as conversations_router
from david_fabric.api.router import fabric_router
from david_fabric.api.operating_router import router as operating_router
from david_fabric.api.ai_core_router import router as ai_core_router
from files import router as files_router
from health import router as health_router
from knowledge import router as knowledge_router
from library import router as library_router
from memory import router as memory_router
from plan import router as plan_router
from projects import router as projects_router
from providers import router as providers_router
from deployments import router as deployments_router
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
    providers_router,
    deployments_router,
    settings_router,
    voice_router,
    voice_features_router,
    speech_engine_router,
    website_router,
    integrations_router,
    agents_router,
    orchestrator_router,
    github_router,
    fabric_router,
    operating_router,
    ai_core_router,
):
    api_router.include_router(router)

# David remains the only mounted control plane. The Fabric and operating system
# contribute additive capabilities without replacing any legacy route.

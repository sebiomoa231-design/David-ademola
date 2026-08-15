from fastapi import APIRouter

from app.api.routes.agents import router as agents_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.memory import router as memory_router
from app.api.routes.plan import router as plan_router
from app.api.routes.projects import router as projects_router
from app.api.routes.settings import router as settings_router
from app.api.routes.voice import router as voice_router
from app.api.routes.website import router as website_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(memory_router)
api_router.include_router(projects_router)
api_router.include_router(conversations_router)
api_router.include_router(plan_router)
api_router.include_router(settings_router)
api_router.include_router(files_router)
api_router.include_router(website_router)
api_router.include_router(voice_router)
api_router.include_router(agents_router)
api_router.include_router(knowledge_router)

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.storage import JsonStorage
from app.models import ChatRequest, ChatResponse
from app.services.conversation_engine import ConversationEngine
from app.services.memory_engine import MemoryEngine
from app.services.supabase_service import SupabasePersistence
from david_fabric.services.ai_core import AICoreService


router = APIRouter(prefix="/chat", tags=["chat"])


def get_memory_engine(settings: Settings = Depends(get_settings)) -> MemoryEngine:
    return MemoryEngine(JsonStorage(settings.data_dir), SupabasePersistence(settings))


def get_conversation_engine(settings: Settings = Depends(get_settings)) -> ConversationEngine:
    return ConversationEngine(JsonStorage(settings.data_dir), SupabasePersistence(settings))


def get_ai_core(
    settings: Settings = Depends(get_settings),
    memory: MemoryEngine = Depends(get_memory_engine),
    conversations: ConversationEngine = Depends(get_conversation_engine),
) -> AICoreService:
    return AICoreService(settings, memory=memory, conversations=conversations)


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    core: AICoreService = Depends(get_ai_core),
) -> ChatResponse:
    result = await core.process(payload.message, conversation_id=payload.conversation_id)
    routing = dict(result.routing)
    # This field historically meant "a side-effect workflow was started" in
    # the chat contract. AI Core reasoning/provider execution is not a side
    # effect, so retain the legacy false value while exposing the full run.
    routing["execution_started"] = False
    routing["orchestration_completed"] = result.status in {"completed", "degraded", "failed", "blocked"}
    return ChatResponse(
        reply=result.reply,
        provider=result.provider,
        conversation_id=result.conversation_id,
        capability_routing=routing,
    )

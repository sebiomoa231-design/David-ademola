from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.storage import JsonStorage
from app.models import ChatRequest, ChatResponse
from app.providers.ai_router import AIRouter
from app.services.conversation_engine import ConversationEngine
from app.services.memory_engine import MemoryEngine
from david_fabric.core.models import CapabilitySelectionRequest
from david_fabric.api.router import route_capability
from app.services.supabase_service import SupabasePersistence

router = APIRouter(prefix="/chat", tags=["chat"])


def get_memory_engine(settings: Settings = Depends(get_settings)) -> MemoryEngine:
    return MemoryEngine(JsonStorage(), SupabasePersistence(settings))


def get_conversation_engine(settings: Settings = Depends(get_settings)) -> ConversationEngine:
    return ConversationEngine(JsonStorage(), SupabasePersistence(settings))


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    settings: Settings = Depends(get_settings),
    memory: MemoryEngine = Depends(get_memory_engine),
    conversations: ConversationEngine = Depends(get_conversation_engine),
) -> ChatResponse:
    router_ = AIRouter(settings)
    result = await router_.generate(payload.message)

    conversation_id = payload.conversation_id
    if not conversation_id:
        conversation = conversations.create(title=payload.message[:60] or "New conversation")
        conversation_id = conversation.id

    conversations.add_message(conversation_id, "user", payload.message)
    conversations.add_message(conversation_id, "assistant", result.text)
    memory.learn_from_text(payload.message, source="chat")
    routing = await route_capability(CapabilitySelectionRequest(objective=payload.message))

    return ChatResponse(
        reply=result.text,
        provider=result.provider,
        conversation_id=conversation_id,
        capability_routing={
            "selected": routing.selected.model_dump() if routing.selected else None,
            "fallback_chain": routing.fallback_chain,
            "execution_started": False,
            "next_step": "create a governed request to plan or execute this capability",
        },
    )

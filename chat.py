from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.storage import JsonStorage
from app.models import ChatRequest, ChatResponse
from app.providers.ai_router import AIRouter
from app.services.conversation_engine import ConversationEngine
from app.services.memory_engine import MemoryEngine

router = APIRouter(prefix="/chat", tags=["chat"])


def get_memory_engine() -> MemoryEngine:
    return MemoryEngine(JsonStorage())


def get_conversation_engine() -> ConversationEngine:
    return ConversationEngine(JsonStorage())


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

    return ChatResponse(
        reply=result.text,
        provider=result.provider,
        conversation_id=conversation_id,
    )

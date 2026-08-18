from fastapi import APIRouter, Depends, HTTPException

from app.core.storage import JsonStorage
from app.models import ConversationItem
from app.services.conversation_engine import ConversationEngine

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_engine() -> ConversationEngine:
    return ConversationEngine(JsonStorage())


@router.get("", response_model=list[ConversationItem])
def list_conversations(engine: ConversationEngine = Depends(get_engine)) -> list[ConversationItem]:
    return engine.all()


@router.post("", response_model=ConversationItem)
def create_conversation(
    title: str = "New conversation",
    engine: ConversationEngine = Depends(get_engine),
) -> ConversationItem:
    return engine.create(title=title)


@router.get("/{conversation_id}", response_model=ConversationItem)
def get_conversation(
    conversation_id: str,
    engine: ConversationEngine = Depends(get_engine),
) -> ConversationItem:
    conversation = engine.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/{conversation_id}/clear")
def clear_conversation(
    conversation_id: str,
    engine: ConversationEngine = Depends(get_engine),
) -> dict[str, bool]:
    ok = engine.clear(conversation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}


@router.get("/{conversation_id}/export")
def export_conversation(
    conversation_id: str,
    engine: ConversationEngine = Depends(get_engine),
) -> dict:
    data = engine.export(conversation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return data


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    engine: ConversationEngine = Depends(get_engine),
) -> dict[str, bool]:
    ok = engine.delete(conversation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}

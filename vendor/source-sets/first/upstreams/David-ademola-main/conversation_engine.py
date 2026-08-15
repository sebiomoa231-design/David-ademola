from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.core.storage import JsonStorage
from app.models import ConversationItem, ConversationMessage


class ConversationEngine:
    """Stores and manages chat conversation history in data/conversations.json."""

    STORE_NAME = "conversations"

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def _load(self) -> list[dict]:
        return self.storage.read(self.STORE_NAME, [])

    def _save(self, conversations: list[dict]) -> None:
        self.storage.write(self.STORE_NAME, conversations)

    def create(self, title: str = "New conversation") -> ConversationItem:
        item = ConversationItem(id=str(uuid4()), title=title)
        conversations = self._load()
        conversations.append(item.model_dump(mode="json"))
        self._save(conversations)
        return item

    def all(self) -> list[ConversationItem]:
        items = [ConversationItem(**c) for c in self._load()]
        items.sort(key=lambda c: c.updated_at, reverse=True)
        return items

    def get(self, conversation_id: str) -> ConversationItem | None:
        for c in self._load():
            if c.get("id") == conversation_id:
                return ConversationItem(**c)
        return None

    def add_message(
        self, conversation_id: str, role: str, content: str
    ) -> ConversationItem | None:
        conversations = self._load()
        updated = None
        for c in conversations:
            if c.get("id") == conversation_id:
                c.setdefault("messages", []).append(
                    ConversationMessage(role=role, content=content).model_dump(mode="json")
                )
                c["updated_at"] = datetime.utcnow().isoformat()
                updated = c
                break
        if updated:
            self._save(conversations)
            return ConversationItem(**updated)
        return None

    def recent_messages(self, conversation_id: str, limit: int = 20) -> list[ConversationMessage]:
        conversation = self.get(conversation_id)
        if not conversation:
            return []
        return conversation.messages[-limit:]

    def clear(self, conversation_id: str) -> bool:
        conversations = self._load()
        found = False
        for c in conversations:
            if c.get("id") == conversation_id:
                c["messages"] = []
                c["updated_at"] = datetime.utcnow().isoformat()
                found = True
                break
        if found:
            self._save(conversations)
        return found

    def delete(self, conversation_id: str) -> bool:
        conversations = self._load()
        remaining = [c for c in conversations if c.get("id") != conversation_id]
        if len(remaining) == len(conversations):
            return False
        self._save(remaining)
        return True

    def export(self, conversation_id: str) -> dict | None:
        conversation = self.get(conversation_id)
        if not conversation:
            return None
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
                for m in conversation.messages
            ],
        }

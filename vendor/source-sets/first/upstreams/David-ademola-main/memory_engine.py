from __future__ import annotations

import re
from datetime import datetime
from uuid import uuid4

from app.core.storage import JsonStorage
from app.models import MemoryCreate, MemoryItem, MemoryType

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "or",
    "for", "in", "on", "at", "it", "this", "that", "i", "my", "me", "with",
}

_LEARN_PATTERNS: list[tuple[str, MemoryType]] = [
    (r"\bi prefer\b|\bi like\b|\bi want\b", "preference"),
    (r"\bwe decided\b|\bi decided\b|\blet's go with\b", "decision"),
    (r"\bremember\b|\bdon't forget\b|\balways\b|\bnever\b", "instruction"),
    (r"\bproject\b", "project"),
    (r"\btask\b|\btodo\b", "task"),
]


class MemoryEngine:
    """
    Long-term memory store supporting semantic memory, project memory,
    preferences, instructions, decisions, knowledge, and experiences.

    Backed by JSON storage today; the public API is stable so storage
    can later move to PostgreSQL (or a vector store for `relevant()`)
    without changing callers.
    """

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def _load(self) -> list[dict]:
        return self.storage.read("memories", [])

    def _save(self, memories: list[dict]) -> None:
        self.storage.write("memories", memories)

    def add(self, payload: MemoryCreate) -> MemoryItem:
        item = MemoryItem(id=str(uuid4()), **payload.model_dump())
        memories = self._load()
        memories.append(item.model_dump(mode="json"))
        self._save(memories)
        return item

    def all(self, include_archived: bool = False) -> list[MemoryItem]:
        items = [MemoryItem(**m) for m in self._load()]
        if include_archived:
            return items
        return [m for m in items if m.status == "active"]

    def get(self, memory_id: str) -> MemoryItem | None:
        for m in self._load():
            if m.get("id") == memory_id:
                return MemoryItem(**m)
        return None

    def update(
        self,
        memory_id: str,
        content: str | None = None,
        importance: float | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
    ) -> MemoryItem | None:
        memories = self._load()
        updated = None
        for m in memories:
            if m.get("id") == memory_id:
                if content is not None:
                    m["content"] = content
                if importance is not None:
                    m["importance"] = importance
                if confidence is not None:
                    m["confidence"] = confidence
                if tags is not None:
                    m["tags"] = tags
                m["updated_at"] = datetime.utcnow().isoformat()
                updated = m
                break
        if updated:
            self._save(memories)
            return MemoryItem(**updated)
        return None

    def delete(self, memory_id: str) -> bool:
        memories = self._load()
        remaining = [m for m in memories if m.get("id") != memory_id]
        if len(remaining) == len(memories):
            return False
        self._save(remaining)
        return True

    def archive(self, memory_id: str) -> bool:
        memories = self._load()
        found = False
        for m in memories:
            if m.get("id") == memory_id:
                m["status"] = "archived"
                m["updated_at"] = datetime.utcnow().isoformat()
                found = True
                break
        if found:
            self._save(memories)
        return found

    def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        query_terms = {t for t in re.findall(r"\w+", query.lower()) if t not in _STOPWORDS}
        if not query_terms:
            return []

        scored: list[tuple[int, dict]] = []
        for m in self._load():
            if m.get("status") != "active":
                continue
            haystack = f"{m.get('content', '')} {' '.join(m.get('tags', []))}".lower()
            score = sum(1 for term in query_terms if term in haystack)
            if score > 0:
                scored.append((score, m))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [MemoryItem(**m) for _, m in scored[:limit]]

    def recent(self, limit: int = 10, memory_type: MemoryType | None = None) -> list[MemoryItem]:
        items = self.all()
        if memory_type:
            items = [m for m in items if m.type == memory_type]
        items.sort(key=lambda m: m.created_at, reverse=True)
        return items[:limit]

    def relevant(self, context: str, limit: int = 5) -> list[MemoryItem]:
        """
        Rank active memories by relevance to a block of context text,
        weighting keyword overlap by each memory's stored importance.
        """
        context_terms = {t for t in re.findall(r"\w+", context.lower()) if t not in _STOPWORDS}
        if not context_terms:
            return self.recent(limit=limit)

        scored: list[tuple[float, dict]] = []
        for m in self._load():
            if m.get("status") != "active":
                continue
            haystack = f"{m.get('content', '')} {' '.join(m.get('tags', []))}".lower()
            overlap = sum(1 for term in context_terms if term in haystack)
            if overlap == 0:
                continue
            score = overlap * (1 + float(m.get("importance", 0.5)))
            scored.append((score, m))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [MemoryItem(**m) for _, m in scored[:limit]]

    def learn_from_text(self, text: str, source: str = "conversation") -> list[MemoryItem]:
        """
        Lightweight pattern-based extraction that turns a chunk of
        conversation text into candidate memories. Intended to run
        after each chat turn; safe to call with plain, unstructured text.
        """
        learned: list[MemoryItem] = []
        lowered = text.lower()

        matched_type: MemoryType = "general"
        for pattern, mem_type in _LEARN_PATTERNS:
            if re.search(pattern, lowered):
                matched_type = mem_type
                break

        if matched_type == "general" and len(text.strip()) < 12:
            return learned

        candidate = MemoryCreate(
            type=matched_type,
            content=text.strip(),
            confidence=0.6,
            importance=0.5,
            source=source,
            tags=[],
        )
        learned.append(self.add(candidate))
        return learned

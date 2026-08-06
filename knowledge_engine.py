from __future__ import annotations

import re
from datetime import datetime
from uuid import uuid4

from app.core.storage import JsonStorage

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "or",
    "for", "in", "on", "at", "it", "this", "that", "i", "my", "me", "with",
}


class KnowledgeEngine:
    """
    Keyword-based knowledge store: ingest text/document content, tag it
    with a category, and retrieve by keyword overlap and recency.

    This is deliberately NOT a vector-database/embeddings RAG system --
    that requires an embeddings provider and a vector store (pgvector,
    Pinecone, etc.) that aren't configured in this environment. The
    public API (ingest / search / get / delete / categories) is shaped
    so a real embedding-based backend can replace the ranking logic
    inside `search()` later without changing any caller.
    """

    STORE_NAME = "knowledge"

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def _load(self) -> list[dict]:
        return self.storage.read(self.STORE_NAME, [])

    def _save(self, items: list[dict]) -> None:
        self.storage.write(self.STORE_NAME, items)

    def ingest(
        self,
        content: str,
        category: str = "general",
        source: str = "upload",
        tags: list[str] | None = None,
    ) -> dict:
        item = {
            "id": str(uuid4()),
            "content": content,
            "category": category,
            "source": source,
            "tags": tags or [],
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        items = self._load()
        items.append(item)
        self._save(items)
        return item

    def get(self, item_id: str) -> dict | None:
        for item in self._load():
            if item["id"] == item_id:
                return item
        return None

    def categories(self) -> list[str]:
        return sorted({item["category"] for item in self._load()})

    def delete(self, item_id: str) -> bool:
        items = self._load()
        remaining = [i for i in items if i["id"] != item_id]
        if len(remaining) == len(items):
            return False
        self._save(remaining)
        return True

    def search(self, query: str, category: str | None = None, limit: int = 10) -> list[dict]:
        terms = {t for t in re.findall(r"\w+", query.lower()) if t not in _STOPWORDS}
        if not terms:
            return []

        scored: list[tuple[int, dict]] = []
        for item in self._load():
            if category and item.get("category") != category:
                continue
            haystack = f"{item['content']} {' '.join(item.get('tags', []))}".lower()
            score = sum(1 for term in terms if term in haystack)
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def retrieve_context(self, query: str, max_items: int = 3, max_chars: int = 2000) -> str:
        """
        Builds a compact context block for a chat request: the top
        matching knowledge entries, trimmed to a character budget so
        it doesn't blow out a provider's context window.
        """
        results = self.search(query, limit=max_items)
        context_parts: list[str] = []
        budget = max_chars
        for item in results:
            snippet = item["content"][:400]
            if len(snippet) > budget:
                break
            context_parts.append(snippet)
            budget -= len(snippet)
        return "\n---\n".join(context_parts)

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.storage import JsonStorage
from app.services.knowledge_engine import KnowledgeEngine

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def get_engine() -> KnowledgeEngine:
    return KnowledgeEngine(JsonStorage())


class IngestRequest(BaseModel):
    content: str
    category: str = "general"
    source: str = "upload"
    tags: list[str] = []


@router.post("/ingest")
def ingest(
    payload: IngestRequest,
    engine: KnowledgeEngine = Depends(get_engine),
) -> dict:
    return engine.ingest(
        content=payload.content,
        category=payload.category,
        source=payload.source,
        tags=payload.tags,
    )


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    category: str | None = None,
    engine: KnowledgeEngine = Depends(get_engine),
) -> list[dict]:
    return engine.search(q, category=category)


@router.get("/categories")
def categories(engine: KnowledgeEngine = Depends(get_engine)) -> list[str]:
    return engine.categories()


@router.delete("/{item_id}")
def delete(item_id: str, engine: KnowledgeEngine = Depends(get_engine)) -> dict:
    ok = engine.delete(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return {"ok": True}

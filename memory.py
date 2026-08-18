from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import Settings, get_settings
from app.core.storage import JsonStorage
from app.models import MemoryCreate, MemoryItem
from app.services.memory_engine import MemoryEngine
from app.services.supabase_service import SupabasePersistence

router = APIRouter(prefix="/memory", tags=["memory"])


def get_engine(settings: Settings = Depends(get_settings)) -> MemoryEngine:
    return MemoryEngine(JsonStorage(), SupabasePersistence(settings))


@router.get("", response_model=list[MemoryItem])
def list_memories(engine: MemoryEngine = Depends(get_engine)) -> list[MemoryItem]:
    return engine.all()


@router.get("/search", response_model=list[MemoryItem])
def search_memories(
    q: str = Query(..., min_length=1),
    engine: MemoryEngine = Depends(get_engine),
) -> list[MemoryItem]:
    return engine.search(q)


@router.get("/recent", response_model=list[MemoryItem])
def recent_memories(
    limit: int = 10,
    engine: MemoryEngine = Depends(get_engine),
) -> list[MemoryItem]:
    return engine.recent(limit=limit)


@router.post("", response_model=MemoryItem)
def add_memory(
    payload: MemoryCreate,
    engine: MemoryEngine = Depends(get_engine),
) -> MemoryItem:
    return engine.add(payload)


@router.delete("/{memory_id}")
def archive_memory(
    memory_id: str,
    engine: MemoryEngine = Depends(get_engine),
) -> dict[str, bool]:
    ok = engine.archive(memory_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"ok": True}

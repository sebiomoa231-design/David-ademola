from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.source_integrations import get_source_pack, list_source_packs

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/sources")
def source_integrations() -> dict[str, object]:
    sources = list_source_packs()
    return {
        "status": "ready",
        "primary_repository": "https://github.com/sebiomoa231-design/David-ademola",
        "count": len(sources),
        "sources": sources,
    }


@router.get("/sources/{source_id}")
def source_integration(source_id: str) -> dict[str, object]:
    source = get_source_pack(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source integration not found")
    return {"status": "ready", "source": source}

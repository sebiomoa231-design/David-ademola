import json
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.services.supabase_service import SupabasePersistence
from app.services.website_engine import WebsiteEngine

router = APIRouter(prefix="/website", tags=["website"])
engine = WebsiteEngine()


class WebsiteRequest(BaseModel):
    prompt: str
    project_id: str | None = None


class WebsiteSection(BaseModel):
    component_type: str
    title: str
    subtitle: str
    body: str
    buttons: list[str]
    image_placeholder: str
    layout: str


class WebsiteResponse(BaseModel):
    title: str
    sections: list[WebsiteSection]
    notes: list[str]
    generation_id: str | None = None


@router.post("/generate", response_model=WebsiteResponse)
def generate_website(
    payload: WebsiteRequest,
    settings: Settings = Depends(get_settings),
) -> WebsiteResponse:
    result: dict[str, Any] = engine.generate(payload.prompt)
    generation_id: str | None = None
    persistence = SupabasePersistence(settings)
    if persistence.database_enabled:
        stored = persistence.create_generation(
            {
                "project_id": payload.project_id,
                "kind": "website",
                "prompt": payload.prompt,
                "provider": "website-engine",
                "status": "completed",
                "output": json.dumps(result),
                "metadata": {"section_count": len(result.get("sections", []))},
            }
        )
        generation_id = str(stored.get("id"))
    return WebsiteResponse(**result, generation_id=generation_id)

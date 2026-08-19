import json
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.services.supabase_service import SupabasePersistence
from app.services.website_engine import WebsiteEngine
from storage import JsonStorage
from website_preview import render_website_html

router = APIRouter(prefix="/website", tags=["website"])
engine = WebsiteEngine()
local_store = JsonStorage()


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
    html: str
    preview_url: str
    generation_id: str
    persistence_status: str


def _local_artifacts() -> list[dict[str, Any]]:
    rows = local_store.read("website_artifacts", [])
    return rows if isinstance(rows, list) else []


@router.post("/generate", response_model=WebsiteResponse)
def generate_website(
    payload: WebsiteRequest,
    settings: Settings = Depends(get_settings),
) -> WebsiteResponse:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="A website prompt is required.")
    result: dict[str, Any] = engine.generate(prompt)
    html = render_website_html(result, prompt)
    generation_id = str(uuid4())
    artifact = {**result, "html": html, "prompt": prompt, "generation_id": generation_id}
    persistence = SupabasePersistence(settings)
    persistence_status = "local-only"
    if persistence.database_enabled:
        persistence.create_generation(
            {
                "id": generation_id,
                "project_id": payload.project_id,
                "kind": "website",
                "prompt": prompt,
                "provider": "website-engine",
                "status": "completed",
                "output": json.dumps(artifact),
                "metadata": {"section_count": len(result.get("sections", [])), "preview_url": f"/api/website/{generation_id}"},
            }
        )
        persistence_status = "persisted"
    else:
        local_store.append(
            "website_artifacts",
            {"id": generation_id, "project_id": payload.project_id, "kind": "website", "status": "completed", "output": json.dumps(artifact)},
        )
    return WebsiteResponse(
        **result,
        html=html,
        preview_url=f"/api/website/{generation_id}",
        generation_id=generation_id,
        persistence_status=persistence_status,
    )


@router.get("/{generation_id}", response_class=HTMLResponse, summary="Open a generated website preview")
def get_website_preview(generation_id: str, settings: Settings = Depends(get_settings)) -> HTMLResponse:
    artifact: dict[str, Any] | None = None
    for row in _local_artifacts():
        if str(row.get("id")) == generation_id:
            try:
                artifact = json.loads(str(row.get("output") or "{}"))
            except json.JSONDecodeError:
                artifact = None
            break
    if artifact is None:
        persistence = SupabasePersistence(settings)
        if persistence.database_enabled:
            rows = persistence.require_database().select("david_generations", {"select": "output", "id": f"eq.{generation_id}", "limit": "1"})
            if rows:
                try:
                    artifact = json.loads(str(rows[0].get("output") or "{}"))
                except json.JSONDecodeError:
                    artifact = None
    if not artifact or not isinstance(artifact.get("html"), str):
        raise HTTPException(status_code=404, detail="Generated website preview was not found.")
    return HTMLResponse(content=artifact["html"])

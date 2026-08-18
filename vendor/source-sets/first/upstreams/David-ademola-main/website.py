from fastapi import APIRouter
from pydantic import BaseModel

from app.services.website_engine import WebsiteEngine

router = APIRouter(prefix="/website", tags=["website"])
engine = WebsiteEngine()


class WebsiteRequest(BaseModel):
    prompt: str


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


@router.post("/generate", response_model=WebsiteResponse)
def generate_website(payload: WebsiteRequest) -> WebsiteResponse:
    return WebsiteResponse(**engine.generate(payload.prompt))

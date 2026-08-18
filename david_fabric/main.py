from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from david_fabric.core.config import settings
from david_fabric.api.router import api_router
from david_fabric.storage.db import init_db

app = FastAPI(
    title="David AI — Intelligence Fabric",
    version="2.0.0-fabric",
    description="Unified control plane for David AI capabilities and internal integrations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup() -> None:
    init_db()

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "name": "David AI",
        "component": "Intelligence Fabric",
        "version": "2.0.0-fabric",
        "status": "running",
    }

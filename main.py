from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import log_shutdown, log_startup

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    log_startup()


@app.on_event("shutdown")
def on_shutdown() -> None:
    log_shutdown()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "David AI backend is running"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "1.5-final"}

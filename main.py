from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import log_request, log_shutdown, log_startup
from app.core.security import check_rate_limit

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from agents import manager as agent_manager

    log_startup()
    try:
        yield
    finally:
        await agent_manager.shutdown()
        log_shutdown()


app = FastAPI(
    title=settings.app_name,
    version="1.5-final",
    debug=settings.debug,
    lifespan=lifespan,
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    check_rate_limit(request)
    log_request(request.method, request.url.path)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "David AI backend is running", "version": "1.5-final"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "1.5-final"}

from fastapi import APIRouter, Depends, HTTPException

from app.core.storage import JsonStorage
from app.models_auth import AuthUser, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_service() -> AuthService:
    return AuthService(JsonStorage())


@router.get("/users", response_model=list[AuthUser])
def users(service: AuthService = Depends(get_service)) -> list[AuthUser]:
    return service.list_users()


@router.post("/register", response_model=AuthUser)
def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_service),
) -> AuthUser:
    try:
        return service.register(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login", response_model=AuthUser)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_service),
) -> AuthUser:
    try:
        return service.login(payload)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

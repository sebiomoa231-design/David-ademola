from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.core.storage import JsonStorage
from app.models_auth import AuthUser, LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def list_users(self) -> list[AuthUser]:
        return [AuthUser(**item) for item in self.storage.read("users", [])]

    def register(self, payload: RegisterRequest) -> AuthUser:
        users = self.storage.read("users", [])
        for user in users:
            if user.get("email") == payload.email:
                raise ValueError("User already exists")

        user = AuthUser(
            id=str(uuid4()),
            name=payload.name,
            email=payload.email,
            created_at=datetime.utcnow(),
        )
        users.append(user.model_dump(mode="json"))
        self.storage.write("users", users)
        return user

    def login(self, payload: LoginRequest) -> AuthUser:
        for user in self.list_users():
            if user.email == payload.email:
                return user
        raise ValueError("Invalid credentials")

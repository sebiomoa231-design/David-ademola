from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=256)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)


class AuthUser(BaseModel):
    id: str
    name: str
    email: str
    role: Literal["owner", "administrator", "user"] = "user"
    status: Literal["pending", "approved", "suspended"] = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

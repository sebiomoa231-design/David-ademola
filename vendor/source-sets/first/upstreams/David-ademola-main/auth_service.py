from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime
from uuid import uuid4

from app.core.config import get_settings
from app.core.storage import JsonStorage
from app.models_auth import AuthUser, LoginRequest, RegisterRequest


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    )
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "scrypt":
            return False
        candidate = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


class AuthService:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def _ensure_owner(self) -> None:
        settings = get_settings()
        if not settings.owner_email or not settings.owner_password:
            return

        users = self.storage.read("users", [])
        normalized = settings.owner_email.strip().lower()
        for user in users:
            if user.get("email", "").lower() == normalized:
                return

        owner = {
            "id": str(uuid4()),
            "name": "My Lord",
            "email": normalized,
            "role": "owner",
            "status": "approved",
            "password_hash": _hash_password(settings.owner_password),
            "created_at": datetime.utcnow().isoformat(),
        }
        users.append(owner)
        self.storage.write("users", users)

    def list_users(self) -> list[AuthUser]:
        self._ensure_owner()
        return [
            AuthUser(**{k: v for k, v in item.items() if k != "password_hash"})
            for item in self.storage.read("users", [])
        ]

    def register(self, payload: RegisterRequest) -> AuthUser:
        self._ensure_owner()
        users = self.storage.read("users", [])
        email = payload.email.strip().lower()

        for user in users:
            if user.get("email", "").lower() == email:
                raise ValueError("User already exists")

        user = {
            "id": str(uuid4()),
            "name": payload.name.strip(),
            "email": email,
            "role": "user",
            "status": "pending",
            "password_hash": _hash_password(payload.password),
            "created_at": datetime.utcnow().isoformat(),
        }
        users.append(user)
        self.storage.write("users", users)
        return AuthUser(**{k: v for k, v in user.items() if k != "password_hash"})

    def login(self, payload: LoginRequest) -> AuthUser:
        self._ensure_owner()
        email = payload.email.strip().lower()

        for user in self.storage.read("users", []):
            if user.get("email", "").lower() != email:
                continue

            if not _verify_password(payload.password, user.get("password_hash", "")):
                break

            if user.get("status") != "approved":
                raise ValueError("Account is pending approval or suspended")

            return AuthUser(**{k: v for k, v in user.items() if k != "password_hash"})

        raise ValueError("Invalid credentials")

"""
PROJECT THEMIS - Auth Store
Version: 5.0

In-memory user store for operator accounts.
Seeded with a default operator on first use.
"""

import threading
import secrets
from typing import Dict, Optional

from app.core.security import hash_password, verify_password


class AuthUser:
    def __init__(self, id: str, name: str, email: str, password_hash: str):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email}


class AuthStore:
    """Thread-safe in-memory user store."""

    def __init__(self):
        self._lock = threading.RLock()
        self._users: Dict[str, AuthUser] = {}
        self._seed_default()

    def _seed_default(self):
        default = AuthUser(
            id="usr_operator",
            name="Operator THEMIS",
            email="operator@themis.ai",
            password_hash=hash_password("themis123"),
        )
        self._users[default.email.lower()] = default

    def register(self, name: str, email: str, password: str) -> Optional[AuthUser]:
        with self._lock:
            key = email.lower()
            if key in self._users:
                return None
            if len(password) < 6:
                return None
            user = AuthUser(
                id=f"usr_{secrets.token_hex(6)}",
                name=name,
                email=email,
                password_hash=hash_password(password),
            )
            self._users[key] = user
            return user

    def authenticate(self, email: str, password: str) -> Optional[AuthUser]:
        with self._lock:
            key = email.lower()
            user = self._users.get(key)
            if user and verify_password(password, user.password_hash):
                return user
            return None

    def get_by_id(self, user_id: str) -> Optional[AuthUser]:
        with self._lock:
            for user in self._users.values():
                if user.id == user_id:
                    return user
            return None

    def get_by_email(self, email: str) -> Optional[AuthUser]:
        with self._lock:
            return self._users.get(email.lower())


auth_store = AuthStore()
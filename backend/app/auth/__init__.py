"""
PROJECT THEMIS - Auth Module
Version: 5.0

In-memory user store, token & API key management for operator login/register
and machine-to-machine access (Unity Digital Twin).
"""

from app.auth.store import auth_store, AuthUser
from app.core.security import verify_api_key, create_token, decode_token, hash_password, verify_password

__all__ = [
    "auth_store",
    "AuthUser",
    "verify_api_key",
    "create_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
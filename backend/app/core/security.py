"""
PROJECT THEMIS - Core Security
Version: 5.0

Token generation/verification and API key validation.
No external crypto dependencies - uses hashlib + secrets.
"""

import base64
import hashlib
import hmac
import json
import secrets
from typing import Optional

from app.config.settings import settings


def hash_password(password: str) -> str:
    """Hash a password with a random salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations=100_000)
    return f"pbkdf2_sha256${100000}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        algo, iterations, salt_hex, hash_hex = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations=int(iterations))
        return hmac.compare_digest(dk, expected)
    except (ValueError, AttributeError):
        return False


def create_token(user_id: str, email: str) -> str:
    """Create a signed bearer token for a user."""
    payload = {"sub": user_id, "email": email}
    raw = json.dumps(payload, separators=(",", ":"))
    body = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
    sig = hmac.new(
        settings.JWT_SECRET.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{body}.{sig}"


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a bearer token. Returns payload or None."""
    if not token or "." not in token:
        return None
    body, sig = token.rsplit(".", 1)
    expected_sig = hmac.new(
        settings.JWT_SECRET.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None
    try:
        raw = base64.urlsafe_b64decode(body.encode("ascii")).decode("utf-8")
        return json.loads(raw)
    except Exception:
        return None


def verify_api_key(provided: Optional[str]) -> bool:
    """Verify a provided API key against the configured Unity API key."""
    if not provided:
        return False
    return hmac.compare_digest(provided, settings.API_KEY)
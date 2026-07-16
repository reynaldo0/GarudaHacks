"""
PROJECT THEMIS - Auth API Endpoint
Version: 5.0

Operator login & register endpoints.
Returns a signed bearer token for the Operation Center dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.auth.store import auth_store
from app.core.security import create_token, decode_token
from app.config.settings import settings

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


def current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """Dependency that resolves the current user from a Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = auth_store.get_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user.to_dict()


@router.post("/auth/login")
async def login(body: LoginRequest):
    """Operator login. Returns user + signed token."""
    user = auth_store.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user.id, user.email)
    return {
        "success": True,
        "data": {
            "user": user.to_dict(),
            "token": token,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.post("/auth/register")
async def register(body: RegisterRequest):
    """Operator register. Returns user + signed token."""
    if not body.name or not body.email or not body.password:
        raise HTTPException(status_code=400, detail="All fields are required")

    user = auth_store.register(body.name, body.email, body.password)
    if not user:
        raise HTTPException(status_code=409, detail="Email already registered or password too short")

    token = create_token(user.id, user.email)
    return {
        "success": True,
        "data": {
            "user": user.to_dict(),
            "token": token,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/auth/me")
async def me(user: dict = Depends(current_user)):
    """Return the current authenticated user."""
    return {"success": True, "data": {"user": user}}


@router.get("/auth/api-key")
async def get_api_key(user: dict = Depends(current_user)):
    """Return the Unity API key for authenticated operators."""
    return {
        "success": True,
        "data": {
            "api_key": settings.API_KEY,
            "note": "Use this key in the X-API-Key header for Unity frame uploads.",
        },
    }
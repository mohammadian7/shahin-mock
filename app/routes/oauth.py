"""OAuth token endpoint."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings

router = APIRouter()
_basic = HTTPBasic(auto_error=False)

# Simple opaque tokens keyed by value (dev only).
_issued_tokens: set[str] = set()


def _verify_basic(credentials: HTTPBasicCredentials | None) -> None:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Basic credentials")
    if (
        credentials.username != settings.client_id
        or credentials.password != settings.client_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid client credentials")


@router.post("/v0.3/obh/oauth/token")
async def oauth_token(
    request: Request,
    credentials: HTTPBasicCredentials | None = Depends(_basic),
):
    _verify_basic(credentials)
    token = secrets.token_urlsafe(32)
    _issued_tokens.add(token)
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": settings.token_ttl_sec,
    }

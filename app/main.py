"""Shahin OBH mock API for payout-hub integration tests."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import account, inquiry, oauth, transfer
from app.signing import verify_inbound

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shahin-mock")

app = FastAPI(title="Shahin Mock", version="0.1.0")

_SKIP_AUTH_PREFIXES = ("/v0.3/obh/oauth/", "/health", "/docs", "/openapi.json", "/redoc")


@app.middleware("http")
async def obh_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in _SKIP_AUTH_PREFIXES):
        return await call_next(request)

    if path.startswith("/v0.3/obh/api/"):
        auth = request.headers.get("authorization") or ""
        if not auth.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "missing_bearer_token"},
            )

        if settings.verify_hmac:
            body = await request.body()

            async def receive():
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive  # noqa: SLF001
            headers = {k.lower(): v for k, v in request.headers.items()}
            if not verify_inbound(secret=settings.hmac_secret, headers=headers, raw_body=body):
                return JSONResponse(
                    status_code=401,
                    content={"error": "invalid_obh_signature"},
                )

    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "shahin-mock"}


app.include_router(oauth.router)
app.include_router(transfer.router)
app.include_router(inquiry.router)
app.include_router(account.router)

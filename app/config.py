"""Environment-driven mock settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, str(default)).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    client_id: str = os.environ.get("MOCK_CLIENT_ID", "mock-client")
    client_secret: str = os.environ.get("MOCK_CLIENT_SECRET", "mock-secret")
    hmac_secret: str = os.environ.get(
        "MOCK_HMAC_SECRET", "dev-hmac-secret-change-me-32b"
    )
    callback_secret: str = os.environ.get(
        "MOCK_CALLBACK_SECRET", "dev-callback-secret-change-me-32b"
    )
    callback_url: str = os.environ.get(
        "MOCK_CALLBACK_URL",
        "http://web:8000/api/v1/callbacks/shahin/shahin-mock/",
    )
    callback_delay_sec: float = _float("MOCK_CALLBACK_DELAY_SEC", 2.0)
    inquiry_delay_sec: float = _float("MOCK_INQUIRY_DELAY_SEC", 0.0)
    verify_hmac: bool = _bool("MOCK_VERIFY_HMAC", False)
    token_ttl_sec: int = int(os.environ.get("MOCK_TOKEN_TTL_SEC", "3600"))
    signing_template: str = os.environ.get("MOCK_SIGNING_TEMPLATE", "uuid_ts")


settings = Settings()

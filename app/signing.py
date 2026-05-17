"""OBH HMAC signing (uuid_ts) — aligned with payout-hub apps.providers.shahin.signing."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid


def epoch_ms_13() -> str:
    return str(int(time.time() * 1000))[:13]


def sign_request(
    *,
    secret: str,
    body: bytes,
    uuid_value: str | None = None,
    timestamp: str | None = None,
) -> dict[str, str]:
    uuid_value = uuid_value or str(uuid.uuid4())
    timestamp = timestamp or epoch_ms_13()
    string_to_sign = f"{uuid_value}\n{timestamp}".encode()
    digest = hmac.new(secret.encode("utf-8"), string_to_sign, hashlib.sha256).hexdigest().upper()
    signature = (
        f"OBH1-HMAC-SHA256;SignedHeaders=X-Obh-uuid,X-Obh-timestamp;Signature={digest}"
    )
    return {
        "X-Obh-signature": signature,
        "X-Obh-uuid": uuid_value,
        "X-Obh-timestamp": timestamp,
    }


def verify_inbound(
    *,
    secret: str,
    headers: dict[str, str],
    raw_body: bytes,
) -> bool:
    uuid_value = headers.get("x-obh-uuid") or headers.get("X-Obh-uuid")
    timestamp = headers.get("x-obh-timestamp") or headers.get("X-Obh-timestamp")
    sig_header = headers.get("x-obh-signature") or headers.get("X-Obh-signature")
    if not (uuid_value and timestamp and sig_header):
        return False
    expected = sign_request(
        secret=secret,
        body=raw_body or b"",
        uuid_value=str(uuid_value),
        timestamp=str(timestamp),
    )
    return hmac.compare_digest(
        sig_header.strip().upper(),
        expected["X-Obh-signature"].strip().upper(),
    )

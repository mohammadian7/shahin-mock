"""Fire signed callbacks to payout-hub after a successful transfer."""

from __future__ import annotations

import asyncio
import json
import logging

import httpx

from app.config import settings
from app.signing import sign_request
from app.store import store

logger = logging.getLogger(__name__)


async def schedule_success_callback(requested_uuid: str, transaction_id: str) -> None:
    if not settings.callback_url:
        return
    delay = max(0.0, settings.callback_delay_sec)
    asyncio.create_task(_send_callback(requested_uuid, transaction_id, delay))


async def _send_callback(requested_uuid: str, transaction_id: str, delay: float) -> None:
    if delay:
        await asyncio.sleep(delay)
    store.mark_done(requested_uuid)
    body = {
        "requestedUuid": requested_uuid,
        "uuid": requested_uuid,
        "transactionId": transaction_id,
        "status": "DONE",
    }
    body_bytes = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        **sign_request(secret=settings.callback_secret, body=body_bytes),
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(settings.callback_url, content=body_bytes, headers=headers)
            logger.info(
                "Callback %s -> %s %s",
                requested_uuid,
                resp.status_code,
                resp.text[:200],
            )
    except Exception:
        logger.exception("Callback failed for %s", requested_uuid)

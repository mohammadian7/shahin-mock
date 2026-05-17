"""Transaction inquiry endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.store import store

router = APIRouter()


@router.post("/v0.3/obh/api/pisp/transaction-inquiry")
async def transaction_inquiry(request: Request) -> dict[str, Any]:
    body: dict[str, Any] = await request.json()
    requested_uuid = str(
        body.get("requestedUuid") or body.get("uuid") or body.get("requested_uuid") or ""
    )
    if not requested_uuid:
        raise HTTPException(status_code=400, detail="requestedUuid is required")

    record = store.get_by_uuid(requested_uuid)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Unknown requestedUuid: {requested_uuid}")

    status = store.inquiry_status(record, settings.inquiry_delay_sec)
    return {
        "result": {
            "uuid": record.requested_uuid,
            "requestedUuid": record.requested_uuid,
            "transactionId": record.transaction_id,
            "status": status,
            "transferStatus": status,
        }
    }

"""PISP transfer endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.callbacks import schedule_success_callback
from app.store import store

router = APIRouter()


def _transfer_response(record) -> dict[str, Any]:
    return {
        "requestedUuid": record.requested_uuid,
        "transactionId": record.transaction_id,
        "status": "ACCEPTED",
        "result": {
            "uuid": record.requested_uuid,
            "requestedUuid": record.requested_uuid,
            "transactionId": record.transaction_id,
            "status": "ACCEPTED",
        },
    }


async def _handle_transfer(request: Request, operation: str) -> dict[str, Any]:
    body: dict[str, Any] = await request.json()
    transfer_id = str(body.get("transferID") or body.get("transferId") or "")
    amount = str(body.get("amount") or "0")
    record = store.get_or_create_transfer(
        transfer_id=transfer_id,
        amount=amount,
        operation=operation,
    )
    await schedule_success_callback(record.requested_uuid, record.transaction_id)
    return _transfer_response(record)


@router.post("/v0.3/obh/api/pisp/transfer")
async def transfer(request: Request):
    return await _handle_transfer(request, "transfer")


@router.post("/v0.3/obh/api/pisp/transfer-to")
async def transfer_to(request: Request):
    return await _handle_transfer(request, "transfer-to")

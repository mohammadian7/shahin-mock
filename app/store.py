"""In-memory transfer state for the mock Shahin API."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class TransferRecord:
    requested_uuid: str
    transaction_id: str
    transfer_id: str
    amount: str
    operation: str
    status: str
    created_at: float = field(default_factory=time.time)


class TransferStore:
    def __init__(self) -> None:
        self._by_uuid: dict[str, TransferRecord] = {}
        self._by_transfer_id: dict[str, str] = {}
        self._lock = Lock()

    def get_or_create_transfer(
        self,
        *,
        transfer_id: str,
        amount: str,
        operation: str,
    ) -> TransferRecord:
        with self._lock:
            if transfer_id and transfer_id in self._by_transfer_id:
                existing_uuid = self._by_transfer_id[transfer_id]
                return self._by_uuid[existing_uuid]

            requested_uuid = str(uuid.uuid4())
            transaction_id = f"MOCK-TXN-{requested_uuid[:8].upper()}"
            record = TransferRecord(
                requested_uuid=requested_uuid,
                transaction_id=transaction_id,
                transfer_id=transfer_id or requested_uuid,
                amount=amount,
                operation=operation,
                status="PROCESSING",
            )
            self._by_uuid[requested_uuid] = record
            if transfer_id:
                self._by_transfer_id[transfer_id] = requested_uuid
            return record

    def get_by_uuid(self, requested_uuid: str) -> TransferRecord | None:
        with self._lock:
            return self._by_uuid.get(requested_uuid)

    def inquiry_status(self, record: TransferRecord, inquiry_delay_sec: float) -> str:
        elapsed = time.time() - record.created_at
        if elapsed < inquiry_delay_sec:
            return "PROCESSING"
        return "DONE"

    def mark_done(self, requested_uuid: str) -> None:
        with self._lock:
            rec = self._by_uuid.get(requested_uuid)
            if rec:
                rec.status = "DONE"


store = TransferStore()

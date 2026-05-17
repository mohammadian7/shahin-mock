"""AISP account endpoints — static success payloads for dev."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

_ACCOUNT_PATHS = (
    "get-account-info",
    "get-account-balance",
    "get-account-list",
    "get-account-statement",
    "get-iban",
    "get-iban-info",
    "get-chequebook-list",
    "get-cheque-statement",
    "get-basic-custinfo",
    "get-detail-custinfo",
    "get-loan-info",
    "get-loan-statement",
)


def _require_account_fields(body: dict[str, Any]) -> dict[str, str]:
    bank = str(body.get("bank") or "")
    national_code = str(body.get("nationalCode") or "")
    source_account = str(body.get("sourceAccount") or "")
    if not (bank and national_code and source_account):
        raise HTTPException(
            status_code=400,
            detail="bank, nationalCode, and sourceAccount are required",
        )
    return {
        "bank": bank,
        "nationalCode": national_code,
        "sourceAccount": source_account,
    }


def _account_result(fields: dict[str, str], endpoint: str) -> dict[str, Any]:
    base: dict[str, Any] = {
        "bank": fields["bank"],
        "nationalCode": fields["nationalCode"],
        "accountNumber": fields["sourceAccount"],
        "currency": "IRR",
        "status": "ACTIVE",
    }
    if endpoint == "get-account-balance":
        base["balance"] = "1000000000"
        base["availableBalance"] = "1000000000"
    elif endpoint == "get-account-list":
        return {"result": {"accounts": [{**base, "label": "Primary"}]}}
    elif endpoint == "get-account-statement":
        return {"result": {**base, "transactions": []}}
    elif endpoint == "get-iban":
        base["iban"] = f"IR370190000009{fields['sourceAccount'][-10:]}"
    elif endpoint == "get-iban-info":
        base["iban"] = fields["sourceAccount"]
        base["ownerName"] = "MOCK_ACCOUNT_HOLDER"
    elif endpoint.startswith("get-loan"):
        base["loanNumber"] = "MOCK-LOAN-001"
        base["balance"] = "0"
    elif endpoint.startswith("get-cheque"):
        base["items"] = []
    elif "custinfo" in endpoint:
        base["customerName"] = "MOCK_CUSTOMER"
    return {"result": base}


async def account_endpoint(request: Request, endpoint: str) -> dict[str, Any]:
    body: dict[str, Any] = await request.json()
    fields = _require_account_fields(body)
    return _account_result(fields, endpoint)


def _register(path: str) -> None:
    async def handler(request: Request, _endpoint: str = path):
        return await account_endpoint(request, _endpoint)

    router.add_api_route(
        f"/v0.3/obh/api/aisp/{path}",
        handler,
        methods=["POST"],
        name=path,
    )


for _p in _ACCOUNT_PATHS:
    _register(_p)

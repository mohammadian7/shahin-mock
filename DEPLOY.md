# Deploy shahin-mock with payout-hub (172.16.1.72)

| Service | URL |
|---------|-----|
| **payout-hub** | http://172.16.1.72:8020 |
| **shahin-mock** | http://172.16.1.72:8005 |

Repository: https://github.com/mohammadian7/shahin-mock

## How they connect

```text
payout-hub (worker)  --transfer/inquiry-->  shahin-mock :8005
shahin-mock          --callback POST-->      payout-hub :8020
```

## Dokploy — shahin-mock app

| Setting | Value |
|---------|--------|
| Repository | `mohammadian7/shahin-mock` |
| Branch | `main` |
| Dockerfile | `Dockerfile` |
| Container port | **8005** |
| Host port | **8005** (bind `0.0.0.0:8005`) |
| Health check | `GET /health` on port **8005** |

### Environment (required for payout-hub integration)

```env
MOCK_CLIENT_ID=mock-client
MOCK_CLIENT_SECRET=mock-secret
MOCK_HMAC_SECRET=dev-hmac-secret-change-me-32b
MOCK_CALLBACK_SECRET=dev-callback-secret-change-me-32b
MOCK_CALLBACK_URL=http://172.16.1.72:8020/api/v1/callbacks/shahin/shahin-mock/
MOCK_CALLBACK_DELAY_SEC=2
MOCK_INQUIRY_DELAY_SEC=0
MOCK_VERIFY_HMAC=false
```

`MOCK_CALLBACK_*` secrets must match the **payout-hub Gateway** `shahin-mock` secrets (`callback_signing_secret`).

## Dokploy — payout-hub gateway

Use the same values as [`payout-hub/gateways_configs/shahin/config.mock.json`](https://github.com/mohammadian7/shahin-mock) (in payout-hub repo):

```json
"auth_url": "http://172.16.1.72:8005/v0.3/obh/oauth/token",
"api_base": "http://172.16.1.72:8005/",
"callback_url": "http://172.16.1.72:8020/api/v1/callbacks/shahin/shahin-mock/"
```

Gateway secrets:

```json
{
  "client_id": "mock-client",
  "client_secret": "mock-secret",
  "hmac_signing_secret": "dev-hmac-secret-change-me-32b",
  "callback_signing_secret": "dev-callback-secret-change-me-32b"
}
```

On payout-hub server:

```bash
docker compose exec web python manage.py seed_shahin_mock --run-seed-demo
```

Ensure gateway `shahin-mock` is **ACTIVE**.

## Smoke tests

```bash
# mock
curl http://172.16.1.72:8005/health

curl -u mock-client:mock-secret -X POST \
  "http://172.16.1.72:8005/v0.3/obh/oauth/token?grant_type=client_credentials&bank=BSI"

# payout-hub
curl http://172.16.1.72:8020/api/v1/health/
```

## Local docker compose (both on same machine)

From `payout-hub/`:

```bash
docker compose up --build
docker compose exec web python manage.py seed_shahin_mock --run-seed-demo
```

Compose publishes mock on **8005** and sets `MOCK_CALLBACK_URL` to `172.16.1.72:8020`.

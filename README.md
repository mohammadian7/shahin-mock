# shahin-mock

Mock of Shahin OBH **2Way** APIs for [payout-hub](https://github.com/mohammadian7/shahin-mock) integration tests.

**Repository:** https://github.com/mohammadian7/shahin-mock  
**Default port:** `8005`  
**Deploy guide:** [DEPLOY.md](DEPLOY.md)

## Endpoints

| Method | Path |
|--------|------|
| GET | `/health` |
| POST | `/v0.3/obh/oauth/token` |
| POST | `/v0.3/obh/api/pisp/transfer` |
| POST | `/v0.3/obh/api/pisp/transfer-to` |
| POST | `/v0.3/obh/api/pisp/transaction-inquiry` |
| POST | `/v0.3/obh/api/aisp/*` (12 account endpoints) |

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005
```

## Docker

```bash
docker build -t shahin-mock .
docker run --rm -p 8005:8005 shahin-mock
curl http://localhost:8005/health
```

## Environment

| Variable | Default |
|----------|---------|
| `MOCK_CLIENT_ID` | `mock-client` |
| `MOCK_CLIENT_SECRET` | `mock-secret` |
| `MOCK_HMAC_SECRET` | `dev-hmac-secret-change-me-32b` |
| `MOCK_CALLBACK_SECRET` | `dev-callback-secret-change-me-32b` |
| `MOCK_CALLBACK_URL` | `http://web:8000/api/v1/callbacks/shahin/shahin-mock/` |
| `MOCK_CALLBACK_DELAY_SEC` | `2` |
| `MOCK_INQUIRY_DELAY_SEC` | `0` |
| `MOCK_VERIFY_HMAC` | `false` |

## With payout-hub (docker compose)

Point gateway `config.mock.json` at `http://shahin-mock:8005/` and run `seed_shahin_mock` on payout-hub.

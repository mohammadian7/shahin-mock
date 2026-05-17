# shahin-mock

Mock of Shahin OBH **2Way** APIs for **payout-hub** integration tests.

| Service | Default URL |
|---------|-------------|
| **This mock** | http://172.16.1.72:8005 |
| **payout-hub** | http://172.16.1.72:8020 |

**Repository:** https://github.com/mohammadian7/shahin-mock  
**Deploy:** [DEPLOY.md](DEPLOY.md)

## Integration flow

1. payout-hub Celery worker calls mock at `172.16.1.72:8005` (transfer / inquiry).
2. mock sends signed callback to `http://172.16.1.72:8020/api/v1/callbacks/shahin/shahin-mock/`.
3. payout marks payout `SUCCESS` (~2s after transfer).

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005
```

```bash
docker build -t shahin-mock .
docker run --rm -p 8005:8005 \
  -e MOCK_CALLBACK_URL=http://172.16.1.72:8020/api/v1/callbacks/shahin/shahin-mock/ \
  shahin-mock
```

## Environment

| Variable | Default (172.16.1.72 setup) |
|----------|-----------------------------|
| `MOCK_CALLBACK_URL` | `http://172.16.1.72:8020/api/v1/callbacks/shahin/shahin-mock/` |
| `MOCK_CLIENT_ID` | `mock-client` |
| `MOCK_CLIENT_SECRET` | `mock-secret` |
| `MOCK_HMAC_SECRET` | `dev-hmac-secret-change-me-32b` |
| `MOCK_CALLBACK_SECRET` | `dev-callback-secret-change-me-32b` |

Must match payout-hub Gateway `shahin-mock` secrets.

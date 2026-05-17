# Deploy shahin-mock (Dokploy + GitHub)

Repository: https://github.com/mohammadian7/shahin-mock

## GitHub

```bash
git clone https://github.com/mohammadian7/shahin-mock.git
cd shahin-mock
```

## Dokploy

| Setting | Value |
|---------|--------|
| Type | Application → Build from **Dockerfile** |
| Repository | `mohammadian7/shahin-mock` |
| Branch | `main` |
| Dockerfile path | `Dockerfile` |
| **Container port** | **8005** |
| Health check | `GET /health` on port **8005** |

### Published port (host)

Map host **8005** → container **8005** (e.g. `8005:8005`).

### Environment variables

```env
MOCK_CLIENT_ID=mock-client
MOCK_CLIENT_SECRET=mock-secret
MOCK_HMAC_SECRET=dev-hmac-secret-change-me-32b
MOCK_CALLBACK_SECRET=dev-callback-secret-change-me-32b
MOCK_CALLBACK_DELAY_SEC=2
MOCK_INQUIRY_DELAY_SEC=0
MOCK_VERIFY_HMAC=false
MOCK_TOKEN_TTL_SEC=3600
MOCK_CALLBACK_URL=http://<payout-hub-web-host>:8000/api/v1/callbacks/shahin/shahin-mock/
```

Replace `MOCK_CALLBACK_URL` with the internal URL of your payout-hub `web` service on the same Dokploy network.

### payout-hub gateway config (internal)

```json
"auth_url": "http://shahin-mock:8005/v0.3/obh/oauth/token",
"api_base": "http://shahin-mock:8005/"
```

If Dokploy assigns a different service hostname, use that host; keep port **8005**.

### Smoke test

```bash
curl http://<server-ip>:8005/health
curl -u mock-client:mock-secret -X POST \
  "http://<server-ip>:8005/v0.3/obh/oauth/token?grant_type=client_credentials&bank=BSI"
```

# راهنمای قدم‌به‌قدم تست (172.16.1.72)

## آدرس‌ها

| سرویس | آدرس |
|--------|------|
| payout-hub | http://172.16.1.72:8020 |
| shahin-mock | http://172.16.1.72:8005 |

---

## بخش A — نصب shahin-mock روی سرور (الزامی)

> تا وقتی `curl http://172.16.1.72:8005/health` جواب ندهد، بخش B معنی ندارد.

### قدم A1 — SSH به سرور

از PowerShell یا PuTTY:

```text
ssh user@172.16.1.72
```

(`user` = همان کاربری که payout-hub را با آن مدیریت می‌کنید)

### قدم A2 — تست روی خود سرور

```bash
curl -s http://127.0.0.1:8005/health
curl -s http://172.16.1.72:8005/health
```

اگر هر دو **خطا** دادند → mock اجرا نشده؛ ادامه A3.

### قدم A3 — دانلود و اجرا

```bash
cd /opt   # یا هر مسیر دلخواه
git clone https://github.com/mohammadian7/shahin-mock.git
cd shahin-mock
docker compose up -d --build
```

### قدم A4 — وضعیت کانتینر

```bash
docker compose ps
docker compose logs --tail=30
```

باید `shahin-mock` وضعیت **running** باشد.

### قدم A5 — دوباره تست

```bash
curl -s http://127.0.0.1:8005/health
```

انتظار:

```json
{"status":"ok","service":"shahin-mock"}
```

### قدم A6 — تست از لپ‌تاپ (Windows CMD)

```cmd
curl http://172.16.1.72:8005/health
```

اگر روی سرور OK بود ولی از Windows نه → **فایروال** پورت 8005 را باز کنید.

### قدم A7 — تست Token (یک خط در CMD)

```cmd
curl -u mock-client:mock-secret -X POST "http://172.16.1.72:8005/v0.3/obh/oauth/token?grant_type=client_credentials&bank=BSI"
```

باید `access_token` ببینید.

---

## بخش B — تنظیم payout-hub

### قدم B1 — پیدا کردن پوشه payout-hub روی سرور

```bash
# مثال
cd /path/to/payout-hub
docker compose ps
```

باید سرویس‌های `web`, `worker` را ببینید.

### قدم B2 — seed گیت‌وی mock

```bash
docker compose exec web python manage.py seed_shahin_mock --run-seed-demo
```

پیام موفق: `Gateway 'shahin-mock' is ACTIVE`

### قدم B3 — worker روشن باشد

```bash
docker compose ps
```

ستون `worker` باید **Up** باشد. اگر نیست:

```bash
docker compose up -d worker
```

### قدم B4 — تست health payout-hub (از Windows)

```cmd
curl http://172.16.1.72:8020/api/v1/health/
```

---

## بخش C — تست End-to-End

### قدم C1 — JWT

در **CMD** (یک خط):

```cmd
curl -s -X POST http://172.16.1.72:8020/api/v1/auth/token/ -H "Content-Type: application/json" -d "{\"application\":\"sale-club-wp\",\"username\":\"saleclub\",\"password\":\"changeme-dev-only-changeme\"}"
```

از پاسخ مقدار `"access":"..."` را کپی کنید → `ACCESS`

> اگر `seed_demo` نزده‌اید یا پسورد عوض شده، از ادمین Django ServiceAccount استفاده کنید.

### قدم C2 — ساخت payout

`ACCESS` و یک UUID برای idempotency بگذارید. در CMD:

```cmd
curl -s -X POST http://172.16.1.72:8020/api/v1/payouts/ -H "Content-Type: application/json" -H "Authorization: Bearer PASTE_ACCESS_HERE" -H "Idempotency-Key: 11111111-2222-3333-4444-555555555555" -d "{\"amount\":100000,\"currency\":\"IRR\",\"transfer_type\":\"PAYA\",\"purpose_code\":\"HOGHOGH\",\"gateway\":\"shahin-mock\",\"beneficiary\":{\"iban\":\"IR450660000000200570150002\",\"name\":\"Test\",\"bank\":\"DEY\"}}"
```

`id` را از JSON کپی کنید.

### قدم C3 — وضعیت (۳۰ ثانیه صبر + دوباره GET)

```cmd
curl -s http://172.16.1.72:8020/api/v1/payouts/PASTE_PAYOUT_ID/ -H "Authorization: Bearer PASTE_ACCESS_HERE"
```

انتظار نهایی: `"status":"SUCCESS"`

### قدم C4 — اگر PROCESSING ماند

```bash
# روی سرور
docker compose logs worker --tail=50
docker compose -f /opt/shahin-mock/docker-compose.yml logs --tail=30
```

---

## خطاهای رایج

| علامت | علت | کار |
|--------|-----|-----|
| connect refused :8005 | mock اجرا نشده | بخش A |
| URL rejected Bad hostname | `\` در CMD | همه curl یک خط |
| CREATED ثابت | worker خاموش | `docker compose up -d worker` |
| PROCESSING برای همیشه | callback | `MOCK_CALLBACK_URL` و لاگ mock |
| 401 Shahin | secrets | Gateway = mock-client / mock-secret |

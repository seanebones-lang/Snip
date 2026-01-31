# Permanent Demo Key Setup

Your demo API key is configured to always work (dashboard + widget) when the following env vars are set on **Railway**.

## 1. Set env vars on Railway

In Railway → Snip service → **Variables**, add:

| Variable | Value |
|----------|--------|
| `PERMANENT_API_KEY` | `snip_jwdWgGJnpJPOwCSUuDksvnFFQOrEhayYii6Zlad_Voc` |
| `PERMANENT_API_KEY_CLIENT_EMAIL` | **Your demo account email** (the one you use for Snip dashboard) |

Optional (for widget/chat bypass if that client is ever deactivated):

| Variable | Value |
|----------|--------|
| `PERMANENT_API_KEY_CLIENT_ID` | The **client UUID** for that demo account (see below) |

- **Dashboard:** With `PERMANENT_API_KEY` and `PERMANENT_API_KEY_CLIENT_EMAIL`, login with that key always resolves to that client and is treated as full access.
- **Widget/Chat:** If you also set `PERMANENT_API_KEY_CLIENT_ID`, requests for that `client_id` skip is_active/subscription checks. You can get the client_id from the dashboard (Snippet page) or by running the script below.

## 2. (Optional) Sync the key in the database

If the key was rotated or the client was deactivated, run this **once** so the key hash and active status are stored in the DB (from repo root, with Railway `DATABASE_URL`):

```bash
cd backend
DATABASE_URL="postgresql://user:pass@host:port/railway" \
  PERMANENT_API_KEY="snip_jwdWgGJnpJPOwCSUuDksvnFFQOrEhayYii6Zlad_Voc" \
  PERMANENT_API_KEY_CLIENT_EMAIL="your-demo@example.com" \
  python -m scripts.set_permanent_demo_key
```

The script prints the `client_id` to set as `PERMANENT_API_KEY_CLIENT_ID` in Railway if you want the widget bypass.

After setting the env vars (and redeploying if needed), the demo key is permanent and has full access.

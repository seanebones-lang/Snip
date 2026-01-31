# Railway & Vercel Verification Report

**Date:** 2026-01-30  
**Purpose:** Inspect production Railway backend and Vercel dashboard/widget; confirm URLs and behavior.

---

## Summary

| Target | URL | Status | Notes |
|-------|-----|--------|-------|
| **Railway backend** | https://snip-production.up.railway.app | ✅ Up | /healthz 200, /healthz/db 200, OpenAPI served |
| **Railway /healthz/ready** | https://snip-production.up.railway.app/healthz/ready | ⚠️ 404 | New endpoint not deployed yet; deploy latest code |
| **Dashboard (Vercel)** | https://snip.mothership-ai.com | ✅ Up | Landing 200, /signup 200, /login 200 |
| **Dashboard API proxy** | https://snip.mothership-ai.com/api/* | ✅ Correct | Rewrites to Railway (vercel.json); /api/* exists on backend |
| **Widget (Vercel)** | https://widget-sigma-sage.vercel.app/widget.js | ✅ Up | 200 OK |

---

## Checks performed

1. **Railway**
   - `GET /healthz` → **200** `{"status":"ok","service":"snip"}`
   - `GET /healthz/db` → **200** DB connected, migration complete, no missing columns
   - `GET /healthz/ready` → **404** (endpoint added in repo; not yet deployed)
   - `GET /openapi.json` → **200** Snip API 1.0.0

2. **Vercel – Dashboard (snip.mothership-ai.com)**
   - `/` → **200** (landing, pricing, signup links)
   - `/signup` → **200**
   - `/login` → **200**
   - `vercel.json`: `/api/(.*)` → `https://snip-production.up.railway.app/api/$1` ✅

3. **Vercel – Widget**
   - `GET https://widget-sigma-sage.vercel.app/widget.js` → **200**

---

## Action: Deploy latest code to Railway

**/healthz/ready** and the **agent-assigned fixes** (Stripe idempotency, subscription gate, Origin check, resend block, per-client rate limit, etc.) are in the repo but **not** on the live backend (404 on /healthz/ready).

1. **Railway:** Trigger a deploy from the connected GitHub repo (main branch), or push a small commit and wait for auto-deploy.
2. **Verify after deploy:**
   - `curl https://snip-production.up.railway.app/healthz/ready` → 200 with `"status":"ready"` and `checks`.
3. **Vercel:** Dashboard and widget are serving; if you set **VITE_API_URL** in Vercel to your backend URL, rebuild so the dashboard uses it (otherwise it keeps using the vercel.json rewrite to Railway, which is correct).

---

## URL reference (current)

- **Backend (Railway):** https://snip-production.up.railway.app  
- **Dashboard (Vercel):** https://snip.mothership-ai.com  
- **Widget (Vercel):** https://widget-sigma-sage.vercel.app  
- **Embed snippet API URL (white-label):** Backend uses `BACKEND_PUBLIC_URL` (default https://snip.mothership-ai.com); set on Railway if different.  
- **Dashboard API:** When `VITE_API_URL` is unset, browser calls `snip.mothership-ai.com/api/*` → Vercel rewrites to Railway `/api/*` ✅  

---

## Manual checks you can do (logged in)

- **Railway dashboard:** Confirm service is running, latest deploy from main, env vars (e.g. `DATABASE_URL`, `STRIPE_WEBHOOK_SECRET`, `XAI_API_KEY`, `RESEND_API_KEY`) set.
- **Vercel dashboard:** For the Snip dashboard project, confirm env vars (e.g. `VITE_API_URL` if you want dashboard to call backend directly), and that latest main is deployed.
- **Stripe:** Webhook endpoint `https://snip-production.up.railway.app/api/webhooks/stripe` (or your white-label backend URL) with events from STRIPE_WEBHOOK_SETUP.md.

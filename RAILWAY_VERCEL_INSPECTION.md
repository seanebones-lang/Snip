# Railway & Vercel Inspection Report

**Date:** 2026-01-31  
**Inspected via:** Live endpoints, Railway dashboard (Architecture + Deployments), Vercel dashboard (projects list).

---

## Railway (Backend)

| Check | Status | Notes |
|-------|--------|--------|
| **Service** | ✅ Online | Snip at `snip-production.up.railway.app`, 1 replica, us-west2 |
| **Postgres** | ✅ Online | Postgres + postgres-volume linked |
| **`/healthz/db`** | ✅ 200 | DB connected, migration complete, `client_configs` table present |
| **`/healthz`** | ⏳ Timeout | Request timed out (endpoint exists in code; may be slow or load-related) |
| **`/healthz/ready`** | ❌ 404 | **Not yet deployed.** Endpoint exists in repo (`main`) but current *active* deployment is older |

### Deployments (at inspection time)

- **Active:** `fix(docs): documentstatus enum + ChromaDB config so uploads complete` (22 min ago) — older commit.
- **Building:**  
  - `fix: Usage page apiUrl + Stripe invoice subscription expanded object` (8 min ago)  
  - `fix: close all system gaps + recommendations...` (9 min ago)  

The **latest code** (with `/healthz/ready`, Stripe lifecycle, allowlist, rate limits, resend-api-key, etc.) was **building** and had not yet become the active deployment. Once the build that includes `healthz_ready` completes and becomes active, `/healthz/ready` will return 200.

### What to do

1. **Wait for the in-progress Railway build to finish** (or trigger a new deploy from `main` if builds failed).
2. **Re-check:**  
   `curl https://snip-production.up.railway.app/healthz/ready`  
   Expect: `200` and JSON with `status: "ready"` and `checks` (database, xai_configured, resend_configured, stripe_configured).
3. **Stripe webhook:** Ensure `STRIPE_WEBHOOK_SECRET` is set in Railway and the webhook sends `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed` to `https://snip-production.up.railway.app/api/webhooks/stripe`.

---

## Vercel (Dashboard & Widget)

| Check | Status | Notes |
|-------|--------|--------|
| **Dashboard** | ✅ Live | `snip.mothership-ai.com` — landing and login load |
| **Widget** | ✅ Live | `widget-sigma-sage.vercel.app` |
| **Dashboard latest deploy** | ⚠️ Older | Vercel showed latest: `fix(docs): documentstatus enum...` (22m ago). Newer commits (apiUrl, VITE_API_URL, Forgot API key) may not be on dashboard yet. |
| **Widget latest deploy** | ✅ Newer | `fix: Usage page apiUrl + Stripe invoice...` (8m ago) |
| **API proxy** | ✅ Correct | `vercel.json` rewrites `/api/(.*)` → `https://snip-production.up.railway.app/api/$1` |
| **Dashboard `api.ts`** | ✅ In repo | Uses `VITE_API_URL` or same-origin; `apiUrl()` used for fetch in code |

### What to do

1. **Dashboard:** If the dashboard project is not set to auto-deploy from `main`, trigger a **Redeploy** from the Vercel dashboard so it gets the latest commit (apiUrl, Login “Forgot API key?”, etc.).
2. **Env:** In Vercel **dashboard** project, set **`VITE_API_URL`** to:
   - `https://snip.mothership-ai.com` (recommended: same-origin, then rewrite sends `/api/*` to Railway), or  
   - `https://snip-production.up.railway.app` (direct to backend).  
   Leave empty only if you rely on same-origin + rewrite.
3. **Widget:** No change needed; already on a recent deploy.

---

## Summary

| Component | Status | Action |
|-----------|--------|--------|
| Railway backend | Online; new code building | Wait for build to complete, then verify `/healthz/ready` |
| Railway DB | OK | None |
| Vercel dashboard | Live; may be on older commit | Redeploy from `main` if needed; set `VITE_API_URL` |
| Vercel widget | Live, newer deploy | None |
| API proxy (Vercel → Railway) | Correct | None |

Once Railway’s new deployment is active and the dashboard is redeployed (if needed), everything should be aligned with the repo and the “system gaps” fixes (Stripe lifecycle, allowlist, rate limits, readiness check, etc.) will be live.

# Recommendations Executed

**Date:** 2026-01-30  
**Purpose:** Record of orchestrated recommendations applied after the system gaps fix.

---

## 1. Stripe webhook documentation

- **Created:** `STRIPE_WEBHOOK_SETUP.md` (repo root)
- **Contents:**
  - Endpoint URL: `POST /api/webhooks/stripe`
  - Required events table: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
  - Steps to add endpoint in Stripe Dashboard and set `STRIPE_WEBHOOK_SECRET`
  - Local testing with Stripe CLI
  - Optional events and troubleshooting

---

## 2. Backend env example

- **Updated:** `backend/env.example.txt`
- **Added:**
  - Stripe: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, price IDs, success/cancel URLs
  - Resend: `RESEND_API_KEY`
  - White-label: `BACKEND_PUBLIC_URL`
  - Comment pointing to `STRIPE_WEBHOOK_SETUP.md`

---

## 3. Dashboard env example

- **Created:** `dashboard/.env.example`
- **Contents:**
  - `VITE_API_URL` with note: empty for local (proxy), set in production to backend URL

---

## 4. Dashboard README and deployment notes

- **Updated:** `dashboard/README.md`
- **Contents:**
  - Environment variables table (VITE_API_URL)
  - Local development (npm run dev, proxy)
  - Deployment on Vercel: set VITE_API_URL, note on vercel.json rewrite
  - Pointer to STRIPE_WEBHOOK_SETUP.md (webhooks are backend-only)

---

## 5. Main README deployment section

- **Updated:** `README.md`
- **Added:**
  - Stripe webhooks subsection: endpoint URL, required events, STRIPE_WEBHOOK_SECRET
  - Dashboard subsection: set VITE_API_URL, link to dashboard/README.md
  - Backend env pointer to backend/env.example.txt

---

## 6. Backend tests

- **Updated:** `backend/tests/test_api.py`
- **Added:** `test_healthz_ready()` – GET /healthz/ready returns 200, `status == "ready"`, `checks.database == "ok"`

**Run tests:** From repo root, activate backend venv and run:
```bash
cd backend && pip install -r requirements.txt && python -m pytest tests/test_api.py -v
```

---

## Summary

| Item | Action |
|------|--------|
| Stripe webhook events | Documented in STRIPE_WEBHOOK_SETUP.md |
| Backend env | backend/env.example.txt updated with Stripe, Resend, white-label |
| Dashboard env | dashboard/.env.example created with VITE_API_URL |
| Dashboard README | Env vars, deployment, webhook pointer |
| Main README | Deployment section: webhooks + VITE_API_URL |
| Backend tests | test_healthz_ready added |

All recommendations are applied in the repo. Manual steps for you: configure the Stripe webhook in the Dashboard (add endpoint + events, copy secret), set env vars in Railway/Vercel, and run tests in your backend venv.

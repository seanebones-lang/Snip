# Snip System Gaps

**Date:** 2026-01-30  
**Purpose:** Gaps identified after reviewing docs and code (backend, dashboard, widget, Stripe, RAG, TTS).

---

## 1. Stripe subscription lifecycle (high)

**Gap:** Webhook only handles `checkout.session.completed`. No handling for:

- `customer.subscription.updated` (plan change, renewal)
- `customer.subscription.deleted` (cancel)
- `invoice.payment_failed`

**Impact:** If a customer cancels or payment fails, the backend still shows them as active. They keep full access until you manually fix it.

**Fix:** In `backend/app/stripe_routes.py`, add handlers for:

- `customer.subscription.deleted` → set `stripe_subscription_status = 'canceled'` and optionally `is_active = False` or downgrade tier
- `customer.subscription.updated` → sync tier/status from Stripe
- `invoice.payment_failed` → optionally set status to `past_due` and/or notify

---

## 2. Domain allowlist not enforced on chat (medium)

**Gap:** `allowed_domains` is checked only on **widget config** (`GET /api/widget/config/{client_id}`). The **chat** endpoint (`POST /api/chat`) does not check `Origin` against `allowed_domains`.

**Impact:** If a client sets `allowed_domains`, anyone with the `client_id` can still call `/api/chat` from any origin (e.g. script on another site) and get responses.

**Fix:** In `backend/app/main.py` in the `chat()` handler, after loading client/config, add the same origin check used in widget config:

- Read `Origin` (or `Referer`) from `req`
- If `config.allowed_domains` is non-empty and origin is present, require origin to match one of the allowed domains; otherwise return 403.

---

## 3. API key email failure is silent (medium)

**Gap:** `send_api_key_email()` in `backend/app/email.py` catches exceptions and only `print()`s. No retry, no alert, no DB flag. Webhook still returns `{"status": "success"}` even when email fails.

**Impact:** Customer can pay, account is created, but they never get the API key email (e.g. Resend misconfigured or down). They have no way to know except “check spam / contact support.”

**Fix:**

- Log email failures (e.g. structured log or error reporting).
- Optionally: set a flag on the client (e.g. `api_key_email_sent: false`) and have a cron or admin endpoint to retry.
- Optionally: return a different webhook status when email fails so you can alert or retry (e.g. queue a retry job).

---

## 4. No API key recovery flow (medium)

**Gap:** API key is shown once (create + Stripe webhook). Docs say “contact support” if lost. There is no self-service “resend API key” or “forgot API key” (e.g. by email).

**Impact:** Friction for users who lose the key; support burden.

**Fix (optional):**

- “Forgot API key” on login: enter email → if match, generate new key, hash it, send email (same as `send_api_key_email`), invalidate old key. Require rate limit and/or verification (e.g. magic link to email) to avoid abuse.
- Or keep “contact support” but document it clearly and optionally add an admin endpoint to rotate and email a new key.

---

## 5. Documentation / UI inconsistencies (low)

- **API key prefix:** Code uses `snip_` (`backend/app/auth.py`). KEY_ISSUANCE_GUIDE.md and Login placeholder use `ne11_`. New keys will never look like `ne11_`.
- **CORS doc:** CORS_FIX_APPLIED.md says `allow_credentials=True`; code uses `allow_credentials=False` (with a comment that `*` + credentials is not allowed). Doc is wrong.

**Fix:** Update KEY_ISSUANCE_GUIDE.md and Login placeholder to `snip_...`. Update CORS_FIX_APPLIED.md to state `allow_credentials=False` and why.

---

## 6. No rate limiting (low–medium)

**Gap:** No per-client or global rate limiting on `/api/chat`, `/api/clients`, or other expensive endpoints.

**Impact:** Abuse (spam, cost) or accidental overload.

**Fix:** Add rate limiting (e.g. by API key for dashboard, by client_id for chat) with something like slowapi or a reverse-proxy limit. Prefer per-client limits for chat to protect xAI cost.

---

## 7. ChromaDB persistence on Railway (low)

**Gap:** DOCUMENT_PROCESSING_RAILWAY.md notes ChromaDB uses ephemeral disk on Railway; embeddings can be lost on redeploy. No volume or external-store guidance in code or deploy docs.

**Impact:** After a deploy, RAG may be empty until clients re-upload documents.

**Fix:** Document attaching a Railway volume (or external store) to `CHROMA_PERSIST_DIRECTORY`, or explicitly document “re-upload after deploy” as the supported behavior.

---

## 8. Health checks don’t cover external deps (low)

**Gap:** `/healthz` is app-only. `/healthz/db` checks DB. No check for xAI, Resend, or Stripe (e.g. connectivity or config presence).

**Impact:** App can report “healthy” while xAI or Resend is down; harder to debug.

**Fix (optional):** Add a “deep” health or readiness endpoint (e.g. `/healthz/ready`) that optionally checks xAI (e.g. minimal call or token validation), Resend config, and DB, and document it for k8s/Railway readiness.

---

## 9. Dashboard API base URL (low) — FIXED

**Gap:** `dashboard/vercel.json` rewrites `/api/*` to a hardcoded URL; no env-based backend URL for white-label or multi-env.

**Fix applied:** Dashboard now uses `VITE_API_URL` (see `dashboard/src/api.ts`). All fetch calls use `apiUrl('/api/...')`. Set `VITE_API_URL` at Vercel build time (e.g. `https://snip.mothership-ai.com`) to point at your backend; if unset, same-origin is used (vercel rewrite still applies for legacy builds).

---

## Summary

| Priority | Gap | Area |
|----------|-----|------|
| High | Stripe subscription cancel/update not handled | Billing / access |
| Medium | allowed_domains not enforced on /api/chat | Security |
| Medium | Email failure silent; no retry/alert | Onboarding |
| Medium | No self-service API key recovery | UX / support |
| Low | Doc/UI: ne11_ vs snip_, CORS doc wrong | Docs / UI |
| Low–Medium | No rate limiting | Abuse / cost |
| Low | ChromaDB persistence not documented for prod | RAG / ops |
| Low | Health doesn’t check external deps | Ops |
| Low | Dashboard backend URL hardcoded in vercel.json | Deploy / white-label |

Recommended order: (1) Stripe lifecycle, (2) chat allowed_domains, (3) email failure handling and doc/UI fixes, then the rest as needed.

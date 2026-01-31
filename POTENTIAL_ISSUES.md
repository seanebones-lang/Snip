# Potential Issues (from full system review)

**Date:** 2026-01-30  
**Scope:** Backend, dashboard, widget, Stripe, RAG, TTS, docs. Not necessarily bugs—things to be aware of or consider.

**Update:** Agent-assigned fixes have been implemented. See **AGENT_ASSIGNMENTS.md** for agent-to-issue mapping and implementation status.

---

## 1. Canceled / past_due clients still have access (design choice)

**What:** When Stripe sends `customer.subscription.deleted` or `invoice.payment_failed`, we only set `stripe_subscription_status` to `"canceled"` or `"past_due"`. We never set `is_active = False`. Chat, widget config, and dashboard (with valid API key) still work.

**Impact:** Canceled or past-due customers can keep using the widget and dashboard until you manually deactivate them or add gating.

**Options:**  
- **Keep as-is** if you want a grace period or manual cutoff.  
- **Gate access:** In `subscription.deleted` set `is_active = False`, and/or in chat/widget/config only allow when `stripe_subscription_status in ("active", "trialing")` (and optionally `"past_due"` for grace).

---

## 2. Allowed_domains when Origin is missing

**What:** Domain allowlist is enforced only when both `config.allowed_domains` and `origin` (or `referer`) are present. If the request has no Origin/Referer (e.g. server-side script, curl, some clients), the request is allowed.

**Impact:** Domain lock can be bypassed by not sending Origin. Most browser traffic sends Origin, so risk is limited.

**Options:** If you need strict server-side locking, require Origin and reject when missing and allowlist is non-empty; document that browser/widget must send Origin.

---

## 3. Resend API key for inactive clients

**What:** `POST /api/resend-api-key` does not check `is_active`. A canceled (or otherwise inactive) client can still request a new key and log in.

**Impact:** Canceled users can regain dashboard access. May be intentional (win-back) or undesirable.

**Options:** If you want to block: after finding the client by email, reject with a generic message when `not client.is_active`.

---

## 4. Stripe webhook idempotency

**What:** We do not track processed Stripe event IDs. If Stripe retries the same event (e.g. `checkout.session.completed`), we may create/update the client again and send the API key email again.

**Impact:** Duplicate emails or duplicate processing on retries. Usually acceptable; can be confusing if a customer gets two “your API key” emails.

**Options:** Store processed event IDs (e.g. in a table or cache) and return 200 without side effects when the event was already handled.

---

## 5. Large document upload in-request

**What:** Document processing runs fully in-request (read file → process → ChromaDB). A 500MB upload is read into memory and processed in one request.

**Impact:** Very large uploads can cause long request duration, timeouts (e.g. Railway), or high memory use.

**Options:** Cap upload size lower for in-request processing; or move to a queue + worker for files above a threshold and keep in-request for smaller files.

---

## 6. Rate limit by IP only

**What:** Slowapi uses `get_remote_address` by default. Rate limits are per IP. Behind a shared proxy (e.g. Vercel, Cloudflare), many users can share one IP.

**Impact:** One abusive client could consume the limit for others on the same IP; or one IP could be overly restricted. Chat is limited per IP (120/min), not per client_id.

**Options:** For cost protection, consider an additional limit keyed by `client_id` for `/api/chat` (e.g. in-memory or Redis). Keep IP limit for unauthenticated endpoints.

---

## 7. Dashboard API key in localStorage

**What:** The dashboard stores the API key in `localStorage` for persistence. Any XSS on the dashboard origin could read it.

**Impact:** Standard risk for client-side secret storage. Key is high-value (full account access).

**Options:** Use short-lived tokens + refresh, or accept the risk and harden with CSP, no untrusted script, and secure dashboard hosting.

---

## 8. ChromaDB ephemeral on Railway

**What:** Without a Railway volume, ChromaDB data is lost on redeploy. Documents must be re-uploaded after each deploy.

**Impact:** Documented in DOCUMENT_PROCESSING_RAILWAY.md; operational constraint, not a code bug.

**Options:** Attach a volume to `CHROMA_PERSIST_DIRECTORY` for persistence, or keep re-upload as the supported behavior.

---

## Summary

| # | Area              | Severity   | Action |
|---|-------------------|------------|--------|
| 1 | Canceled access   | Design     | Decide: keep grace or gate on status/is_active |
| 2 | Origin missing    | Low        | Optional: reject when allowlist set and no Origin |
| 3 | Resend key inactive | Low      | Optional: block when not is_active |
| 4 | Stripe idempotency | Low      | Optional: store event IDs and skip duplicates |
| 5 | Large uploads     | Medium     | Consider size cap or queue for very large files |
| 6 | Rate limit key    | Low        | Optional: per-client_id limit for /api/chat |
| 7 | localStorage key  | Standard   | Harden with CSP; accept or move to tokens |
| 8 | ChromaDB ephemeral| Doc only   | Volume or re-upload; already documented |

None of these are critical bugs; the system is consistent and deployable. Addressing 1 and 5 (if you have very large uploads) gives the most benefit; the rest are optional hardening.

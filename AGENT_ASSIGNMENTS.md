# Agent Assignments – POTENTIAL_ISSUES.md

**Date:** 2026-01-30  
**Source:** Orchestration plan (swarm/orchestrate) to address all 8 potential issues.

---

## Assignment matrix

| Issue | Description | Assigned agent | Phase |
|-------|-------------|----------------|-------|
| 1 | Canceled/past_due clients still have access | **Security** | 1 |
| 2 | Allowed_domains when Origin missing | **Security** | 1 |
| 3 | Resend API key for inactive clients | **Security** | 1 |
| 4 | Stripe webhook idempotency | **Backend** | 1 |
| 5 | Large document upload in-request | **Performance** | 1 |
| 6 | Rate limit by client_id for /api/chat | **Security** | 1 |
| 7 | Dashboard API key in localStorage | **Frontend** | 1 |
| 8 | ChromaDB ephemeral | **Documentation** | 1 |

---

## Execution order

- **Phase 1 (parallel):** Security (1,2,3,6), Backend (4), Performance (5), Frontend (7), Documentation (8).
- **Phase 2:** Testing – verify all fixes.
- **Phase 3:** Code review.
- **Phase 4:** Master Engineer – production readiness.

---

## Scope per agent

- **Security:** Gate chat/widget/config on `stripe_subscription_status` and `is_active`; reject when allowlist set and no Origin; block resend-api-key when not `is_active`; add per-client_id rate limit for `/api/chat`.
- **Backend:** Store processed Stripe event IDs (DB or cache), skip duplicate events in webhook.
- **Performance:** Cap in-request document size (e.g. 100MB) or document current 500MB risk; optional queue for larger files.
- **Frontend:** Document CSP and API key storage risk; optional hardening (e.g. proxy, HttpOnly).
- **Documentation:** Confirm ChromaDB ephemeral note in docs (already in DOCUMENT_PROCESSING_RAILWAY.md).

---

## Implementation stack

Snip is **FastAPI (Python)** backend, **React (Vite)** dashboard, **Stripe** webhooks in `backend/app/stripe_routes.py`. All fixes must be implemented in this stack (not Node/Express). Implementations are applied in-repo per the plan above.

---

## Implementation status (done)

| Issue | Agent | Implemented |
|-------|--------|-------------|
| 1 | Security | Chat + widget config gate on `is_active` and `stripe_subscription_status`; `subscription.deleted` sets `is_active = False` |
| 2 | Security | Reject when `allowed_domains` set and no Origin (chat + widget config) |
| 3 | Security | Resend-api-key returns generic message when `not client.is_active` (no key sent) |
| 4 | Backend | `ProcessedStripeEvent` table; webhook inserts event id before processing; duplicate returns 200 |
| 5 | Performance | Comment in main.py re large upload timeout risk; doc in dashboard README |
| 6 | Security | Per-client_id in-memory rate limit (120/min) in chat handler |
| 7 | Frontend | Dashboard README: Security section (API key localStorage, CSP, hardening) |
| 8 | Documentation | ChromaDB already in DOCUMENT_PROCESSING_RAILWAY.md and POTENTIAL_ISSUES.md |

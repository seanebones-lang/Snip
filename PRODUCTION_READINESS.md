# Production Readiness Checklist

**Date:** 2026-01-31  
**Goal:** Provide a single, repeatable checklist for launch and validation.

---

## Production URLs

- **Dashboard:** https://snip.mothership-ai.com
- **Public landing:** https://snip.mothership-ai.com/
- **Signup:** https://snip.mothership-ai.com/signup
- **Success:** https://snip.mothership-ai.com/success
- **Widget (primary):** https://widget-sigma-sage.vercel.app
- **Backend:** https://snip-production.up.railway.app

## Critical Endpoints

- `POST /api/checkout` (Stripe checkout session creation)
- `POST /api/webhooks/stripe` (Stripe webhook receiver)
- `GET /healthz` (backend health)

---

## Stripe Verification Steps

1. Open `/signup`, select a tier, and proceed to checkout.
2. **Test mode:** Use Visa `4242 4242 4242 4242`, any future date, any 3-digit CVC.
3. **Live mode:** Use a real card and verify success redirect.
4. Confirm webhook received and API key email delivered.
5. Log in with the API key and confirm access.

> Note: The Stripe test card only works in test mode.

---

## Voice Verification Steps

1. Call `POST /api/chat` and confirm `audio_url` is present.
2. Load the widget and confirm audio playback uses backend audio by default.
3. Optional fallback: set `data-allow-browser-tts="true"` only if explicitly desired.

---

## End-to-End Customer Flow

1. Signup → Pay → Success page.
2. Receive API key email.
3. Login with API key.
4. Configure branding + voice.
5. Copy snippet and embed on a test page.
6. Send a message and verify voice playback.

---

## Last Verified

- Backend health: ✅ `/healthz` returns `{ "status": "ok", "service": "snip" }`
- Voice delivery: ✅ `/api/chat` returns `audio_url` (data URL)
- Deployments: ✅ Vercel + Railway tracking `main`

---

## Monitoring Checks

- **Railway logs:** watch for webhook or TTS errors.
- **Resend:** verify email deliverability for key emails.


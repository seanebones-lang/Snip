# Snip Dashboard

React dashboard for Snip customers: login with API key, configure branding, get embed snippet, manage documents and FAQs.

---

## Environment variables

Copy `.env.example` to `.env.local` and set:

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL (no trailing slash). **Local:** leave empty (Vite proxies `/api` to `localhost:8000`). **Production:** set in Vercel to your backend (e.g. `https://snip.mothership-ai.com`) so all API calls go there. |

---

## Local development

```bash
npm install
npm run dev
```

Runs at http://localhost:3000. API requests to `/api/*` are proxied to http://localhost:8000 (see `vite.config.ts`).

---

## Deployment (Vercel)

1. Connect the repo to Vercel and set the root to `dashboard` (or build command/output dir).
2. **Environment variables:** Set `VITE_API_URL` to your backend URL (e.g. `https://snip.mothership-ai.com`). This is baked in at build time; all fetch calls use this base.
3. If `VITE_API_URL` is not set, the app still works if you use the `vercel.json` rewrite that forwards `/api/*` to your backend (e.g. Railway). Prefer setting `VITE_API_URL` for clarity and white-label.

---

## Security (API key storage, Issue 7)

The dashboard stores the API key in **localStorage** for persistence. If the dashboard origin is compromised (e.g. XSS), the key could be read. **Recommendations:**

- **CSP:** Set a strict Content-Security-Policy header when serving the dashboard (e.g. in Vercel headers or your reverse proxy): `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';` (tune as needed so the app still works).
- **Hardening:** Do not load untrusted scripts on the dashboard domain. Prefer hosting the dashboard on a dedicated subdomain with minimal third-party scripts.
- **Future:** Consider short-lived tokens + refresh, or proxying API calls through a backend so the key is never stored in the browser.

---

## Webhook setup

Stripe webhooks are configured on the **backend**, not the dashboard. See repo root doc **STRIPE_WEBHOOK_SETUP.md** for required events and endpoint URL.

# Stripe Webhook Setup (Snip)

Configure Stripe webhooks so the backend stays in sync with subscriptions and payments.

---

## Endpoint

| Item | Value |
|------|--------|
| **URL** | `https://YOUR_BACKEND_URL/api/webhooks/stripe` |
| **Method** | POST |
| **Example (Railway)** | `https://snip-production.up.railway.app/api/webhooks/stripe` |
| **Example (white-label)** | `https://snip.mothership-ai.com/api/webhooks/stripe` |

---

## Required webhook events

Enable these in Stripe Dashboard → Developers → Webhooks → Add endpoint → Select events:

| Event | Description | Backend action |
|-------|-------------|----------------|
| `checkout.session.completed` | New subscription after payment | Create/update client, send API key email |
| `customer.subscription.updated` | Plan change, renewal, status change | Sync `stripe_subscription_status` and tier from Stripe |
| `customer.subscription.deleted` | Subscription canceled | Set `stripe_subscription_status = 'canceled'` |
| `invoice.payment_failed` | Payment failed (e.g. card declined) | Set `stripe_subscription_status = 'past_due'` |

---

## Steps

1. **Stripe Dashboard**
   - Go to [Developers → Webhooks](https://dashboard.stripe.com/webhooks) → **Add endpoint**.
   - **Endpoint URL:** Your backend base URL + `/api/webhooks/stripe` (see table above).
   - **Events to send:** Click “Select events” and add the four events in the table.
   - Create the endpoint and copy the **Signing secret** (starts with `whsec_`).

2. **Backend env**
   - Set `STRIPE_WEBHOOK_SECRET` to that signing secret (e.g. in Railway env vars).
   - Redeploy the backend so it uses the new secret.

3. **Verify**
   - Stripe Dashboard shows recent webhook attempts and responses.
   - After a test payment/cancel, check backend logs for `[Stripe]` or webhook handling.

---

## Local testing (Stripe CLI)

```bash
# Install Stripe CLI, then:
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe
# Use the printed webhook signing secret (whsec_...) as STRIPE_WEBHOOK_SECRET in .env
```

Trigger test events:

```bash
stripe trigger checkout.session.completed
stripe trigger customer.subscription.deleted
stripe trigger invoice.payment_failed
```

---

## Optional events

You can also enable (not required for Snip):

- `invoice.payment_succeeded` – e.g. for usage/billing logs
- `customer.subscription.created` – if you want to react to new subscriptions separately

Keep only the events you need to avoid unnecessary load.

---

## Troubleshooting

- **400 / Signature verification failed:** `STRIPE_WEBHOOK_SECRET` does not match the endpoint’s signing secret. For local, use the secret from `stripe listen`.
- **404:** Backend URL is wrong or the route is not deployed (must be `POST /api/webhooks/stripe`).
- **Account created but no email:** Check `email_failed` in webhook response and backend logs; configure `RESEND_API_KEY` and “From” domain in Resend.

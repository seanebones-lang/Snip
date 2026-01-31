# Snip by NextEleven - API Key Issuance Guide

## Overview
Customers pay via Stripe first, then receive their API key automatically via email. They log in at **https://snip.mothership-ai.com** using the key.

**Tiers:** Basic ($25/mo), Standard ($40/mo), Premium ($60/mo)

## Primary Flow: Stripe Auto-Issuance (Recommended)
1. Customer visits **https://snip.mothership-ai.com/signup**
2. Selects tier, enters email/company name
3. Redirected to Stripe Checkout
4. **Webhook auto-creates Client + sends API key via email**
5. Customer receives email → logs in at dashboard

## Manual Issuance (Admin/Internal)
### Method 1: curl
```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "company_name": "Acme Corp",
    "tier": "standard"
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "customer@example.com",
  "company_name": "Acme Corp",
  "tier": "standard",
  "api_key": "snip_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

### Method 2: Python Script
```python
import requests

response = requests.post("https://snip-production.up.railway.app/api/clients", json={
    "email": "customer@example.com",
    "company_name": "Acme Corp", 
    "tier": "enterprise"
})
print(response.json())
```

### Method 3: Postman
1. POST `https://snip-production.up.railway.app/api/clients`
2. Headers: `Content-Type: application/json`
3. Body (JSON): `{email, company_name, tier}`

## Security Notes
- **Client ID** (`id`): Public, used in widget embed code
- **API Key** (`api_key`): Secret, used for dashboard login only. **Shown once**
- Email keys securely; resend via webhook if lost

## Customer Instructions
```
Your Snip by NextEleven account is ready!

1. Go to https://snip.mothership-ai.com
2. Enter your API key: snip_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
3. Customize branding → Get embed code → Paste on site → Test!

Support: support@mothership-ai.com
```

## Troubleshooting
- **Duplicate email:** Returns 400 error
- **No API key returned:** Check Stripe webhook; contact support
- **Customer can't login:** Verify key format (snip_xxx), check spam folder

**Last Updated:** Jan 30, 2026
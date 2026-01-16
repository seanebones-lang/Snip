# How to Get Your API Key - Quick Guide

## Current Status

The dashboard requires an API key to log in. Here's how to get one:

---

## Option 1: Create via API (Recommended)

### Step 1: Create a Client Account

Run this command (replace with your email and company name):

```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "company_name": "Your Company Name"
  }'
```

### Step 2: Save the Response

You'll receive a JSON response with:
- **Client ID**: Your unique identifier
- **API Key**: Your secret key (save this immediately - only shown once!)

**Example Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "your-email@example.com",
  "company_name": "Your Company Name",
  "api_key": "snip_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tier": "basic",
  "created_at": "2026-01-16T20:00:00Z"
}
```

### Step 3: Use API Key in Dashboard

1. Copy the `api_key` value from the response
2. Go to your dashboard login page
3. Paste the API key
4. Click "Access Dashboard"

---

## Option 2: Contact Support

If the API isn't working or you prefer assistance:

1. **Email support** with:
   - Your email address
   - Your company name
   - Request: "Please create a client account and send my API key"

2. Support will:
   - Create your account manually
   - Send you your Client ID and API Key via email

---

## Troubleshooting

### If API Returns "Internal Server Error"

This means the database might not be properly configured. 

**Solutions:**
1. **Contact support** - They can create your account manually
2. **Check Railway logs** - Database connection might need fixing
3. **Wait and retry** - Sometimes the database needs a moment to initialize

### If API Returns "Email Already Registered"

This means an account already exists for that email.

**Solutions:**
1. **Contact support** to retrieve your existing API key
2. **Try a different email** address
3. **Check your email** - You may have received credentials already

---

## What You Need to Know

### API Key Security

- ✅ **Safe to save** in password manager or secure note
- ✅ **Used for** managing widget settings via API
- ❌ **Never put** in your website's HTML code
- ❌ **Never share** publicly

### Client ID vs API Key

**Client ID:**
- Public identifier
- Used in widget embed code
- Safe to put on website

**API Key:**
- Secret key for authentication
- Only for API calls (server-side)
- Never expose in website code

---

## Quick Test: Check if API Key Works

After receiving your API Key, test it:

```bash
curl https://snip-production.up.railway.app/api/clients/me \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Expected Response:**
- `200 OK` with your client information = ✅ API Key works
- `401 Unauthorized` = ❌ API Key is invalid

---

## After Getting Your API Key

1. **Save it securely** (password manager, encrypted note)
2. **Log into dashboard** using the API key
3. **View pricing plans** on the dashboard
4. **Customize your widget** via the dashboard or API

---

## Still Need Help?

**Contact Support:**
- Include your email address
- Mention you need an API key to access the dashboard
- They'll create your account and send credentials

---

**Note**: The API may return errors if the database isn't fully set up. If you get errors, contact support for manual account creation.

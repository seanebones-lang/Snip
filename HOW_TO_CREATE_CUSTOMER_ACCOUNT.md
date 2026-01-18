# 📝 How to Create a Customer Account - Step by Step

## Where to Do It

**You create customer accounts using the API endpoint.**

You can do this from:
- Terminal/Command Line (Mac/Linux)
- Windows Command Prompt or PowerShell
- Postman (API testing tool)
- Any HTTP client

---

## Step-by-Step Instructions

### Option 1: Using Terminal (Mac/Linux/Terminal)

1. **Open Terminal** (or Command Prompt on Windows)

2. **Run this command** (replace with customer info):

```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "company_name": "Customer Company Name",
    "tier": "premium"
  }'
```

3. **You'll get back a response** like this:

```json
{
  "id": "abc123-def456-ghi789",
  "email": "customer@example.com",
  "company_name": "Customer Company Name",
  "api_key": "snip_xxxxxxxxxxxxxxxxxxxxx",
  "tier": "premium",
  "created_at": "2026-01-17T10:00:00Z"
}
```

4. **Save these two things:**
   - **Client ID**: `abc123-def456-ghi789` (give to customer for embed code)
   - **API Key**: `snip_xxxxxxxxxxxxxxxxxxxxx` (give to customer to access dashboard)

---

### Option 2: Using Postman (Easier if you prefer GUI)

1. **Download Postman** (if you don't have it): https://www.postman.com/downloads/

2. **Create a new request:**
   - Method: `POST`
   - URL: `https://snip-production.up.railway.app/api/clients`

3. **Add Headers:**
   - Key: `Content-Type`
   - Value: `application/json`

4. **Add Body (raw JSON):**
   ```json
   {
     "email": "customer@example.com",
     "company_name": "Customer Company Name",
     "tier": "premium"
   }
   ```

5. **Click Send**

6. **You'll get the response** with Client ID and API Key

---

### Option 3: Using Python (If you have Python installed)

```python
import requests

response = requests.post(
    'https://snip-production.up.railway.app/api/clients',
    json={
        'email': 'customer@example.com',
        'company_name': 'Customer Company Name',
        'tier': 'premium'
    }
)

data = response.json()
print(f"Client ID: {data['id']}")
print(f"API Key: {data['api_key']}")
```

---

## What You Need Before Creating Account

1. **Customer's email address**
2. **Customer's company name**
3. **Tier choice**: `basic` or `premium`

---

## Example: Creating Account for Real Customer

Let's say you have a customer:
- Email: `john@acmecorp.com`
- Company: `Acme Corporation`
- Tier: `premium`

**You run this:**

```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acmecorp.com",
    "company_name": "Acme Corporation",
    "tier": "premium"
  }'
```

**You get back:**

```json
{
  "id": "9d57eadc-f253-4801-a1f2-f6c45df6b615",
  "email": "john@acmecorp.com",
  "company_name": "Acme Corporation",
  "api_key": "snip_jWXHOqb3Recjl59s4pvygSM9b...",
  "tier": "premium",
  "created_at": "2026-01-17T10:00:00Z"
}
```

**You email them:**

```
Hi John!

Your account is ready.

Go to: https://snip.mothership-ai.com
Enter this API key: snip_jWXHOqb3Recjl59s4pvygSM9b...

Then customize your chatbot and get your embed code.

Thanks!
```

---

## Where This Happens

**You do this on YOUR computer/terminal:**

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Run the `curl` command above
3. Get the Client ID and API Key
4. Send API Key to customer via email

**Customer does this on THEIR browser:**

1. Goes to https://snip.mothership-ai.com
2. Enters the API Key you sent them
3. Sees their dashboard
4. Customizes and gets embed code

---

## Quick Reference

**API Endpoint:** `POST https://snip-production.up.railway.app/api/clients`

**Required Fields:**
- `email`: Customer's email
- `company_name`: Their company name
- `tier`: `"basic"` or `"premium"`

**You Get Back:**
- `id`: Client ID (for embed code)
- `api_key`: API Key (for dashboard access)

---

## That's It!

**You don't need any special software** - just Terminal and the curl command.

**No login required** - the `/api/clients` endpoint is public (anyone can create accounts).

**That's where you create accounts** - via that API endpoint! 🚀

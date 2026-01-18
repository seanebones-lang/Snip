# ✅ Fixed Command - How to Create Customer Account

## The Correct Command

**Your command had a quote error.** Here's the fixed version:

### ❌ Wrong (What you tried):
```bash
'{"email":"seanebones@gmail.com,"company_name":"Customer Company","tier":"premium"}'
```
*(Missing quote after email, comma outside quotes)*

### ✅ Correct (Fixed):
```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"seanebones@gmail.com","company_name":"Customer Company","tier":"premium"}'
```

---

## Step-by-Step (Copy This)

**1. Open Terminal**

**2. Copy this ENTIRE command** (all one line):

```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"customer@example.com","company_name":"Customer Company","tier":"premium"}'
```

**3. Replace `customer@example.com` with their email**  
**4. Replace `Customer Company` with their company name**

**5. Paste in Terminal and press Enter**

---

## What You'll See

### If Account Created Successfully:
```json
{
  "id": "abc123-def456-ghi789",
  "email": "customer@example.com",
  "company_name": "Customer Company",
  "api_key": "snip_xxxxxxxxxxxxxxxxxxxxx",
  "tier": "premium",
  "created_at": "2026-01-17T10:00:00Z"
}
```

**Copy the `api_key` and email it to customer.**

### If Email Already Exists:
```json
{"detail": "Email already registered"}
```

**This means:** Account already exists for that email.

**Solutions:**
1. Use a different email
2. Contact support to retrieve existing API key
3. Create account with customer's email (new account)

---

## Quick Test Example

**Create a test account:**

```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"test@example.com","company_name":"Test Company","tier":"premium"}'
```

**If it works:** You'll see JSON with `id` and `api_key` ✅

**If it fails:** You'll see error message ❌

---

## Common Mistakes

### Mistake 1: Quote Errors
❌ Wrong: `"email":"test@gmail.com,"company_name"`  
✅ Right: `"email":"test@gmail.com","company_name"`

### Mistake 2: Missing Quotes
❌ Wrong: `email:test@gmail.com`  
✅ Right: `"email":"test@gmail.com"`

### Mistake 3: Missing Commas
❌ Wrong: `"email":"test@gmail.com" "company_name":"Test"`  
✅ Right: `"email":"test@gmail.com","company_name":"Test"`

---

## The Correct Format

**Always use this format:**

```json
{"email":"THEIR_EMAIL","company_name":"THEIR_COMPANY","tier":"premium"}
```

**Replace:**
- `THEIR_EMAIL` → Their actual email
- `THEIR_COMPANY` → Their actual company name
- `"premium"` → Can also be `"basic"`

---

## That's It!

**Just copy the corrected command above and replace the email/company.**

**One command = Account created!** 🚀

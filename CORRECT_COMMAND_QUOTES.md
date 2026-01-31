# ⚠️ Quote Problem - Fixed Command

**Status:** Complete. Use the commands below with straight quotes; pick the API URL that matches your deployment (Railway or white-label).

---

## Your Command Problem

**Your command has smart quotes (curly quotes) instead of straight quotes.**

The shell sees: `-d '{` and waits forever for the closing quote because the JSON uses smart quotes `"` instead of regular quotes `"`.

---

## What to Do RIGHT NOW

1. **Press `Ctrl + C`** to cancel the hanging command

2. **Use the CORRECT command below** (with straight quotes)

---

## ✅ CORRECT Command (Copy This EXACTLY)

**Option A – Railway backend:**
```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"nextelevenstudios@gmail.com","company_name":"Customer Company","tier":"premium"}'
```

**Option B – White-label backend** (if you use `BACKEND_PUBLIC_URL` / snip.mothership-ai.com):
```bash
curl -X POST https://snip.mothership-ai.com/api/clients -H "Content-Type: application/json" -d '{"email":"nextelevenstudios@gmail.com","company_name":"Customer Company","tier":"premium"}'
```

**Key differences:**
- ✅ Regular quotes `"` not smart quotes `"`
- ✅ `company_name` not `happy time`
- ✅ All quotes match properly

---

## Common Quote Issues

### ❌ Wrong (Smart Quotes):
```bash
-d '{“email":"test@gmail.com"}'
```
*(Shell waits forever for closing quote)*

### ✅ Right (Straight Quotes):
```bash
-d '{"email":"test@gmail.com"}'
```
*(Works immediately)*

---

## Quick Fix for Your Command

**What you typed:**
```bash
-d '{“email”:"nextelevenstudios@gmail.com","happy time":"Customer Company","tier":"premium"}'
```

**Problems:**
1. Smart quotes: `"` instead of `"`
2. Wrong field: `"happy time"` should be `"company_name"`

**Fixed version:**
```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"nextelevenstudios@gmail.com","company_name":"Customer Company","tier":"premium"}'
```

---

## Copy This Exact Command

**Press Ctrl+C first, then paste this** (use Railway URL; if your backend is white-label, replace with `https://snip.mothership-ai.com`):

```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"nextelevenstudios@gmail.com","company_name":"Customer Company","tier":"premium"}'
```

---

## If Email Already Exists

If you see `"Email already registered"`, that's fine! That email already has an account.

**To create a NEW account, use a different email:**

```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"customer@example.com","company_name":"Customer Company","tier":"premium"}'
```

---

## Summary

**Right now:**
1. Press `Ctrl + C` (cancel hanging command)
2. Copy the correct command above (Option A or B depending on your backend)
3. Paste and press Enter
4. Done! ✅

---

**Note:** Replace the API URL in the command with your actual backend URL (Railway or white-label) if different.

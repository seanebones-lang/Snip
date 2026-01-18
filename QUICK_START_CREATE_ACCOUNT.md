# ⚡ Quick Start: Create Customer Account

## In Simple Terms

**You run a command in your Terminal to create their account.**

That's it. No special software. Just Terminal.

---

## Step 1: Open Terminal

**On Mac:**
- Press `Cmd + Space`
- Type `Terminal`
- Press `Enter`

**On Windows:**
- Press `Win + R`
- Type `cmd`
- Press `Enter`

---

## Step 2: Copy This Command

**Copy this whole command** (it's all one command):

```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"customer@example.com","company_name":"Customer Company","tier":"premium"}'
```

**Replace:**
- `customer@example.com` → Their actual email
- `Customer Company` → Their actual company name

**Keep:** `tier":"premium"` (or change to `"basic"`)

---

## Step 3: Paste and Press Enter

1. Paste the command in Terminal
2. Press `Enter`
3. Wait 2 seconds

---

## Step 4: You Get Back Their Info

You'll see something like:

```
{"id":"abc123-def456...","email":"customer@example.com","company_name":"Customer Company","api_key":"snip_xxxxxxxxxxxxx","tier":"premium"}
```

**Copy the `api_key` value** and send it to them.

---

## Example: Real Customer

**Customer Info:**
- Email: `sarah@techstartup.com`
- Company: `TechStartup Inc`

**Command:**

```bash
curl -X POST https://snip-production.up.railway.app/api/clients -H "Content-Type: application/json" -d '{"email":"sarah@techstartup.com","company_name":"TechStartup Inc","tier":"premium"}'
```

**Response:**

```json
{
  "id": "9d57eadc-f253-4801-a1f2-f6c45df6b615",
  "email": "sarah@techstartup.com",
  "company_name": "TechStartup Inc",
  "api_key": "snip_jWXHOqb3Recjl59s4pvygSM9b...",
  "tier": "premium"
}
```

**You email them:**

```
Hi Sarah!

Go to: https://snip.mothership-ai.com
Enter this API key: snip_jWXHOqb3Recjl59s4pvygSM9b...

Thanks!
```

---

## Where You Do This

**You do this on YOUR computer, in YOUR Terminal.**

Not on a website. Not on a dashboard. 

Just in Terminal/Command Prompt.

---

## What Happens Next

1. ✅ You run the command → Account created
2. ✅ You get API key → You email it to customer
3. ✅ Customer goes to dashboard → Enters API key
4. ✅ Customer customizes → Gets embed code
5. ✅ Customer pastes code → Chatbot appears!

---

## That's It!

**No website needed.**  
**No dashboard needed.**  
**Just Terminal + one command.**

**You create accounts using the API endpoint via Terminal.** 🚀

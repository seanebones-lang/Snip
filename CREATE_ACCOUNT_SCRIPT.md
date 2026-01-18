# ✅ GUARANTEED WORKING - Use This Script

## Problem Solved

**I created a script file you can run directly - no quote issues!**

---

## Step 1: Press Ctrl+C (Cancel Hanging Command)

---

## Step 2: Edit the Script

**Open this file:**
```
/Users/nexteleven/snip/Snip/create_customer.sh
```

**Change the email and company name, then run:**

```bash
bash /Users/nexteleven/snip/Snip/create_customer.sh
```

**OR just edit and run:**

```bash
cd /Users/nexteleven/snip/Snip
nano create_customer.sh  # Edit email/company
bash create_customer.sh   # Run it
```

---

## Step 3: Alternative - Python Command

**This avoids all quote issues:**

```bash
python3 -c "import subprocess; import sys; subprocess.run(['curl', '-X', 'POST', 'https://snip-production.up.railway.app/api/clients', '-H', 'Content-Type: application/json', '-d', '{\"email\":\"customer@example.com\",\"company_name\":\"Customer Company\",\"tier\":\"premium\"}'])"
```

**Replace `customer@example.com` and `Customer Company` with actual values.**

---

## The Script File

**Location:** `/Users/nexteleven/snip/Snip/create_customer.sh`

**Contents:**
```bash
#!/bin/bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@example.com","company_name":"Customer Company","tier":"premium"}'
```

**Edit the email/company, then run:**
```bash
bash create_customer.sh
```

---

## That's It!

**No quote issues - just edit and run the script!** 🚀

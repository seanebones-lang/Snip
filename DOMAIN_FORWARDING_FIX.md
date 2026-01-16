# Domain Forwarding Issue - Fix Guide

## The Problem

If you're using **domain forwarding** (redirect) instead of **DNS CNAME**, it can break the API proxy:

- ❌ **Domain Forwarding**: `snip.mothership-ai.com` → redirects to Vercel URL
  - Breaks API paths (`/api/*` gets lost)
  - Branding/snippet pages won't work
  
- ✅ **DNS CNAME**: `snip.mothership-ai.com` → points directly to Vercel
  - Preserves all paths
  - API proxy works correctly

## Solution: Use DNS CNAME Instead of Forwarding

### Step 1: Remove Domain Forwarding

In your domain registrar (where you manage `mothership-ai.com`):
1. Remove any forwarding/redirect rules for `snip.mothership-ai.com`
2. Remove any A records pointing to forwarding services

### Step 2: Add CNAME Record

Add a CNAME record in your DNS:

```
Type: CNAME
Name: snip
Value: cname.vercel-dns.com
TTL: 3600 (or Auto)
```

### Step 3: Configure in Vercel

1. Go to Vercel Dashboard
2. Select your dashboard project
3. Go to **Settings** → **Domains**
4. Add `snip.mothership-ai.com`
5. Follow Vercel's DNS verification steps

### Step 4: Wait for DNS Propagation

- DNS changes can take 5 minutes to 48 hours
- Usually works within 15-30 minutes
- Check with: `dig snip.mothership-ai.com`

## Verify It's Working

After DNS propagates, test:

```bash
# Should return JSON (not HTML redirect)
curl https://snip.mothership-ai.com/api/healthz

# Should return dashboard HTML
curl https://snip.mothership-ai.com/
```

## Masking the Dashboard URL

**Good news**: Your custom domain already masks the Vercel URL!

- ✅ Users see: `https://snip.mothership-ai.com`
- ❌ Users don't see: `https://dashboard-*.vercel.app`

The Vercel URL still exists but is hidden. Once you set up the CNAME properly, all traffic goes through your custom domain.

## Current Status

- ✅ API proxy configured in `vercel.json`
- ✅ Dashboard deployed to Vercel
- ⚠️ Need to switch from forwarding to CNAME DNS

---

**After switching to CNAME, the branding and snippet pages will work!**

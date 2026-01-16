# Domain Setup Guide - snip.mothership-ai.com

## Current Setup

Your dashboard is accessible at:
- **Custom Domain**: https://snip.mothership-ai.com
- **Vercel URL**: https://dashboard-*.vercel.app (masked/redirected)

## How It Works

1. **Custom Domain**: `snip.mothership-ai.com` is configured in Vercel
2. **API Proxy**: All `/api/*` requests are proxied to Railway backend
3. **Dashboard**: Served from Vercel with your custom domain

## Domain Configuration

### In Vercel Dashboard:

1. Go to your project settings
2. Navigate to **Domains**
3. Add `snip.mothership-ai.com`
4. Follow DNS instructions:
   - Add CNAME record: `snip` → `cname.vercel-dns.com`
   - Or A record if using apex domain

### DNS Records Needed:

```
Type: CNAME
Name: snip
Value: cname.vercel-dns.com
```

## API Proxy Configuration

The `vercel.json` file proxies all API requests:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://snip-production.up.railway.app/api/$1"
    }
  ]
}
```

This means:
- `https://snip.mothership-ai.com/api/config` → `https://snip-production.up.railway.app/api/config`
- `https://snip.mothership-ai.com/api/embed-snippet` → `https://snip-production.up.railway.app/api/embed-snippet`

## Troubleshooting

### If Branding/Snippet Pages Are Empty:

1. **Check DNS**: Verify `snip.mothership-ai.com` resolves correctly
2. **Check SSL**: Ensure SSL certificate is active (Vercel auto-provisions)
3. **Check Proxy**: Test API endpoint directly:
   ```bash
   curl https://snip.mothership-ai.com/api/healthz
   ```
4. **Check Browser Console**: Look for CORS or network errors

### If Domain Forwarding Issues:

If you're using a domain forward/redirect instead of DNS:
- **Problem**: Forwards don't preserve API paths
- **Solution**: Use DNS CNAME instead of forwarding

## Masking the Dashboard URL

The dashboard URL is already "masked" by using your custom domain:
- ✅ Users see: `https://snip.mothership-ai.com`
- ❌ Users don't see: `https://dashboard-*.vercel.app`

The Vercel URL still exists but is hidden behind your custom domain.

## Security

- All API requests are proxied through Vercel
- API keys are sent in headers (not visible in URLs)
- HTTPS is enforced by Vercel
- CORS is handled by the backend

---

**Your dashboard is accessible at: https://snip.mothership-ai.com**

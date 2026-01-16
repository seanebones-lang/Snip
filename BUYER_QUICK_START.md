# Snip Widget - Quick Start Guide

**Get your chatbot widget running in 5 minutes!**

---

## Step 1: Get Your Credentials (1 minute)

You'll receive an email with:
- **Client ID**: `123e4567-e89b-12d3-a456-426614174000` (save this!)
- **API Key**: `snip_live_xxxxx...` (keep secret!)
- **Widget CDN URL**: `https://your-widget.vercel.app`
- **API URL**: `https://snip-production.up.railway.app`

**📝 Save these in a secure location!**

---

## Step 2: Copy the Widget Code (30 seconds)

Use this code template:

```html
<script 
  src="WIDGET_CDN_URL/widget.js" 
  data-client-id="YOUR_CLIENT_ID"
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>
```

**Replace:**
- `WIDGET_CDN_URL` → Your Widget CDN URL from email
- `YOUR_CLIENT_ID` → Your Client ID from email

**Example:**
```html
<script 
  src="https://your-widget.vercel.app/widget.js" 
  data-client-id="123e4567-e89b-12d3-a456-426614174000"
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>
```

---

## Step 3: Add to Your Website (2 minutes)

### WordPress
1. Go to **Appearance** → **Theme Editor** → **Footer** (`footer.php`)
2. Find `</body>` tag
3. Paste code **BEFORE** `</body>`
4. Click **Update File**

**Or use a plugin:** "Insert Headers and Footers" → Footer section

### Shopify
1. Go to **Online Store** → **Themes** → **Edit code**
2. Open **Layout** → **theme.liquid**
3. Find `</body>` tag
4. Paste code **BEFORE** `</body>`
5. Click **Save**

### HTML/Static Website
1. Open your `index.html` file
2. Find `</body>` tag near the bottom
3. Paste code **BEFORE** `</body>`
4. Save and upload

### Wix
1. **Settings** → **Tracking & Analytics** → **+ New Tool** → **Custom**
2. Paste code in the code box
3. Choose **All pages** and **Body - end**
4. Click **Apply**

### Squarespace
1. **Settings** → **Advanced** → **Code Injection**
2. Paste code in **Footer** field
3. Click **Save**

---

## Step 4: Test It! (1 minute)

1. **Save/publish** your website changes
2. **Open your website** in a browser
3. **Look for widget button** (usually bottom-right corner)
4. **Click the button** to open chat
5. **Send a test message** (e.g., "Hello")
6. **Verify AI responds**

✅ **Success!** Your chatbot is live!

---

## Quick Troubleshooting

**Widget not appearing?**
- Check code is before `</body>` tag
- Verify Client ID is correct (copy-paste exactly)
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for errors (F12)

**Chat not working?**
- Verify API URL is correct: `https://snip-production.up.railway.app`
- Check internet connection
- Try refreshing the page

**Wrong colors/branding?**
- Colors update automatically after configuration
- May take 1-5 minutes to appear
- Clear browser cache

---

## What's Next?

### Customize Your Widget

**Via API** (for developers):
```bash
curl -X PATCH https://snip-production.up.railway.app/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "bot_name": "Support Bot",
    "primary_color": "#007bff",
    "welcome_message": "Hello! How can I help?"
  }'
```

**Via Support:**
Email support with your Client ID and desired changes.

### Common Customizations

- **Bot Name**: Change "Assistant" to your company name
- **Colors**: Match your brand colors (hex format: `#007bff`)
- **Welcome Message**: Custom first message
- **Logo**: Add your company logo (Premium)
- **Document Training**: Train with your docs (Premium)

---

## Need Help?

1. **Check full guide**: See `BUYER_ONBOARDING_GUIDE.md` for detailed help
2. **Troubleshooting section**: Solutions to common issues
3. **FAQ**: Answers to 50+ questions
4. **Contact Support**: Include your Client ID in your message

---

## Quick Reference

**Your Credentials:**
- Client ID: `_____________________` (public - safe in website code)
- API Key: `_____________________` (secret - never in website code!)

**Widget Code:**
```html
<script 
  src="_____________________/widget.js" 
  data-client-id="_____________________"
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>
```

**Production URLs:**
- API: `https://snip-production.up.railway.app`
- API Docs: `https://snip-production.up.railway.app/docs`

---

**That's it! You're done in 5 minutes.** 🎉

For detailed instructions, troubleshooting, and FAQs, see the complete `BUYER_ONBOARDING_GUIDE.md`.

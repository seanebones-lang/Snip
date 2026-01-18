# Quick Start Guide - Dom and Tom Chatbot

Hey Tom! 👋

Your chatbot is ready to go. Here's everything you need to get started.

---

## Step 1: Access Your Dashboard

**Go to:** https://snip.mothership-ai.com

**Login with your API Key:**
```
snip_KJRVGdZj2fCfk5VUweUiAQE3y2O9eJNbvRGSm4FLuFE
```

Just paste that API key on the login page and click "Access Dashboard".

---

## Step 2: Customize Your Chatbot

Once you're logged in, you'll see several pages:

### **Branding Page** (Recommended First!)
- **Bot Name**: Change the chatbot's name (e.g., "Dom and Tom Support")
- **Colors**: Set your brand colors (primary, secondary, background)
- **Logo**: Upload your company logo
- **Welcome Message**: Customize the greeting message
- **System Prompt**: Tell the bot how to behave

### **Snippet Page**
- Get your embed code to add to your website
- Copy the code and paste it into your site

### **Documents Page** (Premium Feature)
- Upload PDFs, Word docs, or text files
- Train the bot with your company documents
- The bot will use these to answer questions

---

## Step 3: Add the Widget to Your Website

### The Widget Code

Go to the **Snippet** page in your dashboard and copy the embed code. It will look like this:

```html
<script 
  src="https://widget-sigma-sage.vercel.app/widget.js" 
  data-client-id="9167ca71-547d-441e-9a4b-a13e3be07358"
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>
```

### Where to Add It

**WordPress:**
1. Go to **Appearance** → **Theme Editor** → **Footer** (`footer.php`)
2. Find the `</body>` tag
3. Paste the code **BEFORE** `</body>`
4. Click **Update File**

**Or use a plugin:** "Insert Headers and Footers" → Footer section

**Shopify:**
1. Go to **Online Store** → **Themes** → **Edit code**
2. Open **Layout** → `theme.liquid`
3. Find `</body>` tag
4. Paste the code **BEFORE** `</body>`
5. Click **Save**

**HTML/Static Site:**
1. Open your `index.html` file
2. Find `</body>` tag near the bottom
3. Paste the code **BEFORE** `</body>`
4. Save and upload

---

## ✅ Voice Feature - Fully Working!

### The Voice Feature

Your chatbot includes **text-to-speech (voice)** capabilities that are **fully implemented and working**. The bot automatically speaks its responses using high-quality xAI Grok Voice Agent API.

### How It Works:

✅ **Automatic Voice Responses**
- Every AI response is automatically converted to speech
- Uses natural, human-like voice (xAI Grok Voice - Ara voice by default)
- Audio plays automatically after each response

✅ **Reliable & Robust**
- Automatic error recovery (falls back to browser TTS if needed)
- Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- Optimized for performance (no memory leaks, handles long responses)

✅ **Works On:**
- Live websites with HTTPS (e.g., `https://domandtom.com`)
- Any deployed/test site with HTTPS
- Mobile and desktop browsers

⚠️ **Note for Testing:**
- Voice requires HTTPS and a deployed site
- Testing locally (`file://` or `localhost`) may show text-only (this is normal for security)
- Once deployed to your live website, voice works automatically!

### Voice Features:

- **Natural Sounding**: High-quality xAI voice synthesis
- **Automatic**: No configuration needed - works out of the box
- **Accessible**: Screen reader announcements for visually impaired users
- **Resilient**: Automatic fallback to browser TTS if needed

---

## Testing Checklist

1. ✅ **Customize** your bot in the dashboard (branding, colors, messages)
2. ✅ **Copy** your widget embed code from the Snippet page
3. ✅ **Add** the code to your website (WordPress/Shopify/HTML)
4. ✅ **Publish** your website changes
5. ✅ **Test** on your live website (voice will work!)
6. ⚠️ Don't test offline - voice won't work until deployed

---

## Need Help?

- **Dashboard Issues**: Check that you're using the correct API key
- **Widget Not Appearing**: Make sure the code is in the right place (before `</body>`)
- **Voice Not Working**: Ensure it's deployed to a live website (not local)
- **Customization**: All settings are in the dashboard under "Branding"

---

## Your Account Details

**Dashboard URL:** https://snip.mothership-ai.com  
**API Key:** `snip_KJRVGdZj2fCfk5VUweUiAQE3y2O9eJNbvRGSm4FLuFE`  
**Client ID:** `9167ca71-547d-441e-9a4b-a13e3be07358`  
**Tier:** Premium (includes document upload & RAG training)

---

That's it! Get started at **snip.mothership-ai.com** and customize away. Once you deploy to your site, the voice feature will kick in automatically. 🚀

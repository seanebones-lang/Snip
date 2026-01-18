# 🚀 Simple Customer Setup - Step by Step

## The Process (Super Simple!)

### 1. **Customer Pays** 💰
   - They sign up / purchase
   - You get their email and company name

### 2. **You Create Their Account** 🔧
   Run this command (replace with their info):

   ```bash
   curl -X POST https://snip-production.up.railway.app/api/clients \
     -H "Content-Type: application/json" \
     -d '{
       "email": "customer@example.com",
       "company_name": "Their Company",
       "tier": "premium"
     }'
   ```

   **You get back:**
   - Client ID (e.g., `abc123-def456-...`)
   - API Key (e.g., `snip_xxxxxxxx...`)

### 3. **Send Them Their API Key** 📧
   Email them:
   ```
   Subject: Your Snip Chatbot API Key
   
   Hi!
   
   Your account is ready. Here's your API key:
   
   snip_xxxxxxxxxxxxxxxxxxxxx
   
   Go to: https://snip.mothership-ai.com
   Enter your API key to access your dashboard.
   
   Thanks!
   ```

### 4. **Customer Goes to Dashboard** 🎨
   - They visit: **https://snip.mothership-ai.com**
   - They enter their **API Key**
   - They click "Login" / "Access Dashboard"

### 5. **Customer Customizes** ✨
   On the dashboard, they can:
   - Change bot name
   - Pick colors
   - Edit welcome message
   - Upload logo
   - Configure settings
   - **View their embed code**

### 6. **Customer Gets Embed Code** 📋
   On the dashboard, they'll see their embed code like this:
   
   ```html
   <script 
     src="https://widget-sigma-sage.vercel.app/widget.js" 
     data-client-id="abc123-def456-..."
     async>
   </script>
   ```

### 7. **Customer Pastes Code** 📝
   They copy that code and paste it into their website (anywhere in the HTML, usually before `</body>`).

### 8. **Done!** ✅
   Their chatbot appears on their website with TTS working!

---

## What You Need to Know

### **You Do:**
1. ✅ Create account (curl command above)
2. ✅ Send them API key via email

### **They Do:**
1. ✅ Go to dashboard website
2. ✅ Enter API key
3. ✅ Customize their chatbot
4. ✅ Copy embed code
5. ✅ Paste on their website

---

## Quick Reference

**Dashboard URL:** https://snip.mothership-ai.com  
**Backend URL:** https://snip-production.up.railway.app  
**Widget URL:** https://widget-sigma-sage.vercel.app/widget.js

**Tier Options:** `basic` or `premium`

---

## Example Email to Customer

```
Subject: Your Snip Chatbot is Ready! 🎉

Hi [Customer Name],

Your account is set up! Here's what to do next:

1. Go to: https://snip.mothership-ai.com

2. Enter this API key:
   snip_xxxxxxxxxxxxxxxxxxxxx

3. Customize your chatbot (name, colors, message, etc.)

4. Copy your embed code from the dashboard

5. Paste it into your website

That's it! Your talking chatbot will appear on your site.

Need help? Just reply to this email.

Thanks!
[Your Name]
```

---

## That's It!

**Simple flow:**
1. Customer pays → 
2. You create account → 
3. You send API key → 
4. They go to dashboard → 
5. They customize → 
6. They get embed code → 
7. They paste it → 
8. ✅ Done!

**No technical knowledge needed from them!** Just paste the code. 🚀

# Complete Buyer Onboarding Guide - Snip Chatbot Widget

Welcome to Snip! This comprehensive guide will walk you through everything you need to get your AI chatbot widget up and running on your website.

---

## Table of Contents

1. [What is Snip?](#what-is-snip)
2. [Prerequisites](#prerequisites)
3. [Getting Started - Receiving Your Credentials](#getting-started)
4. [Understanding Your Credentials](#understanding-credentials)
5. [Installation Guide](#installation-guide)
6. [Configuration & Customization](#configuration)
7. [Testing Your Widget](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Frequently Asked Questions (FAQ)](#faq)
10. [Advanced Features](#advanced-features)
11. [Support & Resources](#support)

---

## What is Snip? {#what-is-snip}

Snip is an AI-powered chatbot widget that you can embed on your website to provide instant customer support. It features:

- **AI-Powered Responses**: Uses advanced AI to answer customer questions 24/7
- **Fully Customizable**: Match your brand colors, logo, and messaging
- **Easy Installation**: One line of code - no technical skills required
- **Document Training (Premium)**: Train the bot with your own documents for accurate answers
- **Analytics**: Track conversations and usage statistics

### What You'll Get

After purchase, you'll receive:
- A **Client ID** (unique identifier for your widget)
- An **API Key** (for managing settings - keep this secret!)
- Widget embed code ready to paste
- Access to customization options

---

## Prerequisites {#prerequisites}

Before you begin, make sure you have:

### Required:
- ✅ A website (WordPress, Shopify, HTML, or any platform)
- ✅ Access to edit your website's HTML code
- ✅ Basic understanding of copy/paste

### Optional but Helpful:
- 📝 Text editor (to save your credentials)
- 🌐 Browser developer tools knowledge (for troubleshooting)
- 📧 Email access (for receiving credentials)

### What You DON'T Need:
- ❌ Programming knowledge
- ❌ Server access
- ❌ Database setup
- ❌ API knowledge

**Important**: You must have access to edit your website's HTML, or know someone who can add code to your site (web developer, IT team, etc.).

---

## Getting Started - Receiving Your Credentials {#getting-started}

### Step 1: Receive Your Email

After your purchase, you'll receive an email containing:

1. **Your Client ID** - A unique identifier (looks like: `123e4567-e89b-12d3-a456-426614174000`)
2. **Your API Key** - A secret key starting with `snip_live_`
3. **Widget CDN URL** - Where the widget file is hosted
4. **API URL** - The backend service URL (usually: `https://snip-production.up.railway.app`)

### Step 2: Save Your Credentials Securely

**⚠️ CRITICAL: Save these immediately!**

Create a document and save:
- **Client ID**: This is public and can be shared in your website code
- **API Key**: This is SECRET - never share it publicly or put it in your website code

**Recommended Storage:**
- Password manager (1Password, LastPass, etc.)
- Secure note-taking app
- Encrypted file on your computer
- Printed copy in a secure location

### Step 3: Verify Your Information

Double-check that you have:
- ✅ Correct Client ID (UUID format - 36 characters with hyphens)
- ✅ API Key (starts with `snip_live_` followed by long string)
- ✅ Widget CDN URL (starts with `https://`)
- ✅ API URL (starts with `https://`)

If anything is missing or unclear, contact support immediately.

---

## Understanding Your Credentials {#understanding-credentials}

### Client ID

**Format**: UUID (e.g., `123e4567-e89b-12d3-a456-426614174000`)
- **What it is**: Your unique account identifier
- **Where to use**: In the widget embed code (`data-client-id`)
- **Security**: Can be public (safe to put on your website)

### API Key

**Format**: `snip_live_` followed by a long random string
- **What it is**: Secret key for managing your account settings
- **Where to use**: Only in API calls to update configuration (NOT in website code!)
- **Security**: Must remain secret - never expose in frontend code

### Widget CDN URL

**Format**: `https://your-widget-deployment.vercel.app` or similar
- **What it is**: Where the widget JavaScript file is hosted
- **Where to use**: In the `src` attribute of the script tag

### API URL

**Format**: `https://snip-production.up.railway.app`
- **What it is**: The backend service that powers your chatbot
- **Where to use**: In the `data-api-url` attribute of the script tag

---

## Installation Guide {#installation-guide}

Choose your platform below and follow the instructions.

### The Universal Widget Embed Code

This is the code you'll be adding (replace the placeholders with your actual values):

```html
<script 
  src="WIDGET_CDN_URL/widget.js" 
  data-client-id="YOUR_CLIENT_ID"
  data-api-url="API_URL"
  async>
</script>
```

**Example with real values:**
```html
<script 
  src="https://your-widget.vercel.app/widget.js" 
  data-client-id="123e4567-e89b-12d3-a456-426614174000"
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>
```

---

### Installation Methods by Platform

#### Method 1: WordPress (Recommended: Theme Editor)

**Step 1: Access Theme Editor**
1. Log in to your WordPress admin dashboard
2. Go to **Appearance** → **Theme Editor**
3. Select **Theme Footer** (`footer.php`) from the right sidebar

**Step 2: Add Widget Code**
1. Scroll to the bottom of the file
2. Find the `</body>` tag (usually near the end)
3. Add the widget code **BEFORE** the `</body>` tag
4. Click **Update File**

**Alternative: Using a Plugin (Safer)**
1. Install a plugin like "Insert Headers and Footers" or "Code Snippets"
2. Go to the plugin settings
3. Paste the widget code in the "Footer" section
4. Save changes

#### Method 2: WordPress (Using a Plugin - Easiest)

**Recommended Plugins:**
- **Insert Headers and Footers** (free)
- **Code Snippets** (free)
- **Header Footer Code Manager** (free)

**Steps:**
1. Install your chosen plugin
2. Activate it
3. Go to plugin settings
4. Find "Footer Code" or "Before </body>" section
5. Paste your widget code
6. Save

**Why use a plugin?**
- Code won't be lost when you update your theme
- Easier to manage
- No risk of breaking your site

#### Method 3: Shopify

**Step 1: Access Theme Code**
1. Log in to Shopify Admin
2. Go to **Online Store** → **Themes**
3. Click **Actions** → **Edit code**

**Step 2: Add to Theme Footer**
1. In the left sidebar, open **Layout**
2. Click **theme.liquid**
3. Find `</body>` near the bottom
4. Add widget code **BEFORE** `</body>`
5. Click **Save**

**Alternative: Using a Section**
1. In theme.liquid, find `{{ content_for_layout }}`
2. Add widget code after this line
3. Save

**Important Note**: Shopify may remove custom code during theme updates. Consider using a Shopify app or saving your customizations in a separate file.

#### Method 4: HTML/Static Website

**Step 1: Open Your HTML File**
- Use a text editor (Notepad, TextEdit, VS Code, etc.)
- Open your `index.html` or main HTML file

**Step 2: Find the `</body>` Tag**
- Look for `</body>` near the end of the file
- This closes the body section

**Step 3: Add Widget Code**
- Paste your widget code **BEFORE** `</body>`
- Example:
  ```html
  <!-- Your existing content -->
  
  <!-- Snip Chatbot Widget -->
  <script 
    src="https://your-widget.vercel.app/widget.js" 
    data-client-id="123e4567-e89b-12d3-a456-426614174000"
    data-api-url="https://snip-production.up.railway.app"
    async>
  </script>
  </body>
  </html>
  ```

**Step 4: Save and Upload**
- Save your HTML file
- Upload it to your web server if needed

#### Method 5: Wix

**Step 1: Add Custom Code**
1. Log in to Wix Editor
2. Click **Settings** (gear icon) in the top bar
3. Go to **Tracking & Analytics**
4. Click **+ New Tool**
5. Select **Custom**

**Step 2: Configure**
1. Give it a name (e.g., "Chatbot Widget")
2. Paste your widget code
3. Choose **Load code on**: **All pages** or specific pages
4. Choose **Place code in**: **Body - end**
5. Click **Apply**

#### Method 6: Squarespace

**Step 1: Add Code Injection**
1. Log in to Squarespace
2. Go to **Settings** → **Advanced** → **Code Injection**
3. Find **Footer** section

**Step 2: Add Widget Code**
1. Paste your widget code in the Footer field
2. Click **Save**

#### Method 7: Webflow

**Step 1: Add Custom Code**
1. Open your Webflow project
2. Go to **Project Settings** (gear icon)
3. Click **Custom Code** tab
4. Find **Footer Code** section

**Step 2: Add Widget**
1. Paste your widget code
2. Click **Save**
3. Publish your site

#### Method 8: Custom CMS or Framework

**General Instructions:**
1. Find where your site's global HTML is rendered
2. Look for the `</body>` tag
3. Add widget code before `</body>`
4. Ensure it's on all pages where you want the widget

**For React/Next.js:**
- Add to `_app.js` or `_app.tsx` in Next.js
- Add to `App.js` or `App.tsx` in React

**For Vue.js:**
- Add to `App.vue` or `index.html`

---

### Important Installation Notes

#### Where to Place the Code

**✅ CORRECT: Before `</body>` tag**
```html
<body>
  <!-- Your website content -->
  
  <!-- Widget goes here -->
  <script ...></script>
</body>
```

**❌ WRONG: In the middle of content**
```html
<body>
  <div>Content</div>
  <script ...></script>  <!-- Don't do this -->
  <div>More content</div>
</body>
```

**Why?** Placing it before `</body>` ensures:
- All page content loads first
- Widget doesn't block page rendering
- Widget appears when ready

#### Using the `async` Attribute

The widget code includes `async` attribute:
```html
<script src="..." async></script>
```

**What this means:**
- Script loads in parallel with page content
- Doesn't block page loading
- Executes when ready

**Keep it!** Don't remove the `async` attribute.

#### Multiple Pages

**Question**: Do I need to add it to every page?

**Answer**: 
- If added in theme template/footer: **No** - it appears on all pages automatically
- If added to a single HTML file: **Yes** - add to each page where you want the widget

**Best Practice**: Add to global template/theme file (footer.php, theme.liquid, etc.) so it appears site-wide.

---

## Configuration & Customization {#configuration}

After installation, you can customize your widget's appearance and behavior.

### Available Customization Options

#### Basic Settings

| Setting | Description | Example |
|---------|-------------|---------|
| **Bot Name** | Name shown in the widget | "Support Bot", "AI Assistant" |
| **Welcome Message** | First message users see | "Hi! How can I help you today?" |
| **Primary Color** | Main widget color (hex code) | `#007bff` (blue) |
| **Secondary Color** | Secondary/accent color | `#6c757d` (gray) |
| **Logo URL** | Your company logo image URL | `https://example.com/logo.png` |

#### Advanced Settings (Premium)

| Setting | Description |
|---------|-------------|
| **System Prompt** | AI personality instructions |
| **Document Training** | Upload PDFs/docs to train the bot |
| **Position** | Widget position (`bottom-right` or `bottom-left`) |
| **Auto Open** | Automatically open chat on page load |
| **Show Branding** | Display "Powered by Snip" (Premium can hide) |

### How to Customize

#### Method 1: Via API (Recommended for Developers)

You'll need:
- Your API Key (secret - from your welcome email)
- API URL (usually `https://snip-production.up.railway.app`)

**Update Configuration:**

```bash
curl -X PATCH https://snip-production.up.railway.app/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "bot_name": "Your Bot Name",
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "welcome_message": "Hello! How can I help?",
    "logo_url": "https://yourwebsite.com/logo.png"
  }'
```

**Example Request:**
```bash
curl -X PATCH https://snip-production.up.railway.app/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer snip_live_abc123..." \
  -d '{
    "bot_name": "Acme Support",
    "primary_color": "#FF6B35",
    "welcome_message": "Welcome to Acme! How can I assist you today?"
  }'
```

**View Current Configuration:**
```bash
curl https://snip-production.up.railway.app/api/config \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Method 2: Request Changes from Support

If you don't have API access or prefer not to use it:

1. Email support with your Client ID
2. Specify what you want to change
3. Provide the new values

**Example Email:**
```
Subject: Widget Configuration Change Request

Hi Support,

Please update my widget configuration:
- Client ID: 123e4567-e89b-12d3-a456-426614174000
- Bot Name: "Acme Support" → "Help Desk Bot"
- Primary Color: #007bff → #FF6B35
- Welcome Message: "Hello! How can I help?" → "Welcome to Acme!"

Thank you!
```

### Color Codes (Hex Format)

Colors must be in hex format: `#RRGGBB`

**Examples:**
- Blue: `#007bff`
- Red: `#dc3545`
- Green: `#28a745`
- Orange: `#ff6b35`
- Purple: `#6f42c1`
- Dark Gray: `#343a40`
- Light Gray: `#6c757d`

**How to find your brand colors:**
1. Use a color picker tool online
2. Check your brand guidelines
3. Use your website's existing colors

**Color Picker Tools:**
- [HTML Color Picker](https://www.w3schools.com/colors/colors_picker.asp)
- [Coolors](https://coolors.co/)
- Browser DevTools (right-click element → Inspect → Color picker)

### Logo Requirements

**Supported Formats:**
- PNG (recommended)
- JPG/JPEG
- SVG (recommended for scalability)

**Best Practices:**
- **Size**: 200x200 pixels or square aspect ratio
- **File Size**: Under 500KB (smaller = faster loading)
- **Background**: Transparent (PNG) works best
- **URL**: Must be publicly accessible (HTTPS recommended)

**Where to Host Logo:**
- Your website (`https://yoursite.com/logo.png`)
- CDN (Cloudflare, AWS CloudFront, etc.)
- Image hosting service (Imgur, Cloudinary)

**Getting Logo URL:**
1. Upload logo to your website or hosting service
2. Get the direct image URL (ends with `.png`, `.jpg`, etc.)
3. Use this URL in configuration

---

## Testing Your Widget {#testing}

### Step 1: Basic Visibility Test

**After adding the widget code:**

1. **Save your changes** on your website
2. **Open your website** in a browser
3. **Look for the widget** - usually appears as a button in the bottom-right corner
4. **Check appearance** - should match your brand colors

**Expected Result:**
- Widget button/icon visible in corner
- Button has your primary color
- Button is clickable

### Step 2: Chat Interface Test

1. **Click the widget button** to open chat
2. **Verify welcome message** appears (your custom message)
3. **Type a test message** (e.g., "Hello")
4. **Check for response** - AI should reply

**Expected Result:**
- Chat window opens smoothly
- Welcome message displays correctly
- AI responds to your message
- Chat interface matches your color scheme

### Step 3: Cross-Browser Testing

Test on different browsers:
- ✅ Google Chrome
- ✅ Mozilla Firefox
- ✅ Safari (Mac/iOS)
- ✅ Microsoft Edge
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

**What to check:**
- Widget appears on all browsers
- Chat opens and functions correctly
- Colors display properly
- No JavaScript errors

### Step 4: Mobile Testing

**Important**: Most traffic is mobile - test thoroughly!

1. **Open your site on mobile** (phone/tablet)
2. **Check widget visibility** - should appear in corner
3. **Test chat functionality** - send messages
4. **Verify layout** - chat should be mobile-friendly

**Expected on Mobile:**
- Widget button visible but not intrusive
- Chat window fits screen properly
- Easy to type and send messages
- Buttons are touch-friendly (large enough)

### Step 5: Performance Test

**Check loading time:**
1. Use browser DevTools (F12)
2. Open Network tab
3. Refresh page
4. Find `widget.js` request
5. Check load time (should be under 1 second)

**If widget loads slowly:**
- Check your internet connection
- Verify Widget CDN URL is correct
- Contact support if consistently slow

### Troubleshooting Test Issues

**Widget doesn't appear?**
- See [Troubleshooting](#troubleshooting) section below
- Check browser console for errors (F12 → Console tab)

**Chat not responding?**
- Verify API URL is correct in embed code
- Check internet connection
- Try refreshing the page

**Colors not matching?**
- Confirm color codes are in hex format (`#RRGGBB`)
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Wait a few minutes for changes to propagate

---

## Troubleshooting {#troubleshooting}

### Common Issues and Solutions

#### Issue 1: Widget Not Appearing

**Symptoms:**
- No widget button visible on website
- No errors, just nothing appears

**Possible Causes & Solutions:**

**Cause A: Code Not Added Correctly**
- **Check**: Is the code in the right place? (Before `</body>` tag)
- **Fix**: Move code to immediately before `</body>`
- **Verify**: View page source (right-click → View Page Source) and search for "widget.js"

**Cause B: Client ID Incorrect**
- **Check**: Compare Client ID in code with your received ID
- **Fix**: Replace with correct Client ID (case-sensitive)
- **Format**: Should be UUID format with hyphens

**Cause C: Widget CDN URL Wrong**
- **Check**: Does the URL load? Try opening `YOUR_CDN_URL/widget.js` in browser
- **Fix**: Replace with correct Widget CDN URL from your welcome email
- **Test**: Should download a JavaScript file, not show 404

**Cause D: Browser Blocking Script**
- **Check**: Browser console for blocked content (F12 → Console)
- **Fix**: Disable ad blockers, check browser security settings
- **Test**: Try different browser or incognito mode

**Cause E: Page Not Saved/Published**
- **Check**: Did you save changes? Did you publish the site?
- **Fix**: Save and publish your website changes
- **Verify**: View live website (not editor preview)

#### Issue 2: Widget Appears But Chat Doesn't Work

**Symptoms:**
- Widget button visible
- Clicking opens chat window
- No response when sending messages

**Possible Causes & Solutions:**

**Cause A: API URL Incorrect**
- **Check**: Verify `data-api-url` attribute in embed code
- **Fix**: Ensure it matches your API URL exactly (usually `https://snip-production.up.railway.app`)
- **Test**: Try opening API URL in browser - should see JSON response

**Cause B: Client ID Mismatch**
- **Check**: Client ID in embed code matches your assigned ID
- **Fix**: Replace with correct Client ID
- **Important**: Client ID must be exact (including hyphens)

**Cause C: Network/CORS Issues**
- **Check**: Browser console for CORS errors (F12 → Console)
- **Fix**: Contact support - may need domain allowlisting
- **Workaround**: Try different network or disable VPN

**Cause D: API Service Down**
- **Check**: Visit API URL directly - should return valid response
- **Fix**: Contact support if API is unreachable
- **Status**: Check with support for service status

#### Issue 3: Wrong Colors or Branding

**Symptoms:**
- Widget has default colors instead of yours
- Logo not appearing
- Welcome message is default

**Possible Causes & Solutions:**

**Cause A: Configuration Not Saved**
- **Check**: Verify configuration was updated via API or support
- **Fix**: Re-save configuration with correct values
- **Wait**: Changes may take 1-5 minutes to appear

**Cause B: Browser Cache**
- **Check**: Old version cached in browser
- **Fix**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- **Alternative**: Clear browser cache completely

**Cause C: Color Format Wrong**
- **Check**: Colors must be hex format: `#RRGGBB` (e.g., `#007bff`)
- **Fix**: Ensure colors start with `#` and have 6 characters
- **Common Error**: Missing `#` or using color names (use hex codes)

**Cause D: Logo URL Invalid**
- **Check**: Open logo URL in browser - should show image
- **Fix**: Ensure logo is publicly accessible (HTTPS URL)
- **Test**: Logo should load when pasted in browser address bar

#### Issue 4: Widget Loading Slowly

**Symptoms:**
- Widget takes several seconds to appear
- Website feels slow

**Possible Causes & Solutions:**

**Cause A: Slow Internet Connection**
- **Check**: Test your internet speed
- **Fix**: Widget requires internet connection - improve connection
- **Impact**: Widget loads in parallel, shouldn't block page

**Cause B: Widget CDN Issues**
- **Check**: Try accessing widget.js URL directly
- **Fix**: Contact support if CDN is slow
- **Workaround**: None - CDN speed is service-dependent

**Cause C: Too Many Scripts on Page**
- **Check**: Count scripts on your page
- **Fix**: Widget loads asynchronously, but many scripts can slow page
- **Optimize**: Review other scripts for performance impact

#### Issue 5: Widget Appears on Some Pages But Not Others

**Symptoms:**
- Widget works on homepage
- Missing on other pages

**Possible Causes & Solutions:**

**Cause A: Code Only Added to One Page**
- **Check**: Was code added to page template or single page?
- **Fix**: Add to global template/theme file (footer, header, etc.)
- **Best Practice**: Add to theme template so it appears on all pages

**Cause B: Different Theme/Template for Different Pages**
- **Check**: Do different pages use different templates?
- **Fix**: Add widget code to all page templates
- **Alternative**: Use a global code injection method (plugin, etc.)

#### Issue 6: Mobile Display Issues

**Symptoms:**
- Widget looks wrong on mobile
- Buttons too small to click
- Chat window doesn't fit screen

**Possible Causes & Solutions:**

**Cause A: Mobile-Specific CSS Conflicts**
- **Check**: Do you have custom CSS affecting widgets?
- **Fix**: Widget has mobile-responsive styles - avoid overriding
- **Solution**: Contact support for custom mobile adjustments

**Cause B: Mobile Browser Compatibility**
- **Check**: Test on different mobile browsers
- **Fix**: Widget supports modern mobile browsers
- **Issue**: Very old mobile browsers may have issues

#### Issue 7: JavaScript Errors in Console

**Symptoms:**
- Widget not working
- Browser console shows red errors

**How to Check Console:**
1. Open browser DevTools (F12 or right-click → Inspect)
2. Click "Console" tab
3. Look for red error messages

**Common Errors & Fixes:**

**Error: "Failed to fetch" or "Network error"**
- **Fix**: Check API URL is correct and accessible
- **Check**: Internet connection is working

**Error: "Client ID not found" or "Invalid client_id"**
- **Fix**: Verify Client ID is correct in embed code
- **Check**: Client ID must be valid UUID format

**Error: "CORS policy" or "CORS error"**
- **Fix**: Contact support - domain may need allowlisting
- **Note**: CORS is server-side configuration

**Error: "widget.js failed to load"**
- **Fix**: Check Widget CDN URL is correct
- **Verify**: URL should end with `/widget.js`

---

## Frequently Asked Questions (FAQ) {#faq}

### General Questions

**Q: How long does it take to set up?**
A: Installation takes 5-10 minutes. You just need to paste the code and save. Configuration (customization) can take additional time depending on how much you want to customize.

**Q: Do I need coding knowledge?**
A: No! If you can copy and paste, you can install the widget. However, having someone with basic HTML knowledge helps if you run into issues.

**Q: Can I use it on multiple websites?**
A: Each Client ID is for one website/domain. Contact support if you need multiple installations.

**Q: Is there a mobile app?**
A: No, this is a web-based widget. It works on mobile browsers when visitors view your website.

**Q: What happens if I update my website theme?**
A: If the widget code is in your theme file, you may need to re-add it after theme updates. Using a plugin or global code injection prevents this.

### Technical Questions

**Q: Will the widget slow down my website?**
A: No. The widget loads asynchronously, meaning it doesn't block your page from loading. It appears after your page content loads.

**Q: Does it work with HTTPS?**
A: Yes! The widget requires HTTPS and works perfectly with secure websites.

**Q: Can I hide the widget on certain pages?**
A: This requires custom JavaScript. Contact support or your developer for page-specific hiding.

**Q: What browsers are supported?**
A: All modern browsers: Chrome, Firefox, Safari, Edge (latest versions). Works on desktop and mobile browsers.

**Q: Can I customize the widget position?**
A: Yes, but this requires configuration changes. Default is bottom-right. Contact support to change to bottom-left.

**Q: Does it work with site builders (Wix, Squarespace, etc.)?**
A: Yes! See the Installation Guide section for platform-specific instructions.

### Account & Credentials

**Q: I lost my API Key - what do I do?**
A: Contact support immediately with your Client ID. We can help you manage your account. **Note**: For security, we may require verification.

**Q: Can I change my Client ID?**
A: Client IDs are permanent and cannot be changed. This is by design for security and tracking.

**Q: Is my API Key safe in my website code?**
A: **NO!** Never put your API Key in your website HTML code. Only use it in server-side API calls. Your website code should only contain your Client ID (which is safe to be public).

**Q: Who can see my Client ID?**
A: Anyone who views your website's source code can see your Client ID. This is normal and safe - Client IDs are meant to be public.

### Features & Functionality

**Q: Can I train the bot with my own content?**
A: Yes! This is a Premium feature. You can upload PDFs, Word docs, and text files to train the bot with your specific knowledge base.

**Q: How does the AI know about my business?**
A: Through customization:
- **Basic**: System prompt tells the AI about your business
- **Premium**: Document training with your actual content/documents

**Q: Can I see conversation history?**
A: Analytics features are available. Contact support for access to conversation logs and statistics.

**Q: Can customers chat 24/7?**
A: Yes! The AI chatbot is available 24/7. There are no operating hours.

**Q: What if the bot can't answer a question?**
A: The bot will try its best, but if it's unsure, it can:
- Ask for clarification
- Suggest contacting you directly
- Provide general information

You can customize the system prompt to handle this better.

### Troubleshooting

**Q: The widget worked yesterday but stopped today - why?**
A: Possible causes:
1. Website code was changed/updated
2. Theme update removed the code
3. Browser cache needs clearing
4. Service maintenance (rare - you'll be notified)

Check the code is still in place and try clearing cache.

**Q: Can I test the widget before going live?**
A: Yes! Install it on a test/staging version of your site first. Or create a simple test HTML page with the code to test.

**Q: The widget works on desktop but not mobile - why?**
A: Check:
1. Mobile browser console for errors
2. Mobile internet connection
3. Try different mobile browsers
4. Clear mobile browser cache

**Q: I see "Powered by Snip" - can I remove it?**
A: Branding removal is a Premium feature. Basic plans include branding. Upgrade to Premium to remove it.

### Pricing & Plans

**Q: What's the difference between Basic and Premium?**
A: See the Pricing section, but main differences:
- **Basic**: Customization, branding included
- **Premium**: Document training (RAG), remove branding, priority support

**Q: Can I upgrade later?**
A: Yes! Contact support anytime to upgrade your plan.

**Q: What happens if I exceed my usage limits?**
A: Contact support. We'll work with you on usage and billing options.

**Q: Is there a free trial?**
A: This depends on your purchase. Check your welcome email or contact support.

### Support

**Q: How do I get help?**
A: 
1. Check this guide first (most questions are answered here)
2. Check the troubleshooting section
3. Contact support with your Client ID and description of issue

**Q: How quickly will I get a response?**
A: Response times vary:
- **Basic**: 24-48 hours
- **Premium**: Priority support, faster response

**Q: Do you offer setup assistance?**
A: Yes! Contact support and we can help with installation or configuration.

---

## Advanced Features {#advanced-features}

### Document Training (Premium Feature)

Train your bot with your own documents for more accurate, business-specific answers.

**Supported File Types:**
- PDF documents (`.pdf`)
- Word documents (`.doc`, `.docx`)
- Text files (`.txt`)
- Plain text

**How to Upload Documents:**

**Via API:**
```bash
curl -X POST https://snip-production.up.railway.app/api/documents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@/path/to/document.pdf"
```

**Via Support:**
- Email support with your Client ID and attached documents
- We'll upload and process them for you

**Processing Time:**
- Small documents (< 1MB): Usually processed in minutes
- Large documents (> 10MB): May take 10-30 minutes

**Document Limits:**
- **File Size**: Maximum 50MB per file
- **Total Documents**: Depends on your plan
- **Supported Languages**: Primarily English (others may work)

### Analytics & Usage Tracking

**Available Metrics:**
- Total conversations
- Messages per day/week/month
- Token usage
- Document query count (Premium)

**How to View Analytics:**

**Via API:**
```bash
curl https://snip-production.up.railway.app/api/usage \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response Example:**
```json
{
  "date": "2026-01-16",
  "message_count": 150,
  "token_count": 45000,
  "rag_query_count": 25
}
```

**Via Support:**
- Request usage reports via email
- Premium plans may have dashboard access

### Custom Domain Allowlisting

**What is it?**
Restrict widget to only load on specific domains (security feature).

**Why use it?**
- Prevents unauthorized use of your widget
- Ensures widget only appears on your legitimate websites
- Security best practice

**How to Set Up:**

**Via Configuration:**
```json
{
  "allowed_domains": [
    "yoursite.com",
    "www.yoursite.com",
    "shop.yoursite.com"
  ]
}
```

**Important Notes:**
- Include both `yoursite.com` and `www.yoursite.com` if you use both
- Include all subdomains where widget should appear
- Contact support if you need changes

---

## Support & Resources {#support}

### Getting Help

**Before Contacting Support:**

1. ✅ **Read this guide completely**
2. ✅ **Check the troubleshooting section**
3. ✅ **Test in different browser/device**
4. ✅ **Check browser console for errors** (F12 → Console)
5. ✅ **Clear browser cache** and try again

### When Contacting Support

**Include this information:**

1. **Your Client ID** (found in your embed code or welcome email)
2. **Description of issue** (what's happening vs. what should happen)
3. **Steps to reproduce** (what you did that caused the issue)
4. **Browser/device** (Chrome on Windows, Safari on iPhone, etc.)
5. **Screenshots** (if possible - helps us understand the issue)
6. **Error messages** (from browser console if applicable)

**Example Support Request:**
```
Subject: Widget Not Appearing on Mobile

Hi Support,

My widget isn't appearing on mobile devices:
- Client ID: 123e4567-e89b-12d3-a456-426614174000
- Issue: Widget button doesn't show on iPhone Safari
- Desktop works fine (Chrome, Firefox)
- Tried: Clearing cache, different browsers
- Browser console shows: [paste any errors]

Can you help?

Thanks!
```

### Support Channels

**Email Support:**
- Check your welcome email for support contact
- Include Client ID in subject line for faster response

**Response Times:**
- **Basic Plan**: 24-48 hours
- **Premium Plan**: Priority support (faster response)

### Additional Resources

**API Documentation:**
- Visit: `https://snip-production.up.railway.app/docs`
- Interactive API documentation (Swagger UI)
- Try API endpoints directly from browser

**Testing Tools:**
- **Browser DevTools**: Built into Chrome, Firefox, Safari (F12)
- **Postman**: For testing API calls (advanced users)
- **cURL**: Command-line tool for API testing

### Community & Updates

**Stay Updated:**
- Check your email for service updates
- Contact support for feature announcements
- Review API documentation for new endpoints

---

## Quick Reference Checklist

Use this checklist when setting up:

### Initial Setup
- [ ] Received welcome email with credentials
- [ ] Saved Client ID securely
- [ ] Saved API Key securely (never in website code!)
- [ ] Verified all credentials are correct

### Installation
- [ ] Copied widget embed code
- [ ] Replaced placeholder Client ID with actual ID
- [ ] Replaced placeholder Widget CDN URL
- [ ] Replaced placeholder API URL
- [ ] Added code to website (before `</body>` tag)
- [ ] Saved/published website changes

### Testing
- [ ] Widget appears on desktop browser
- [ ] Widget appears on mobile browser
- [ ] Chat opens when clicking widget
- [ ] Welcome message displays correctly
- [ ] Can send messages and receive responses
- [ ] Colors match your brand
- [ ] Logo appears (if configured)

### Configuration
- [ ] Customized bot name
- [ ] Set brand colors (hex format)
- [ ] Added welcome message
- [ ] Uploaded logo (if desired)
- [ ] Configured system prompt (if desired)

### Troubleshooting (if needed)
- [ ] Checked code placement (before `</body>`)
- [ ] Verified Client ID is correct
- [ ] Verified Widget CDN URL is accessible
- [ ] Verified API URL is correct
- [ ] Cleared browser cache
- [ ] Tested in different browsers
- [ ] Checked browser console for errors

---

## Final Notes

### Remember

1. **Client ID** = Public (safe in website code)
2. **API Key** = Secret (never in website code!)
3. **Widget Code** = Goes before `</body>` tag
4. **Colors** = Must be hex format (`#RRGGBB`)
5. **Test Everything** = Before going live

### Success Indicators

You'll know everything is working when:
- ✅ Widget button appears on your website
- ✅ Clicking opens chat interface
- ✅ Colors match your brand
- ✅ AI responds to messages
- ✅ Widget works on desktop and mobile

### Need More Help?

If you've gone through this entire guide and still have issues:

1. **Double-check the troubleshooting section**
2. **Verify all credentials are correct**
3. **Contact support** with all relevant information

We're here to help you succeed! 🚀

---

## Appendix: Glossary

**API Key**: Secret key used for authentication when managing settings (not used in website code)

**Client ID**: Public identifier for your account (safe to use in website code)

**Widget**: The chat interface that appears on your website

**CDN**: Content Delivery Network - where the widget file is hosted

**API**: Application Programming Interface - the backend service that powers the chatbot

**Embed Code**: The HTML code you paste on your website

**Hex Color**: Color format using hexadecimal values (e.g., `#007bff`)

**UUID**: Universally Unique Identifier - the format of your Client ID

**CORS**: Cross-Origin Resource Sharing - security mechanism for web requests

**RAG**: Retrieval-Augmented Generation - using your documents to improve AI responses (Premium feature)

---

**Version**: 1.0  
**Last Updated**: January 2026  
**For**: Snip Chatbot Widget Service

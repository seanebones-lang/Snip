# Quick Reference Guide - Snip Chatbot

**Last Updated**: 2026-01-16  
**Version**: Enhanced Edition

---

## 🚀 Quick Start

### For Clients (Buyers)

1. **Get Your Credentials**
   - Client ID (for widget embed)
   - API Key (for dashboard access)

2. **Embed Widget**
   ```html
   <script 
     src="https://widget-sigma-sage.vercel.app/widget.js" 
     data-client-id="YOUR_CLIENT_ID"
     data-api-url="https://snip-production.up.railway.app"
     async>
   </script>
   ```

3. **Customize in Dashboard**
   - Login at: https://snip.mothership-ai.com
   - Navigate to "Branding" page
   - Customize colors, messages, widget size, position, theme, CSS

---

## 📋 Feature Reference

### Document Upload (Premium)

**Supported Formats** (8 total):
- PDF (`.pdf`)
- Word (`.docx`, `.doc`)
- Text (`.txt`)
- Markdown (`.md`, `.markdown`)
- HTML (`.html`, `.htm`)
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)

**Upload Limits**:
- **Maximum Size**: 500MB per file
- **Processing**: Asynchronous (large files may take 10-60 minutes)

**How to Upload**:
1. Go to Dashboard → Documents
2. Click "Upload Document"
3. Select file (up to 500MB)
4. Wait for processing (status updates automatically)

---

### Customization Options

#### Basic Customization
- **Bot Name**: Name shown in widget
- **Logo URL**: Your company logo
- **Colors**: Primary, Secondary, Background, Text
- **Welcome Message**: First message users see
- **Placeholder Text**: Input placeholder

#### Advanced Customization
- **Widget Width**: 200-800px (default: 380px)
- **Widget Height**: 300-1000px (default: 550px)
- **Position**: 5 options
  - Bottom Right (default)
  - Bottom Left
  - Top Right
  - Top Left
  - Center
- **Theme**: Auto, Light, Dark, Custom
- **Custom CSS**: Full CSS customization (10,000 chars)

#### Behavior
- **Auto Open**: Automatically open chat on page load
- **Show Branding**: Display "Powered by Snip" (Premium can hide)

---

### Voice Settings

**Available Voices**:
- Ara (Female, Natural) - Default
- Leo (Male, Natural)
- Rex (Male, Natural)
- Sal (Male, Natural)
- Eve (Female, Natural)

**How to Change**:
1. Dashboard → Branding
2. Scroll to "Voice Settings"
3. Select voice from dropdown
4. Save

---

### Dashboard Features

#### Test Chat
- **Location**: Dashboard → Test Chat
- **Purpose**: Test your bot before deploying
- **Features**: Live chat with audio toggle

#### Conversation Logs
- **Location**: Dashboard → Conversations
- **Purpose**: View all conversations
- **Features**: Search, filter, view full conversation history

#### FAQ Management
- **Location**: Dashboard → FAQs
- **Purpose**: Create/edit FAQs for your bot
- **Features**: Categories, priority, bulk management

#### Enhanced Analytics
- **Location**: Dashboard → Usage
- **Purpose**: Monitor bot performance
- **Features**: 
  - Popular questions
  - Growth trends
  - Peak day metrics
  - Daily breakdown

#### Document Management
- **Location**: Dashboard → Documents
- **Purpose**: Upload and manage training documents
- **Features**: 
  - Upload (8 formats, 500MB max)
  - View status
  - Delete documents

---

## 🔧 API Quick Reference

### Authentication
All API requests require API key in header:
```
X-API-Key: YOUR_API_KEY
```

### Key Endpoints

#### Get Configuration
```bash
GET /api/config
Headers: X-API-Key: YOUR_API_KEY
```

#### Update Configuration
```bash
PATCH /api/config
Headers: X-API-Key: YOUR_API_KEY
Body: {
  "bot_name": "My Bot",
  "widget_width": 400,
  "widget_height": 600,
  "custom_css": ".snip-chat { border-radius: 20px; }",
  "theme": "light"
}
```

#### Upload Document
```bash
POST /api/documents
Headers: X-API-Key: YOUR_API_KEY
Body: FormData with file
```

#### Get Usage
```bash
GET /api/usage?days=30
Headers: X-API-Key: YOUR_API_KEY
```

#### List Conversations
```bash
GET /api/conversations?limit=50
Headers: X-API-Key: YOUR_API_KEY
```

#### Manage FAQs
```bash
GET /api/faqs
POST /api/faqs
PATCH /api/faqs/{id}
DELETE /api/faqs/{id}
Headers: X-API-Key: YOUR_API_KEY
```

---

## 💡 Tips & Best Practices

### Document Upload
- **Best Formats**: PDF, DOCX for best text extraction
- **Large Files**: Upload during off-peak hours (processing takes time)
- **Multiple Documents**: Upload related documents for better context
- **File Size**: Keep under 100MB for faster processing

### Customization
- **Colors**: Use high contrast for accessibility
- **Widget Size**: Test on mobile (defaults work well)
- **Custom CSS**: Test thoroughly before deploying
- **Position**: Bottom-right is most common (best UX)

### RAG Training
- **Quality over Quantity**: Fewer, well-structured documents work better
- **Update Regularly**: Keep documents current
- **Categories**: Use document names to indicate categories
- **Test Questions**: Test with questions your users will ask

### Voice Settings
- **Ara (Default)**: Best for general use
- **Leo**: Good for professional/business
- **Test First**: Use Test Chat to hear different voices

---

## 🐛 Troubleshooting

### Widget Not Appearing
- Check Client ID is correct
- Verify script tag is correct
- Check browser console for errors
- Verify domain is allowed (if configured)

### Document Not Processing
- Check file size (max 500MB)
- Verify file format is supported
- Check document status in dashboard
- Large files may take 30-60 minutes

### Customization Not Working
- Clear browser cache
- Verify widget.js is latest version
- Check custom CSS for syntax errors
- Verify database migration completed

### Chat Not Responding
- Check API key is valid
- Verify client is active
- Check backend health: `/healthz`
- Review error logs

---

## 📞 Support

### Documentation
- **Complete Guide**: `BUYER_ONBOARDING_GUIDE.md`
- **Implementation**: `COMPLETE_SYSTEM_READY.md`
- **Migration**: `DATABASE_MIGRATION_NEEDED_CUSTOMIZATION.md`
- **Deployment**: `DEPLOYMENT_READY.md`

### API Documentation
- **Swagger UI**: https://snip-production.up.railway.app/docs
- **OpenAPI Schema**: https://snip-production.up.railway.app/openapi.json

---

## 🎯 Feature Checklist

### Basic Setup ✅
- [ ] Client account created
- [ ] API key saved securely
- [ ] Widget embedded on website
- [ ] Basic customization applied

### Advanced Setup ✅
- [ ] Documents uploaded (Premium)
- [ ] FAQs created
- [ ] Voice selected
- [ ] Advanced customization applied
- [ ] Test Chat verified

### Monitoring ✅
- [ ] Analytics dashboard checked
- [ ] Conversation logs reviewed
- [ ] Usage metrics monitored

---

**Quick Reference Version**: Enhanced Edition  
**Last Updated**: 2026-01-16

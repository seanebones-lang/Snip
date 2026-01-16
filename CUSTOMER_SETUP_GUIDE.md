# Complete Customer Setup Guide for Snip

This guide will walk you through creating a customer, getting their ID and API key, and setting up their widget.

## Prerequisites

- Your production API URL: `https://snip-production.up.railway.app`
- Access to a terminal/command line (curl or Postman)
- Your customer's email and company name

---

## Step 1: Create a New Customer

### Using curl (Command Line)

Run this command, replacing `customer@example.com` with the actual email and `Company Name` with the company name:

```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "company_name": "Company Name"
  }'
```

### Example with Real Data

```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acmecorp.com",
    "company_name": "Acme Corporation"
  }'
```

### Expected Response

You'll get back a JSON response like this:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "customer@example.com",
  "company_name": "Company Name",
  "api_key": "snip_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tier": "basic",
  "created_at": "2026-01-16T20:00:00Z"
}
```

### Important Information to Save

**SAVE THESE TWO VALUES:**

1. **Client ID**: The `id` field (UUID format)
   - Example: `123e4567-e89b-12d3-a456-426614174000`
   - This is used to configure the widget

2. **API Key**: The `api_key` field
   - Example: `snip_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - This is used to manage the client's settings via API
   - **Keep this secret!**

---

## Step 2: Configure Customer Settings (Optional but Recommended)

Set up branding, colors, and chatbot personality using the API key from Step 1.

### Update Widget Configuration

```bash
curl -X PATCH https://snip-production.up.railway.app/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -d '{
    "bot_name": "Support Bot",
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "welcome_message": "Hello! How can I help you today?",
    "system_prompt": "You are a helpful customer support assistant."
  }'
```

### Configuration Options

- `bot_name`: Name shown in the widget (default: "Chat Bot")
- `primary_color`: Main color for the widget (hex code, e.g., "#007bff")
- `secondary_color`: Secondary color (hex code)
- `welcome_message`: First message users see (text)
- `system_prompt`: Instructions for the AI personality (text)
- `logo_url`: URL to company logo image (optional)
- `allowed_domains`: List of domains where widget can load (optional, array of strings)

### Example Full Configuration

```bash
curl -X PATCH https://snip-production.up.railway.app/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer snip_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "bot_name": "Acme Support",
    "primary_color": "#FF6B35",
    "secondary_color": "#004E89",
    "welcome_message": "Welcome to Acme Corporation! I'\''m here to help with any questions.",
    "system_prompt": "You are a friendly and professional customer support assistant for Acme Corporation. Help customers with product questions, orders, and general inquiries.",
    "logo_url": "https://example.com/logo.png",
    "allowed_domains": ["acmecorp.com", "www.acmecorp.com"]
  }'
```

---

## Step 3: Get the Widget Embed Code

### Get Widget Configuration (Public Endpoint)

This endpoint doesn't require authentication - it uses the client ID:

```bash
curl https://snip-production.up.railway.app/api/widget/config/CLIENT_ID_HERE
```

**Replace `CLIENT_ID_HERE` with the actual client ID from Step 1.**

### Response

You'll get back the widget configuration:

```json
{
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "bot_name": "Acme Support",
  "primary_color": "#FF6B35",
  "secondary_color": "#004E89",
  "welcome_message": "Welcome to Acme Corporation!",
  "system_prompt": "...",
  "widget_cdn_url": "https://snip.yourdomain.com"
}
```

---

## Step 4: Generate the Widget Embed Code

### HTML Snippet for Customer Website

Have your customer add this HTML code to their website (usually in the `<head>` or before `</body>` tag):

```html
<script 
  src="YOUR_WIDGET_CDN_URL/widget.js" 
  data-client-id="CLIENT_ID_HERE"
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>
```

### Replace These Values:

1. `YOUR_WIDGET_CDN_URL` - The URL where your widget.js is hosted
   - If using Vercel/CDN: `https://your-widget-deployment.vercel.app`
   - If using your own CDN: `https://cdn.yourdomain.com`

2. `CLIENT_ID_HERE` - The client ID from Step 1

### Complete Example

```html
<script 
  src="https://your-widget.vercel.app/widget.js" 
  data-client-id="123e4567-e89b-12d3-a456-426614174000"
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>
```

---

## Step 5: Test the Widget

### Verify Widget Loads

1. Have your customer add the embed code to a test page
2. Open the page in a browser
3. You should see the chatbot widget appear (usually bottom-right corner)
4. Click the widget to open the chat interface
5. Send a test message to verify it's working

---

## Step 6: Managing Customer Settings (Ongoing)

### View Current Configuration

```bash
curl https://snip-production.up.railway.app/api/config \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

### View Client Information

```bash
curl https://snip-production.up.railway.app/api/clients/me \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

### Check Usage Statistics

```bash
curl https://snip-production.up.railway.app/api/usage \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

---

## Quick Reference: All Customer Data

For each customer, you need to save:

1. **Client ID** (UUID)
   - Used in: Widget embed code (`data-client-id`)
   - Found in: Response from `POST /api/clients`

2. **API Key** (starts with `snip_live_`)
   - Used in: All API calls that modify settings
   - Found in: Response from `POST /api/clients`
   - **Keep this secret - never share publicly!**

3. **Email**
   - Used for: Customer contact
   - Found in: Response from `POST /api/clients`

4. **Company Name**
   - Used for: Reference
   - Found in: Response from `POST /api/clients`

---

## Using Postman (GUI Alternative)

If you prefer a visual interface instead of command line:

1. **Create Customer:**
   - Method: POST
   - URL: `https://snip-production.up.railway.app/api/clients`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "email": "customer@example.com",
       "company_name": "Company Name"
     }
     ```

2. **Update Configuration:**
   - Method: PATCH
   - URL: `https://snip-production.up.railway.app/api/config`
   - Headers: 
     - `Content-Type: application/json`
     - `Authorization: Bearer YOUR_API_KEY`
   - Body (raw JSON): Configuration object (see Step 2)

---

## Troubleshooting

### Customer can't see the widget

- Verify the `data-client-id` in the embed code matches the actual client ID
- Check that `data-api-url` points to the correct production URL
- Ensure the widget.js file is accessible at the CDN URL
- Check browser console for JavaScript errors

### Configuration not updating

- Verify the API key is correct
- Check that you're using `PATCH` method (not POST or PUT)
- Ensure all required fields are included in the request

### Widget shows wrong colors/messages

- Configuration updates may take a moment to propagate
- Clear browser cache
- Verify the widget config endpoint returns updated values

---

## Example: Complete Customer Onboarding Workflow

Here's a complete example for onboarding a new customer:

```bash
# Step 1: Create the customer
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah@techstartup.io",
    "company_name": "TechStartup Inc"
  }' > customer_response.json

# Step 2: Extract client ID and API key (using jq if available)
CLIENT_ID=$(cat customer_response.json | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
API_KEY=$(cat customer_response.json | grep -o '"api_key":"[^"]*"' | cut -d'"' -f4)

echo "Client ID: $CLIENT_ID"
echo "API Key: $API_KEY"

# Step 3: Configure the widget
curl -X PATCH https://snip-production.up.railway.app/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "bot_name": "TechStartup Support",
    "primary_color": "#0066CC",
    "welcome_message": "Hi! Welcome to TechStartup. How can I help?",
    "system_prompt": "You are a helpful support assistant for TechStartup Inc."
  }'

# Step 4: Provide embed code to customer
echo "Add this to your website:"
echo "<script src=\"YOUR_WIDGET_CDN_URL/widget.js\" data-client-id=\"$CLIENT_ID\" data-api-url=\"https://snip-production.up.railway.app\" async></script>"
```

---

## Security Notes

- **API Key Security**: Never expose API keys in public repositories or client-side code
- **API keys are for server-side use only** (managing settings)
- **Client IDs can be public** (they're used in the widget embed code)
- Use HTTPS for all API requests in production
- Consider rate limiting for production deployments

---

## Support

For issues or questions:
- Check the API documentation: `https://snip-production.up.railway.app/docs`
- Review error responses from API calls
- Verify all required environment variables are set

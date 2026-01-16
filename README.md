# Snip - Embeddable Chatbot Snippet Service

Turn your AI chatbot into sellable "snippets" - embeddable widgets that clients can paste onto their websites with custom branding and optional RAG training.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Websites                        │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐                   │
│  │Client A │   │Client B │   │Client C │                   │
│  │ Website │   │ Website │   │ Website │                   │
│  └────┬────┘   └────┬────┘   └────┬────┘                   │
└───────┼─────────────┼─────────────┼─────────────────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │ Load widget.js
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Snip Infrastructure                       │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Widget CDN  │    │   Backend    │    │  Dashboard   │  │
│  │  (widget.js) │───▶│   (FastAPI)  │◀───│   (React)    │  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘  │
│                             │                               │
│                    ┌────────┴────────┐                     │
│                    ▼                 ▼                     │
│              ┌──────────┐     ┌──────────┐                 │
│              │PostgreSQL│     │ ChromaDB │                 │
│              │(clients, │     │ (vectors)│                 │
│              │ configs) │     │          │                 │
│              └──────────┘     └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Features

### For You (The Seller)
- Multi-tenant architecture - serve unlimited clients from one codebase
- Usage tracking per client for billing
- Easy client management via API

### For Your Clients
- **One-line installation** - paste a script tag, done
- **Full branding** - custom colors, logo, bot name, welcome message
- **Custom AI personality** - system prompt customization
- **Document training (Premium)** - upload PDFs/docs for RAG

## Project Structure

```
Snip/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py    # API endpoints
│   │   ├── models.py  # Database models
│   │   ├── schemas.py # Pydantic schemas
│   │   ├── auth.py    # API key authentication
│   │   ├── rag.py     # RAG pipeline
│   │   └── config.py  # Settings
│   └── requirements.txt
├── widget/            # Embeddable widget
│   ├── src/
│   │   └── widget.ts  # Widget source
│   └── package.json
├── dashboard/         # Client dashboard
│   ├── src/
│   │   ├── pages/     # Dashboard pages
│   │   └── components/
│   └── package.json
└── ARCHITECTURE.md    # Detailed diagrams
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- xAI API key (for Grok)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment config
cp env.example.txt .env
# Edit .env with your database URL and API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

### 2. Widget Setup

```bash
cd widget

# Install dependencies
npm install

# Build widget
npm run build

# The built widget.js will be in dist/
```

### 3. Dashboard Setup

```bash
cd dashboard

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Create Your First Client

```bash
# Create a client via API
curl -X POST http://localhost:8000/api/clients \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "company_name": "Test Company"}'

# Response includes API key (save this!)
# {
#   "id": "uuid-here",
#   "api_key": "snip_xxxxxxxx...",
#   ...
# }
```

### 5. Test the Widget

Add this to any HTML page:

```html
<script 
  src="http://localhost:5173/widget.js" 
  data-client-id="YOUR_CLIENT_ID"
  data-api-url="http://localhost:8000"
  async>
</script>
```

## API Endpoints

### Client Management
- `POST /api/clients` - Create new client (returns API key)
- `GET /api/clients/me` - Get current client info (requires API key)

### Configuration
- `GET /api/config` - Get client config (requires API key)
- `PATCH /api/config` - Update config (requires API key)
- `GET /api/widget/config/{client_id}` - Get widget config (public)

### Chat
- `POST /api/chat` - Send message (public, requires client_id)

### Documents (Premium)
- `POST /api/documents` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### Analytics
- `GET /api/usage` - Get usage stats
- `GET /api/embed-snippet` - Get embed code

## Deployment

### Backend (Railway/Render)
1. Push to GitHub
2. Connect to Railway/Render
3. Set environment variables
4. Deploy

### Widget (Vercel/CDN)
1. Build: `npm run build`
2. Deploy `dist/widget.js` to CDN
3. Update `WIDGET_CDN_URL` in backend

### Dashboard (Vercel)
1. Connect to Vercel
2. Set `VITE_API_URL` to backend URL
3. Deploy

## Pricing Tiers

| Feature | Basic | Premium |
|---------|-------|---------|
| Custom branding | ✓ | ✓ |
| Custom colors | ✓ | ✓ |
| Welcome message | ✓ | ✓ |
| System prompt | ✓ | ✓ |
| Document upload | ✗ | ✓ |
| RAG training | ✗ | ✓ |
| Remove branding | ✗ | ✓ |

## License

Copyright NextEleven Studios

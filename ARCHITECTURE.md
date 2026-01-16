# Snip - Architecture Overview

## System Architecture

```mermaid
flowchart TB
    subgraph clients [Client Websites]
        C1[Client A Site]
        C2[Client B Site]
        C3[Client C Site]
    end
    
    subgraph snip [Snip Infrastructure]
        Widget[widget.js CDN]
        API[Multi-tenant API]
        DB[(PostgreSQL)]
        Vector[(Vector DB)]
        Dashboard[Client Dashboard]
    end
    
    C1 & C2 & C3 -->|"Load widget"| Widget
    Widget -->|"API calls with client_id"| API
    API --> DB
    API -->|"RAG queries"| Vector
    Dashboard -->|"Configure"| DB
    Dashboard -->|"Upload docs"| Vector
```

## How It Works

### 1. Client Onboarding Flow

```mermaid
sequenceDiagram
    participant Client
    participant Dashboard
    participant API
    participant DB
    
    Client->>Dashboard: Sign up
    Dashboard->>API: Create account
    API->>DB: Store client + generate API key
    API-->>Dashboard: Return client_id
    Dashboard-->>Client: Show embed snippet
    
    Client->>Dashboard: Customize branding
    Dashboard->>API: Save config
    API->>DB: Store colors, logo, bot name
    
    Client->>Their Website: Paste snippet
    Note over Client,Their Website: Done! Bot is live
```

### 2. Chat Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Widget
    participant API
    participant DB
    participant VectorDB
    participant Grok
    
    User->>Widget: Types message
    Widget->>API: POST /chat {client_id, message}
    API->>DB: Load client config
    
    alt Premium Client with RAG
        API->>VectorDB: Search relevant docs
        VectorDB-->>API: Return context chunks
    end
    
    API->>Grok: Send message + context + system prompt
    Grok-->>API: AI response
    API-->>Widget: Return branded response
    Widget-->>User: Display message
```

### 3. Document Upload Flow (Premium)

```mermaid
sequenceDiagram
    participant Client
    participant Dashboard
    participant API
    participant Storage
    participant Embedder
    participant VectorDB
    
    Client->>Dashboard: Upload document
    Dashboard->>API: POST /documents
    API->>Storage: Save file
    API->>Embedder: Process document
    
    Note over Embedder: Chunk text into segments
    Note over Embedder: Generate embeddings
    
    Embedder->>VectorDB: Store with client namespace
    API-->>Dashboard: Upload complete
    Dashboard-->>Client: Document ready!
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Widget** | Vanilla JS (Vite build) | Embeddable script for client websites |
| **API** | FastAPI + Python | Multi-tenant backend |
| **Database** | PostgreSQL | Clients, configs, usage tracking |
| **Vector DB** | ChromaDB or Pinecone | Document embeddings for RAG |
| **AI Model** | xAI Grok 4.1 | Chat responses |
| **Dashboard** | React + TypeScript | Client configuration portal |
| **Hosting** | Vercel + Railway | Scalable deployment |

## Data Model

```mermaid
erDiagram
    CLIENTS {
        uuid id PK
        string api_key UK
        string email UK
        string company_name
        string tier
        timestamp created_at
    }
    
    CONFIGS {
        uuid id PK
        uuid client_id FK
        string bot_name
        string logo_url
        string primary_color
        string secondary_color
        text welcome_message
        text system_prompt
        json allowed_domains
    }
    
    DOCUMENTS {
        uuid id PK
        uuid client_id FK
        string filename
        string status
        int chunk_count
        timestamp created_at
    }
    
    USAGE {
        uuid id PK
        uuid client_id FK
        date date
        int message_count
        int token_count
    }
    
    CLIENTS ||--o| CONFIGS : has
    CLIENTS ||--o{ DOCUMENTS : uploads
    CLIENTS ||--o{ USAGE : tracks
```

## Tier Features

| Feature | Basic | Premium |
|---------|-------|---------|
| Custom bot name | ✓ | ✓ |
| Custom colors | ✓ | ✓ |
| Custom logo | ✓ | ✓ |
| Welcome message | ✓ | ✓ |
| System prompt customization | ✓ | ✓ |
| Document upload (RAG) | ✗ | ✓ |
| Priority support | ✗ | ✓ |
| Analytics dashboard | Basic | Advanced |

## Widget Embed Code

What clients paste on their website:

```html
<script 
  src="https://snip.yourdomain.com/widget.js" 
  data-client-id="abc123"
  async>
</script>
```

That's it - one line, and the branded chatbot appears on their site.

## Security Considerations

- API keys are hashed before storage
- Client IDs validated on every request
- Domain allowlisting prevents unauthorized usage
- Rate limiting per client
- Document uploads scanned and sanitized
- CORS configured per client's domains

"""
Snip - Multi-tenant Chatbot Snippet Service
Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
import os
import requests
from uuid import UUID

from .config import get_settings
from .database import get_db, init_db
from .models import Client, ClientConfig, Document, UsageRecord, TierEnum, DocumentStatus
from .schemas import (
    ClientCreate, ClientResponse, ClientWithApiKey,
    ConfigUpdate, ConfigResponse, WidgetConfig,
    ChatRequest, ChatResponse,
    DocumentResponse, DocumentList,
    UsageSummary, UsageResponse,
    EmbedSnippet
)
from .auth import (
    generate_api_key, hash_api_key,
    get_client_from_api_key, get_client_from_client_id
)

settings = get_settings()

app = FastAPI(
    title="Snip API",
    description="Multi-tenant chatbot snippet service",
    version="1.0.0"
)

# CORS - allow widget to load from any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    try:
        init_db()
    except Exception as e:
        # Log error but don't crash app - database might not be ready yet
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize database: {e}")
        # In production, you might want to fail fast, but this allows app to start


# ============== Health Check ==============

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "snip"}


# ============== Client Management ==============

@app.post("/api/clients", response_model=ClientWithApiKey)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new client account
    Returns the API key (only shown once!)
    """
    # Check if email already exists
    existing = db.query(Client).filter(Client.email == client_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate API key
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)
    
    # Create client
    client = Client(
        email=client_data.email,
        company_name=client_data.company_name,
        tier=client_data.tier,
        api_key=api_key[:16] + "...",  # Store truncated version for display
        api_key_hash=api_key_hash
    )
    db.add(client)
    db.flush()
    
    # Create default config
    config = ClientConfig(
        client_id=client.id,
        bot_name=f"{client_data.company_name} Assistant",
        welcome_message=f"Hello! Welcome to {client_data.company_name}. How can I help you today?"
    )
    db.add(config)
    
    db.commit()
    db.refresh(client)
    
    # Return with full API key (only time it's shown)
    return ClientWithApiKey(
        id=client.id,
        email=client.email,
        company_name=client.company_name,
        tier=client.tier,
        is_active=client.is_active,
        created_at=client.created_at,
        api_key=api_key  # Full key returned only on creation
    )


@app.get("/api/clients/me", response_model=ClientResponse)
async def get_current_client(
    client: Client = Depends(get_client_from_api_key)
):
    """Get current client info (requires API key)"""
    return client


# ============== Configuration ==============

@app.get("/api/config", response_model=ConfigResponse)
async def get_config(
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Get client configuration (requires API key)"""
    if not client.config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    # Use from_orm to hide actual API key
    return ConfigResponse.from_orm(client.config)


@app.patch("/api/config", response_model=ConfigResponse)
async def update_config(
    config_data: ConfigUpdate,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Update client configuration (requires API key)"""
    if not client.config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    # Update only provided fields
    update_data = config_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client.config, field, value)
    
    db.commit()
    db.refresh(client.config)
    
    # Use from_orm to hide actual API key
    return ConfigResponse.from_orm(client.config)


@app.get("/api/widget/config/{client_id}", response_model=WidgetConfig)
async def get_widget_config(
    client_id: UUID,
    origin: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get widget configuration (public endpoint)
    Called by the embedded widget to get branding
    """
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.is_active == True
    ).first()
    
    if not client or not client.config:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check domain allowlist if configured
    config = client.config
    if config.allowed_domains and origin:
        # Extract domain from origin
        allowed = any(
            domain in origin 
            for domain in config.allowed_domains
        )
        if not allowed:
            raise HTTPException(status_code=403, detail="Domain not allowed")
    
    return WidgetConfig(
        botName=config.bot_name,
        logoUrl=config.logo_url,
        colors={
            "primary": config.primary_color,
            "secondary": config.secondary_color,
            "background": config.background_color,
            "text": config.text_color,
        },
        welcomeMessage=config.welcome_message,
        placeholderText=config.placeholder_text,
        position=config.position,
        autoOpen=config.auto_open,
        showBranding=config.show_branding,
    )


# ============== Chat Endpoint ==============

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Multi-tenant chat endpoint
    Called by widget with client_id
    """
    # Get client
    client = db.query(Client).filter(
        Client.id == request.client_id,
        Client.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    config = client.config
    if not config:
        raise HTTPException(status_code=500, detail="Client config missing")
    
    # Build system prompt with client customization
    base_prompt = f"""You are {config.bot_name}, an AI assistant for {client.company_name}.

{config.system_prompt or "Be helpful, friendly, and professional."}

Guidelines:
- Be concise and helpful
- Stay on topic for {client.company_name}
- If you don't know something, say so
"""
    
    # For premium clients with RAG, add document context
    rag_context = ""
    if client.tier == TierEnum.PREMIUM:
        try:
            from .rag import retrieve_context
            rag_context = await retrieve_context(client.id, request.message) or ""
            
            # Track RAG query
            if rag_context:
                today = date.today()
                usage = db.query(UsageRecord).filter(
                    UsageRecord.client_id == client.id,
                    UsageRecord.date == today
                ).first()
                if usage:
                    usage.rag_query_count += 1
        except Exception as e:
            print(f"RAG retrieval error: {e}")
            rag_context = ""
    
    if rag_context:
        base_prompt += f"""

RELEVANT CONTEXT FROM COMPANY DOCUMENTS:
{rag_context}

Use this context to answer questions when relevant.
"""
    
    # Get AI provider configuration - use client's settings if set, otherwise fallback to global
    api_key = None
    provider = None
    model = None
    
    # Check client's AI configuration first
    if config.ai_api_key:
        api_key = config.ai_api_key
        provider = config.ai_provider or 'xai'  # Default to xAI if not specified
        model = config.ai_model or 'grok-3-fast'  # Default model based on provider
    # Fallback to legacy xai_api_key if present
    elif hasattr(config, 'xai_api_key') and config.xai_api_key:
        api_key = config.xai_api_key
        provider = 'xai'
        model = 'grok-3-fast'
    # Fallback to global settings
    elif settings.xai_api_key:
        api_key = settings.xai_api_key
        provider = 'xai'
        model = 'grok-3-fast'
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="AI service not configured. Please add your AI API key in the dashboard settings."
        )
    
    # Normalize provider name
    provider = (provider or 'xai').lower()
    
    # Determine API endpoint and model defaults based on provider
    api_url = None
    default_models = {
        'xai': 'grok-3-fast',
        'openai': 'gpt-4',
        'anthropic': 'claude-3-opus-20240229'
    }
    
    if provider == 'xai':
        api_url = "https://api.x.ai/v1/chat/completions"
        model = model or default_models['xai']
    elif provider == 'openai':
        api_url = "https://api.openai.com/v1/chat/completions"
        model = model or default_models['openai']
    elif provider == 'anthropic':
        api_url = "https://api.anthropic.com/v1/messages"
        model = model or default_models['anthropic']
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported AI provider: {provider}. Supported providers: xai, openai, anthropic"
        )
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if provider == 'anthropic':
            # Anthropic uses a different API format
            payload = {
                "model": model,
                "max_tokens": 500,
                "system": base_prompt,
                "messages": [
                    {"role": "user", "content": request.message}
                ]
            }
            headers["x-api-key"] = api_key
            headers.pop("Authorization", None)
        else:
            # OpenAI and xAI use the same format
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": base_prompt},
                    {"role": "user", "content": request.message}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = "AI service error"
            try:
                error_data = response.json()
                error_detail = error_data.get("error", {}).get("message", error_detail)
            except:
                pass
            raise HTTPException(
                status_code=502,
                detail=error_detail
            )
        
        result = response.json()
        
        # Extract response text based on provider format
        if provider == 'anthropic':
            response_text = result["content"][0]["text"]
        else:
            response_text = result["choices"][0]["message"]["content"]
        
        # Track usage
        today = date.today()
        usage = db.query(UsageRecord).filter(
            UsageRecord.client_id == client.id,
            UsageRecord.date == today
        ).first()
        
        if not usage:
            usage = UsageRecord(client_id=client.id, date=today)
            db.add(usage)
        
        usage.message_count += 1
        # Estimate tokens (rough approximation)
        usage.token_count += len(request.message.split()) + len(response_text.split())
        
        db.commit()
        
        return ChatResponse(
            response=response_text,
            mood="neutral",
            sentiment_data={}
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Embed Snippet ==============

@app.get("/api/embed-snippet", response_model=EmbedSnippet)
async def get_embed_snippet(
    client: Client = Depends(get_client_from_api_key)
):
    """
    Get the embed snippet code for this client
    """
    snippet_html = f'''<script 
  src="{settings.widget_cdn_url}/widget.js" 
  data-client-id="{client.id}"
  async>
</script>'''
    
    return EmbedSnippet(
        html=snippet_html,
        script_url=f"{settings.widget_cdn_url}/widget.js",
        client_id=str(client.id)
    )


# ============== Documents (Premium) ==============

@app.post("/api/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Upload a document for RAG (Premium only)
    """
    # Check tier
    if client.tier != TierEnum.PREMIUM:
        raise HTTPException(
            status_code=403,
            detail="Document upload requires Premium tier"
        )
    
    # Validate file type
    allowed_types = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt"
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: PDF, DOCX, TXT"
        )
    
    # Read file
    contents = await file.read()
    file_size = len(contents)
    
    # Max 10MB
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    # Create document record
    doc = Document(
        client_id=client.id,
        filename=file.filename,
        file_type=allowed_types[file.content_type],
        file_size=file_size,
        status=DocumentStatus.PROCESSING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Process document (in production, this should be async/background job)
    try:
        from .rag import process_document
        chunk_count = await process_document(
            client_id=client.id,
            doc_id=doc.id,
            content=contents,
            file_type=allowed_types[file.content_type],
            filename=file.filename
        )
        doc.status = DocumentStatus.COMPLETED
        doc.chunk_count = chunk_count
        doc.processed_at = datetime.utcnow()
    except Exception as e:
        doc.status = DocumentStatus.FAILED
        doc.error_message = str(e)
    
    db.commit()
    db.refresh(doc)
    
    return doc


@app.get("/api/documents", response_model=DocumentList)
async def list_documents(
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """List all documents for this client"""
    docs = db.query(Document).filter(
        Document.client_id == client.id
    ).order_by(Document.created_at.desc()).all()
    
    return DocumentList(documents=docs, total=len(docs))


@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.client_id == client.id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from vector store
    try:
        from .rag import delete_document_embeddings
        await delete_document_embeddings(client.id, doc.id)
    except Exception as e:
        print(f"Failed to delete embeddings: {e}")
    
    db.delete(doc)
    db.commit()
    
    return {"status": "deleted"}


# ============== Usage Analytics ==============

@app.get("/api/usage", response_model=UsageSummary)
async def get_usage(
    days: int = 30,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Get usage statistics for the last N days"""
    from datetime import timedelta
    
    start_date = date.today() - timedelta(days=days)
    
    records = db.query(UsageRecord).filter(
        UsageRecord.client_id == client.id,
        UsageRecord.date >= start_date
    ).order_by(UsageRecord.date.desc()).all()
    
    total_messages = sum(r.message_count for r in records)
    total_tokens = sum(r.token_count for r in records)
    total_rag = sum(r.rag_query_count for r in records)
    
    daily = [
        UsageResponse(
            date=str(r.date),
            message_count=r.message_count,
            token_count=r.token_count,
            rag_query_count=r.rag_query_count
        )
        for r in records
    ]
    
    return UsageSummary(
        total_messages=total_messages,
        total_tokens=total_tokens,
        total_rag_queries=total_rag,
        daily_usage=daily
    )

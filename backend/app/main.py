"""
Snip - Multi-tenant Chatbot Snippet Service
Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
import os
import time
import requests
import httpx
import websockets
import json
import base64
import asyncio
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

# X.AI TTS Configuration
XAI_REALTIME_WS = "wss://api.x.ai/v1/realtime"
XAI_EPHEMERAL_TOKEN_ENDPOINT = "https://api.x.ai/v1/realtime/client_secrets"


async def get_xai_ephemeral_token(api_key: str) -> str:
    """
    Get ephemeral token for X.AI Grok Voice Agent API
    Uses the X.AI API key to get a short-lived token for WebSocket connection
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                XAI_EPHEMERAL_TOKEN_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={}  # Empty JSON body
            )
            response.raise_for_status()
            data = response.json()
            return data["value"]  # X.AI returns "value" not "token"
    except Exception as e:
        print(f"Failed to get X.AI ephemeral token: {e}")
        raise


async def generate_xai_tts_audio(text: str, api_key: str, voice: str = "Ara") -> Optional[bytes]:
    """
    Generate TTS audio using X.AI Grok Voice Agent API via WebSocket
    
    Args:
        text: Text to convert to speech
        api_key: X.AI API key
        voice: Voice name (Ara, Leo, Rex, Sal, Eve)
    
    Returns:
        Audio bytes (PCM format at 24kHz) or None if failed
    """
    try:
        # Step 1: Get ephemeral token
        token = await get_xai_ephemeral_token(api_key)
        
        # Step 2: Connect via WebSocket
        async with websockets.connect(
            XAI_REALTIME_WS,
            additional_headers={"Authorization": f"Bearer {token}"},
            ping_interval=20,
            ping_timeout=10
        ) as ws:
            
            # Step 3: Send session configuration
            session_update = {
                "type": "session.update",
                "session": {
                    "voice": voice,
                    "instructions": "You are a helpful voice assistant. Speak clearly and naturally.",
                    "audio": {
                        "input": {"format": {"type": "audio/pcm", "rate": 24000}},
                        "output": {"format": {"type": "audio/pcm", "rate": 24000}}
                    }
                }
            }
            await ws.send(json.dumps(session_update))
            
            # Wait for session.updated
            session_ready = False
            for _ in range(5):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    obj = json.loads(msg)
                    if obj.get("type") == "session.updated":
                        session_ready = True
                        print(f"[X.AI TTS] Session configured with voice: {voice}")
                        break
                except asyncio.TimeoutError:
                    continue
            
            if not session_ready:
                print(f"[X.AI TTS] Warning: Session update not confirmed")
            
            # Step 4: Create conversation item with text
            item_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": text}]
                }
            }
            await ws.send(json.dumps(item_message))
            print(f"[X.AI TTS] Sent text input: {text[:50]}...")
            
            # Wait for conversation.item.added
            item_added = False
            for _ in range(5):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    obj = json.loads(msg)
                    if obj.get("type") == "conversation.item.added":
                        item_added = True
                        break
                except asyncio.TimeoutError:
                    continue
            
            if not item_added:
                print(f"[X.AI TTS] Warning: Conversation item not confirmed")
            
            # Step 5: Create response to generate audio
            response_message = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            await ws.send(json.dumps(response_message))
            
            # Step 6: Collect audio deltas
            audio_chunks = []
            timeout = 30
            start_time = time.time()
            
            async for msg in ws:
                if time.time() - start_time > timeout:
                    print(f"[X.AI TTS] Timeout waiting for audio")
                    break
                
                try:
                    obj = json.loads(msg)
                    msg_type = obj.get("type")
                    
                    if msg_type == "response.output_audio.delta":
                        # Audio comes in delta field as base64
                        delta = obj.get("delta")
                        if delta:
                            audio_bytes = base64.b64decode(delta)
                            audio_chunks.append(audio_bytes)
                            print(f"[X.AI TTS] Received audio delta: {len(audio_bytes)} bytes")
                    
                    elif msg_type in ["response.output_audio.done", "response.done"]:
                        print(f"[X.AI TTS] Audio generation complete")
                        break
                    
                    elif msg_type == "error":
                        error_msg = obj.get("error", {}).get("message", "Unknown error")
                        print(f"[X.AI TTS] Error: {error_msg}")
                        break
                        
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"[X.AI TTS] Error processing message: {e}")
                    continue
            
            if audio_chunks:
                combined_audio = b"".join(audio_chunks)
                print(f"[X.AI TTS] Generated {len(combined_audio)} bytes of audio")
                return combined_audio
            else:
                print(f"[X.AI TTS] No audio chunks received")
                return None
                
    except Exception as e:
        print(f"[X.AI TTS] Failed to generate audio: {e}")
        import traceback
        traceback.print_exc()
        return None


def convert_pcm_to_wav(pcm_audio: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
    """
    Convert PCM audio to WAV format for browser playback
    """
    import struct
    
    # WAV header constants
    fmt_size = 16
    data_size = len(pcm_audio)
    file_size = 36 + data_size
    
    # Create WAV header
    header = b'RIFF'
    header += struct.pack('<I', file_size)
    header += b'WAVE'
    header += b'fmt '
    header += struct.pack('<I', fmt_size)
    header += struct.pack('<H', 1)  # PCM format
    header += struct.pack('<H', channels)
    header += struct.pack('<I', sample_rate)
    header += struct.pack('<I', sample_rate * channels * sample_width)  # byte rate
    header += struct.pack('<H', channels * sample_width)  # block align
    header += struct.pack('<H', sample_width * 8)  # bits per sample
    header += b'data'
    header += struct.pack('<I', data_size)
    
    return header + pcm_audio


app = FastAPI(
    title="Snip API",
    description="Multi-tenant chatbot snippet service",
    version="1.0.0"
)

# CORS - allow widget to load from any domain
# Note: allow_credentials=False because we use API keys in headers, not cookies
# Browsers don't allow allow_origins=["*"] with allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Fixed: Cannot use "*" with credentials=True
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Ensure all headers are exposed to clients
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
                    usage.rag_query_count = (usage.rag_query_count or 0) + 1
                    db.commit()
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
        'xai': 'grok-4-1-fast-non-reasoning',  # Updated to latest fast model
        'openai': 'gpt-4',
        'anthropic': 'claude-3-opus-20240229'
    }
    
    if provider == 'xai':
        # Note: Chat Completions endpoint is deprecated, Responses API is preferred
        # TODO: Migrate to /v1/responses endpoint for future-proofing
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
            usage = UsageRecord(
                client_id=client.id,
                date=today,
                message_count=0,
                token_count=0,
                rag_query_count=0
            )
            db.add(usage)
        
        usage.message_count = (usage.message_count or 0) + 1
        # Estimate tokens (rough approximation)
        usage.token_count = (usage.token_count or 0) + len(request.message.split()) + len(response_text.split())
        
        db.commit()
        
        # Generate TTS audio URL using X.AI Grok Voice Agent API
        audio_url = None
        try:
            # Only generate TTS if provider is xai (X.AI supports voice generation)
            if provider == 'xai' and api_key:
                print(f"[TTS] Generating audio for: {response_text[:50]}...")
                
                # Generate audio using X.AI Grok Voice Agent API
                pcm_audio = await generate_xai_tts_audio(
                    text=response_text,
                    api_key=api_key,
                    voice="Ara"  # Can be: Ara, Leo, Rex, Sal, Eve
                )
                
                if pcm_audio:
                    # Convert PCM to WAV for browser compatibility
                    wav_audio = convert_pcm_to_wav(pcm_audio)
                    
                    # Convert to base64 data URL
                    audio_base64 = base64.b64encode(wav_audio).decode('utf-8')
                    audio_url = f"data:audio/wav;base64,{audio_base64}"
                    print(f"[TTS] Successfully generated audio ({len(wav_audio)} bytes)")
                else:
                    print(f"[TTS] Failed to generate audio from X.AI")
            else:
                print(f"[TTS] Skipping TTS generation (provider: {provider})")
        except Exception as e:
            # TTS is optional - don't fail if it doesn't work
            print(f"[TTS] TTS generation failed (non-fatal): {e}")
            import traceback
            traceback.print_exc()
            audio_url = None
        
        return ChatResponse(
            response=response_text,
            mood="neutral",
            sentiment_data={},
            audio_url=audio_url
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
  data-api-url="https://snip-production.up.railway.app"
  async>
</script>'''
    
    return EmbedSnippet(
        html=snippet_html,
        script_url=f"{settings.widget_cdn_url}/widget.js",
        client_id=str(client.id)
    )


# ============== Documents (Premium) ==============

async def process_document_background(
    client_id: UUID,
    doc_id: UUID,
    content: bytes,
    file_type: str,
    filename: str
):
    """
    Background task to process document (runs on Railway)
    Updates document status when complete
    """
    from .database import SessionLocal
    from .rag import process_document
    
    # Get a new database session for background task
    db = SessionLocal()
    try:
        # Get document
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            print(f"[Background] Document {doc_id} not found")
            return
        
        # Update status to PROCESSING
        doc.status = DocumentStatus.PROCESSING
        db.commit()
        
        # Process document
        chunk_count = await process_document(
            client_id=client_id,
            doc_id=doc_id,
            content=content,
            file_type=file_type,
            filename=filename
        )
        
        # Update status to COMPLETED
        doc.status = DocumentStatus.COMPLETED
        doc.chunk_count = chunk_count
        doc.processed_at = datetime.utcnow()
        db.commit()
        
        print(f"[Background] Document {doc_id} processed successfully: {chunk_count} chunks")
        
    except Exception as e:
        # Update status to FAILED
        db.rollback()
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)
            db.commit()
        print(f"[Background] Document {doc_id} processing failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@app.post("/api/documents", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Upload a document for RAG (Premium only)
    Processing happens asynchronously on Railway
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
    
    # Create document record with PENDING status
    doc = Document(
        client_id=client.id,
        filename=file.filename,
        file_type=allowed_types[file.content_type],
        file_size=file_size,
        status=DocumentStatus.PENDING  # Start as PENDING, will update to PROCESSING -> COMPLETED
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Queue document for background processing on Railway
    background_tasks.add_task(
        process_document_background,
        client_id=client.id,
        doc_id=doc.id,
        content=contents,
        file_type=allowed_types[file.content_type],
        filename=file.filename
    )
    
    # Return immediately with PENDING status
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

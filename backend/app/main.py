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
import time
import threading
import requests
import httpx
import websockets
import json
import base64
import asyncio
from uuid import UUID

from .config import get_settings
from .database import get_db, init_db
from .models import Client, ClientConfig, Document, UsageRecord, TierEnum, DocumentStatus, Conversation, ConversationMessage, FAQ
from .schemas import (
    ClientCreate, ClientResponse, ClientWithApiKey,
    ConfigUpdate, ConfigResponse, WidgetConfig,
    ChatRequest, ChatResponse,
    DocumentResponse, DocumentList,
    UsageSummary, UsageResponse,
    EmbedSnippet,
    FAQCreate, FAQUpdate, FAQResponse, FAQList,
    ConversationResponse, ConversationList, MessageResponse
)
from .auth import (
    generate_api_key, hash_api_key,
    get_client_from_api_key, get_client_from_client_id
)
from .email import send_api_key_email
from .stripe_routes import router as stripe_router
from pydantic import BaseModel as PydanticBaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

# Per-client_id rate limit for /api/chat (Issue 6) - in-memory, 120/min per client
_chat_rate_cache: dict = {}
_chat_rate_lock = threading.Lock()
CHAT_RATE_LIMIT = 120
CHAT_RATE_WINDOW_SEC = 60.0


def _check_chat_rate_limit(client_id: UUID) -> bool:
    """Return True if allowed, False if over limit (120/min per client_id)."""
    now = time.time()
    key = str(client_id)
    with _chat_rate_lock:
        if key not in _chat_rate_cache:
            _chat_rate_cache[key] = []
        times = _chat_rate_cache[key]
        times[:] = [t for t in times if now - t < CHAT_RATE_WINDOW_SEC]
        if len(times) >= CHAT_RATE_LIMIT:
            return False
        times.append(now)
    return True


# TTS Configuration (Voice API endpoints)
TTS_REALTIME_WS = "wss://api.x.ai/v1/realtime"
TTS_EPHEMERAL_TOKEN_ENDPOINT = "https://api.x.ai/v1/realtime/client_secrets"


async def get_ephemeral_token(api_key: str, retries: int = 3) -> str:
    """
    Get ephemeral token for Voice API
    Uses API key to get a short-lived token for WebSocket connection
    Includes retry logic for resilience
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    TTS_EPHEMERAL_TOKEN_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={}  # Empty JSON body
                )
                response.raise_for_status()
                data = response.json()
                return data["value"]  # API returns "value" not "token"
        except httpx.TimeoutException as e:
            last_error = e
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 0.5  # Exponential backoff
                print(f"[TTS] Ephemeral token timeout (attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except httpx.HTTPStatusError as e:
            # Don't retry on auth errors (401/403) or client errors (4xx)
            if e.response.status_code in [401, 403, 400]:
                print(f"[TTS] Ephemeral token auth/client error: {e.response.status_code}")
                raise
            last_error = e
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 0.5
                print(f"[TTS] Ephemeral token HTTP error (attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 0.5
                print(f"[TTS] Ephemeral token error (attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
    
    # All retries exhausted
    print(f"[TTS] Failed to get ephemeral token after {retries} attempts: {last_error}")
    raise last_error or Exception("Failed to get ephemeral token")


async def generate_tts_audio(text: str, api_key: str, voice: str = "Ara") -> Optional[bytes]:
    """
    Generate TTS audio via WebSocket (Voice API)
    
    Args:
        text: Text to convert to speech
        api_key: API key for voice generation
        voice: Voice name (Ara, Leo, Rex, Sal, Eve)
    
    Returns:
        Audio bytes (PCM format at 24kHz) or None if failed
    """
    try:
        # Step 1: Get ephemeral token
        token = await get_ephemeral_token(api_key)
        
        # Step 2: Connect via WebSocket
        async with websockets.connect(
            TTS_REALTIME_WS,
            extra_headers={"Authorization": f"Bearer {token}"},
            ping_interval=20,
            ping_timeout=10
        ) as ws:
            
            # Step 3: Send session configuration
            # CRITICAL: Voice Agent is conversational (user says X → assistant says Y). We send our
            # bot's reply as "user" input and force repeat via instruction + message framing.
            session_update = {
                "type": "session.update",
                "session": {
                    "voice": voice,
                    "instructions": (
                        "You are a text-to-speech engine. The user will send a line that starts with "
                        "'SPEAK:' followed by the exact words to speak. Your ONLY output is to speak "
                        "those words—the part after 'SPEAK:'. Do not say 'SPEAK:' or anything else. "
                        "No greetings, no questions, no comment. Just the words after SPEAK:."
                    ),
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
                        print(f"[TTS] Session configured with voice: {voice}")
                        break
                except asyncio.TimeoutError:
                    continue
            
            if not session_ready:
                print(f"[TTS] Warning: Session update not confirmed")
            
            # Step 4: Send our bot's reply with SPEAK: prefix so the model speaks only the content
            # (Voice Agent has no true TTS-only mode; instruction says output = words after SPEAK:).
            tts_user_message = f"SPEAK: {text}"
            item_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": tts_user_message}]
                }
            }
            await ws.send(json.dumps(item_message))
            print(f"[TTS] Sent text input (say exactly): {text[:50]}...")
            
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
                print(f"[TTS] Warning: Conversation item not confirmed")
            
            # Step 5: Request audio only so the model doesn't "reply" in text first
            response_message = {
                "type": "response.create",
                "response": {
                    "modalities": ["audio"]
                }
            }
            await ws.send(json.dumps(response_message))
            
            # Step 6: Collect audio deltas
            audio_chunks = []
            timeout = 30
            start_time = time.time()
            
            async for msg in ws:
                if time.time() - start_time > timeout:
                    print(f"[TTS] Timeout waiting for audio")
                    break
                
                try:
                    obj = json.loads(msg)
                    msg_type = obj.get("type")
                    
                    if msg_type in ["response.output_audio.delta", "response.audio.delta"]:
                        # Audio comes in delta field as base64 (some APIs use "audio" instead)
                        delta = obj.get("delta") or obj.get("audio") or obj.get("data")
                        if isinstance(delta, str) and delta:
                            audio_bytes = base64.b64decode(delta)
                            audio_chunks.append(audio_bytes)
                            print(f"[TTS] Received audio delta: {len(audio_bytes)} bytes")
                    
                    elif msg_type in ["response.output_audio.done", "response.audio.done", "response.done"]:
                        print(f"[TTS] Audio generation complete")
                        break
                    
                    elif msg_type == "error":
                        error_msg = obj.get("error", {}).get("message", "Unknown error")
                        print(f"[TTS] Error: {error_msg}")
                        break
                        
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"[TTS] Error processing message: {e}")
                    continue
            
            if audio_chunks:
                combined_audio = b"".join(audio_chunks)
                print(f"[TTS] Generated {len(combined_audio)} bytes of audio")
                return combined_audio
            else:
                print(f"[TTS] No audio chunks received")
                return None
                
    except Exception as e:
        print(f"[TTS] Failed to generate audio: {e}")
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
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(stripe_router, prefix="/api", tags=["stripe"])

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

@app.get("/healthz/db")
async def healthz_db(db: Session = Depends(get_db)):
    """Database health check - verifies schema and migration status"""
    try:
        from sqlalchemy import text, inspect
        from .database import engine
        
        inspector = inspect(engine)
        
        # Check if client_configs table exists
        tables = inspector.get_table_names()
        has_client_configs = "client_configs" in tables
        
        # Check for required columns
        columns = {}
        if has_client_configs:
            cols = inspector.get_columns("client_configs")
            columns = {col["name"]: col["type"] for col in cols}
        
        required_columns = ["widget_width", "widget_height", "custom_css", "theme"]
        missing_columns = [col for col in required_columns if col not in columns]
        
        return {
            "status": "ok",
            "service": "snip",
            "database": {
                "connected": True,
                "tables": {"client_configs": has_client_configs},
                "columns": {
                    "exists": list(columns.keys()),
                    "required": required_columns,
                    "missing": missing_columns
                },
                "migration_status": "complete" if not missing_columns else "pending"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "snip",
            "database": {
                "connected": False,
                "error": str(e)
            }
        }


@app.get("/healthz/ready")
async def healthz_ready(db: Session = Depends(get_db)):
    """
    Readiness check: DB connection and optional external config presence.
    Returns 503 if DB unreachable; 200 with details for xAI/Resend/Stripe config.
    """
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not ready: {e}")
    checks = {
        "database": "ok",
        "xai_configured": bool(settings.xai_api_key),
        "resend_configured": bool(settings.resend_api_key),
        "stripe_configured": bool(settings.stripe_secret_key and settings.stripe_webhook_secret),
    }
    return {"status": "ready", "checks": checks}


# ============== Client Management ==============

@app.post("/api/clients", response_model=ClientWithApiKey, status_code=201)
@limiter.limit("30/minute")
async def create_client(
    request: Request,
    client_data: ClientCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new client account
    Returns the API key (only shown once!)
    """
    try:
        # Ensure database is initialized (run migration if needed)
        try:
            init_db()
        except Exception as migration_error:
            # Log but don't fail - migration might already be done
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Migration check warning: {migration_error}")
        
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
        
        # Create default config - only set required fields
        # Optional customization fields (widget_width, widget_height, custom_css, theme)
        # are nullable in the model and will default to NULL in the database
        config_data = {
            "client_id": client.id,
            "bot_name": f"{client_data.company_name} Assistant",
            "welcome_message": f"Hello! Welcome to {client_data.company_name}. How can I help you today?"
        }
        
        # Try to create config with minimal fields first
        # If migration hasn't run, these required fields should still work
        config = ClientConfig(**config_data)
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
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for duplicate email)
        raise
    except Exception as e:
        # Log the full error for debugging
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating client: {e}")
        logger.error(traceback.format_exc())
        
        # Return 500 with helpful error message
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create client: {str(e)}. Please check database migration status."
        )


class ResendApiKeyRequest(PydanticBaseModel):
    email: str


@app.post("/api/resend-api-key")
@limiter.limit("5/minute")
async def resend_api_key(
    request: Request,
    body: ResendApiKeyRequest,
    db: Session = Depends(get_db)
):
    """
    Request a new API key to be sent to the given email.
    If an account exists, a new key is generated, stored, and emailed.
    Same response whether or not account exists (avoids email enumeration).
    """
    from sqlalchemy import func
    email_lower = body.email.strip().lower()
    client = db.query(Client).filter(func.lower(Client.email) == email_lower).first()
    if not client:
        return {"status": "success", "message": "If an account exists for this email, a new API key has been sent."}
    if not client.is_active:
        return {"status": "success", "message": "If an account exists for this email, a new API key has been sent."}
    api_key = generate_api_key()
    client.api_key = api_key[:16] + "..."
    client.api_key_hash = hash_api_key(api_key)
    db.commit()
    tier_str = client.tier.value if hasattr(client.tier, "value") else str(client.tier)
    send_api_key_email(client.email, api_key, tier_str)
    return {"status": "success", "message": "If an account exists for this email, a new API key has been sent."}


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
    # Allow permanent demo client: lookup without is_active filter when client_id matches
    permanent_client_id = (settings.permanent_api_key_client_id or "").strip()
    if permanent_client_id and str(client_id) == permanent_client_id:
        client = db.query(Client).filter(Client.id == client_id).first()
    else:
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.is_active == True
        ).first()

    if not client or not client.config:
        raise HTTPException(status_code=404, detail="Client not found")

    # Gate: only active or grace-period subscriptions (Issue 1); skip for permanent demo client
    if not (permanent_client_id and str(client_id) == permanent_client_id):
        if not client.is_active:
            raise HTTPException(status_code=403, detail="Account inactive")
        if client.stripe_subscription_status and client.stripe_subscription_status.lower() not in ("active", "trialing", "past_due"):
            raise HTTPException(status_code=403, detail="Subscription not active")
    
    # Check domain allowlist; reject when allowlist set but no Origin (Issue 2)
    config = client.config
    origin_val = (origin or "").strip()
    if config.allowed_domains:
        if not origin_val:
            raise HTTPException(status_code=403, detail="Origin required")
        allowed = any(
            (d.strip() in origin_val) for d in config.allowed_domains if d and isinstance(d, str)
        )
        if not allowed:
            raise HTTPException(status_code=403, detail="Domain not allowed")
    
    # Use to_widget_config method which includes all new fields
    widget_config_dict = config.to_widget_config()
    return WidgetConfig(**widget_config_dict)


# ============== Chat Endpoint ==============

@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("120/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Multi-tenant chat endpoint
    Called by widget with client_id
    """
    # Allow permanent demo client: lookup without is_active filter when client_id matches
    permanent_client_id = (settings.permanent_api_key_client_id or "").strip()
    if permanent_client_id and str(body.client_id) == permanent_client_id:
        client = db.query(Client).filter(Client.id == body.client_id).first()
    else:
        client = db.query(Client).filter(
            Client.id == body.client_id,
            Client.is_active == True
        ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Gate: only active or grace-period subscriptions (Issue 1); skip for permanent demo client
    if not (permanent_client_id and str(body.client_id) == permanent_client_id):
        if not client.is_active:
            raise HTTPException(status_code=403, detail="Account inactive")
        if client.stripe_subscription_status and client.stripe_subscription_status.lower() not in ("active", "trialing", "past_due"):
            raise HTTPException(status_code=403, detail="Subscription not active")
    
    if not _check_chat_rate_limit(client.id):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    config = client.config
    if not config:
        raise HTTPException(status_code=500, detail="Client config missing")
    
    # Enforce allowed_domains if configured; reject when allowlist set but no Origin (Issue 2)
    origin = (request.headers.get("origin") or request.headers.get("referer") or "").strip()
    if config.allowed_domains:
        if not origin:
            raise HTTPException(status_code=403, detail="Origin required")
        allowed = any(
            (d.strip() in origin) for d in config.allowed_domains if d and isinstance(d, str)
        )
        if not allowed:
            raise HTTPException(status_code=403, detail="Domain not allowed")
    
    # Build system prompt with client customization
    base_prompt = f"""You are {config.bot_name}, an AI assistant for {client.company_name}.

{config.system_prompt or "Be helpful, friendly, and professional."}

Guidelines:
- Be concise and helpful
- Stay on topic for {client.company_name}
- If you don't know something, say so
"""
    
    # For standard+ clients with RAG, add document context
    rag_context = ""
    if client.tier != TierEnum.BASIC:
        try:
            from .rag import retrieve_context
            rag_context = await retrieve_context(client.id, body.message) or ""
            
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
    # White-labeled: Always use xAI in background, don't expose provider to clients
    api_key = None
    provider = 'xai'  # Always xAI for white-labeled solution
    model = None
    
    # Check client's AI configuration first (if they provided their own key)
    if config.ai_api_key:
        api_key = config.ai_api_key
        model = config.ai_model or 'grok-4-1-fast-non-reasoning'
    # Fallback to legacy xai_api_key if present
    elif hasattr(config, 'xai_api_key') and config.xai_api_key:
        api_key = config.xai_api_key
        model = 'grok-4-1-fast-non-reasoning'
    # Fallback to global settings (your xAI key)
    elif settings.xai_api_key:
        api_key = settings.xai_api_key
        model = 'grok-4-1-fast-non-reasoning'
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="AI service not configured. Please contact support."
        )
    
    # Always use xAI - white-labeled
    api_url = "https://api.x.ai/v1/chat/completions"
    model = model or 'grok-4-1-fast-non-reasoning'
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Always use xAI format (white-labeled)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": body.message}
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
        
        # Extract response text (always xAI format)
        response_text = result["choices"][0]["message"]["content"]
        
        # Store conversation (for conversation logs feature)
        try:
            # Create or get conversation (simplified: one per session, or create new)
            conversation = Conversation(
                client_id=client.id,
                started_at=datetime.utcnow(),
                last_message_at=datetime.utcnow(),
                message_count=2  # User + assistant
            )
            db.add(conversation)
            db.flush()
            
            # Store user message
            user_msg = ConversationMessage(
                conversation_id=conversation.id,
                role='user',
                content=body.message
            )
            db.add(user_msg)
            
            # Store assistant response
            assistant_msg = ConversationMessage(
                conversation_id=conversation.id,
                role='assistant',
                content=response_text
            )
            db.add(assistant_msg)
            
            db.commit()
        except Exception as e:
            # Don't fail chat if conversation logging fails
            print(f"[Conversation] Failed to store conversation: {e}")
            db.rollback()
        
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
        usage.token_count = (usage.token_count or 0) + len(body.message.split()) + len(response_text.split())
        
        db.commit()
        
        # Generate TTS audio URL (voice responses)
        audio_url = None
        try:
            # Generate voice audio (always available)
            if api_key:
                print(f"[TTS] Generating audio for: {response_text[:50]}...")
                
                # Generate audio using Voice API (white-labeled)
                # Voice options: Ara (default), Leo, Rex, Sal, Eve
                # Voice is configurable per-client via ClientConfig.tts_voice field
                voice = getattr(config, 'tts_voice', None) or os.getenv('XAI_TTS_VOICE', 'Ara')
                if voice not in ['Ara', 'Leo', 'Rex', 'Sal', 'Eve']:
                    voice = 'Ara'  # Fallback to safe default
                
                pcm_audio = await generate_tts_audio(
                    text=response_text,
                    api_key=api_key,
                    voice=voice
                )
                
                if pcm_audio:
                    # Convert PCM to WAV for browser compatibility
                    wav_audio = convert_pcm_to_wav(pcm_audio)
                    
                    # Convert to base64 data URL
                    audio_base64 = base64.b64encode(wav_audio).decode('utf-8')
                    audio_url = f"data:audio/wav;base64,{audio_base64}"
                    print(f"[TTS] Successfully generated audio ({len(wav_audio)} bytes)")
                else:
                    print(f"[TTS] Failed to generate audio")
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
  data-api-url="{settings.backend_public_url}"
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
    file: UploadFile = File(...),
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Upload a document for RAG (Standard+ only)
    Processing runs in-request so documents complete on Railway (BackgroundTasks
    often never run after response on PaaS, leaving docs stuck in PENDING).
    """
    # Check tier
    if client.tier == TierEnum.BASIC:
        raise HTTPException(
            status_code=403,
            detail="Document upload requires Standard or Premium tier"
        )
    
    # Validate file type - Support multiple formats
    allowed_types = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
        "text/markdown": "md",
        "text/x-markdown": "md",
        "text/html": "html",
        "text/csv": "csv",
        "text/comma-separated-values": "csv",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    }
    
    # Also check file extension if content-type not recognized
    file_ext_map = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'docx',  # Try to handle .doc files
        '.txt': 'txt',
        '.md': 'md',
        '.markdown': 'md',
        '.html': 'html',
        '.htm': 'html',
        '.csv': 'csv',
        '.xlsx': 'xlsx',
        '.xls': 'xls',
    }
    
    file_type = None
    if file.content_type in allowed_types:
        file_type = allowed_types[file.content_type]
    elif file.filename:
        # Try to determine from extension
        import os
        ext = os.path.splitext(file.filename.lower())[1]
        file_type = file_ext_map.get(ext)
    
    if not file_type:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Supported: PDF, DOCX, TXT, MD, HTML, CSV, XLSX, XLS"
        )
    
    # Read file
    contents = await file.read()
    file_size = len(contents)
    
    # Max 500MB; very large files are processed in-request and may timeout on Railway (Issue 5)
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large (max {MAX_FILE_SIZE // (1024*1024)}MB). "
                   "Large files are processed asynchronously and may take several minutes."
        )
    
    # Create document record and process in-request (so Railway actually runs it)
    doc = Document(
        client_id=client.id,
        filename=file.filename,
        file_type=file_type,
        file_size=file_size,
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    doc_id = doc.id
    print(f"[Documents] Created doc id={doc_id} filename={file.filename} size={file_size}")

    try:
        # Mark processing so we never leave PENDING if something fails before process_document
        doc.status = DocumentStatus.PROCESSING
        db.commit()
        db.refresh(doc)
        print(f"[Documents] Processing doc id={doc_id} ...")

        from .rag import process_document
        chunk_count = await process_document(
            client_id=client.id,
            doc_id=doc_id,
            content=contents,
            file_type=file_type,
            filename=file.filename,
        )
        doc.status = DocumentStatus.COMPLETED
        doc.chunk_count = chunk_count
        doc.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(doc)
        print(f"[Documents] Processed doc id={doc_id} filename={doc.filename} chunks={chunk_count}")
    except Exception as e:
        db.rollback()
        # Ensure doc is never left PENDING or PROCESSING; mark FAILED so UI shows error
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)[:500]
            db.commit()
            db.refresh(doc)
        print(f"[Documents] Failed doc id={doc_id} filename={file.filename}: {e}")
        import traceback
        traceback.print_exc()
        # Return doc so client gets 200 with failed status; UI can show error_message
        if not doc:
            raise HTTPException(status_code=500, detail=f"Document processing failed: {e}")

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


# ============== FAQ Management ==============

@app.post("/api/faqs", response_model=FAQResponse)
async def create_faq(
    faq_data: FAQCreate,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Create a new FAQ"""
    faq = FAQ(
        client_id=client.id,
        question=faq_data.question,
        answer=faq_data.answer,
        category=faq_data.category,
        priority=faq_data.priority
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@app.get("/api/faqs", response_model=FAQList)
async def list_faqs(
    category: Optional[str] = None,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """List all FAQs for this client"""
    query = db.query(FAQ).filter(FAQ.client_id == client.id)
    
    if category:
        query = query.filter(FAQ.category == category)
    
    faqs = query.order_by(FAQ.priority.desc(), FAQ.created_at.desc()).all()
    
    return FAQList(faqs=faqs, total=len(faqs))


@app.patch("/api/faqs/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: UUID,
    faq_data: FAQUpdate,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Update an existing FAQ"""
    faq = db.query(FAQ).filter(
        FAQ.id == faq_id,
        FAQ.client_id == client.id
    ).first()
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    update_data = faq_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)
    
    db.commit()
    db.refresh(faq)
    return faq


@app.delete("/api/faqs/{faq_id}")
async def delete_faq(
    faq_id: UUID,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Delete an FAQ"""
    faq = db.query(FAQ).filter(
        FAQ.id == faq_id,
        FAQ.client_id == client.id
    ).first()
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    db.delete(faq)
    db.commit()
    
    return {"status": "deleted"}


# ============== Conversation Logs ==============

@app.get("/api/conversations", response_model=ConversationList)
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """List conversations for this client"""
    conversations = db.query(Conversation).filter(
        Conversation.client_id == client.id
    ).order_by(Conversation.last_message_at.desc()).offset(offset).limit(limit).all()
    
    total = db.query(Conversation).filter(Conversation.client_id == client.id).count()
    
    # Load messages for each conversation
    for conv in conversations:
        conv.messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conv.id
        ).order_by(ConversationMessage.created_at).all()
    
    return ConversationList(conversations=conversations, total=total)


@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    client: Client = Depends(get_client_from_api_key),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.client_id == client.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Load messages
    conversation.messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation.id
    ).order_by(ConversationMessage.created_at).all()
    
    return conversation

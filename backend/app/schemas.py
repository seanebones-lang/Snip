"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .models import TierEnum, DocumentStatus


# ============== Client Schemas ==============

class ClientCreate(BaseModel):
    """Create a new client account"""
    email: EmailStr
    company_name: str = Field(..., min_length=1, max_length=255)
    tier: TierEnum = TierEnum.BASIC


class ClientResponse(BaseModel):
    """Client account response"""
    id: UUID
    email: str
    company_name: str
    tier: TierEnum
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClientWithApiKey(ClientResponse):
    """Client response including API key (only shown once on creation)"""
    api_key: str


# ============== Config Schemas ==============

class ColorsConfig(BaseModel):
    """Widget color configuration"""
    primary: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary: str = Field(default="#1E40AF", pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(default="#111827", pattern=r"^#[0-9A-Fa-f]{6}$")
    text: str = Field(default="#F3F4F6", pattern=r"^#[0-9A-Fa-f]{6}$")


class ConfigUpdate(BaseModel):
    """Update client configuration"""
    bot_name: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    background_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    text_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    welcome_message: Optional[str] = Field(None, max_length=1000)
    placeholder_text: Optional[str] = Field(None, max_length=255)
    system_prompt: Optional[str] = Field(None, max_length=5000)
    position: Optional[str] = Field(None, pattern=r"^(bottom-right|bottom-left|top-right|top-left|center)$")
    auto_open: Optional[bool] = None
    show_branding: Optional[bool] = None
    allowed_domains: Optional[List[str]] = None
    widget_width: Optional[int] = Field(None, ge=200, le=800, description="Widget width in pixels (200-800)")
    widget_height: Optional[int] = Field(None, ge=300, le=1000, description="Widget height in pixels (300-1000)")
    custom_css: Optional[str] = Field(None, max_length=10000, description="Custom CSS for advanced styling")
    theme: Optional[str] = Field(None, pattern=r"^(light|dark|auto|custom)$", description="Theme preset")
    ai_provider: Optional[str] = Field(None, description="AI provider: 'xai', 'openai', 'anthropic'")
    ai_api_key: Optional[str] = Field(None, description="Your AI API key (bring your own key)")
    ai_model: Optional[str] = Field(None, description="AI model to use (e.g., 'grok-3-fast', 'gpt-4', 'claude-3')")
    tts_voice: Optional[str] = Field(None, description="TTS voice for xAI: 'Ara', 'Leo', 'Rex', 'Sal', 'Eve' (default: 'Ara')")
    has_completed_onboarding: Optional[bool] = None


class ConfigResponse(BaseModel):
    """Client configuration response"""
    bot_name: str
    logo_url: Optional[str]
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    welcome_message: str
    placeholder_text: str
    system_prompt: Optional[str]
    position: str
    auto_open: bool
    show_branding: bool
    allowed_domains: List[str]
    widget_width: Optional[int] = None
    widget_height: Optional[int] = None
    custom_css: Optional[str] = None
    theme: Optional[str] = None
    ai_provider: Optional[str] = Field(None, description="AI provider selected")
    ai_model: Optional[str] = Field(None, description="AI model selected")
    ai_api_key_set: bool = Field(default=False, description="Whether AI API key is configured (never returns actual key)")
    tts_voice: Optional[str] = Field(None, description="TTS voice selected (only applies to xAI provider)")
    has_completed_onboarding: bool
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object, hiding actual API key"""
        data = obj.__dict__.copy()
        data['ai_api_key_set'] = bool(obj.ai_api_key) # Set flag based on key presence
        data.pop('ai_api_key', None) # Remove actual key from response
        # Handle legacy xai_api_key field if present
        if hasattr(obj, 'xai_api_key') and obj.xai_api_key and not obj.ai_api_key:
            data['ai_provider'] = data.get('ai_provider') or 'xai'
            data['ai_api_key_set'] = True
        data.pop('xai_api_key', None) # Remove legacy field if present
        return cls(**data)


class WidgetConfig(BaseModel):
    """Configuration sent to the widget (public-safe)"""
    botName: str
    logoUrl: Optional[str]
    colors: ColorsConfig
    welcomeMessage: str
    placeholderText: str
    position: str
    autoOpen: bool
    showBranding: bool
    width: Optional[int] = None
    height: Optional[int] = None
    customCss: Optional[str] = None
    theme: Optional[str] = None


# ============== Chat Schemas ==============

class ChatRequest(BaseModel):
    """Chat message from widget"""
    message: str = Field(..., min_length=1, max_length=4000)
    client_id: UUID


class ChatResponse(BaseModel):
    """Chat response to widget"""
    response: str
    mood: str = "neutral"
    sentiment_data: dict = {}
    audio_url: Optional[str] = None  # TTS audio URL


# ============== Document Schemas ==============

class DocumentResponse(BaseModel):
    """Document upload response"""
    id: UUID
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    chunk_count: int
    created_at: datetime
    processed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """List of documents"""
    documents: List[DocumentResponse]
    total: int


# ============== Usage Schemas ==============

class UsageResponse(BaseModel):
    """Usage statistics response"""
    date: str
    message_count: int
    token_count: int
    rag_query_count: int


class UsageSummary(BaseModel):
    """Usage summary for a period"""
    total_messages: int
    total_tokens: int
    total_rag_queries: int
    daily_usage: List[UsageResponse]


# ============== Embed Snippet Schema ==============

class EmbedSnippet(BaseModel):
    """Embed code for client website"""
    html: str
    script_url: str
    client_id: str


# ============== FAQ Schemas ==============

class FAQCreate(BaseModel):
    """Create a new FAQ"""
    question: str = Field(..., min_length=1, max_length=1000)
    answer: str = Field(..., min_length=1, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    priority: int = Field(default=0, ge=0)


class FAQUpdate(BaseModel):
    """Update an existing FAQ"""
    question: Optional[str] = Field(None, min_length=1, max_length=1000)
    answer: Optional[str] = Field(None, min_length=1, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=0)


class FAQResponse(BaseModel):
    """FAQ response"""
    id: UUID
    question: str
    answer: str
    category: Optional[str]
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FAQList(BaseModel):
    """List of FAQs"""
    faqs: List[FAQResponse]
    total: int


# ============== Conversation Schemas ==============

class MessageResponse(BaseModel):
    """Individual message in conversation"""
    id: UUID
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: UUID
    started_at: datetime
    last_message_at: datetime
    message_count: int
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    """List of conversations"""
    conversations: List[ConversationResponse]
    total: int

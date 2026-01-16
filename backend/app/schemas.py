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
    position: Optional[str] = Field(None, pattern=r"^(bottom-right|bottom-left)$")
    auto_open: Optional[bool] = None
    show_branding: Optional[bool] = None
    allowed_domains: Optional[List[str]] = None
    ai_provider: Optional[str] = Field(None, description="AI provider: 'xai', 'openai', 'anthropic'")
    ai_api_key: Optional[str] = Field(None, description="Your AI API key (bring your own key)")
    ai_model: Optional[str] = Field(None, description="AI model to use (e.g., 'grok-3-fast', 'gpt-4', 'claude-3')")


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
    ai_provider: Optional[str] = Field(None, description="AI provider selected")
    ai_model: Optional[str] = Field(None, description="AI model selected")
    ai_api_key_set: bool = Field(default=False, description="Whether AI API key is configured (never returns actual key)")
    
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

"""
Snip Database Models
SQLAlchemy models for clients, configs, documents, and usage tracking
"""
import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, Date, 
    ForeignKey, JSON, Boolean, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .database import Base


class TierEnum(str, enum.Enum):
    BASIC = "basic"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Client(Base):
    """
    Client/Customer accounts
    Each client gets their own branded chatbot instance
    """
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    api_key_hash = Column(String(128), nullable=False)  # Hashed version for verification
    
    # Account info
    email = Column(String(255), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    
    # Subscription
    tier = Column(SQLEnum(TierEnum), default=TierEnum.BASIC, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Stripe subscription fields
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_subscription_status = Column(String(50), default="active", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    config = relationship("ClientConfig", back_populates="client", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="client", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="client", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client {self.company_name} ({self.email})>"


class ClientConfig(Base):
    """
    Client branding and customization settings
    """
    __tablename__ = "client_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Branding
    bot_name = Column(String(100), default="Assistant", nullable=False)
    logo_url = Column(String(500), nullable=True)
    
    # Colors (hex values)
    primary_color = Column(String(7), default="#3B82F6", nullable=False)  # Blue
    secondary_color = Column(String(7), default="#1E40AF", nullable=False)  # Darker blue
    background_color = Column(String(7), default="#111827", nullable=False)  # Dark gray
    text_color = Column(String(7), default="#F3F4F6", nullable=False)  # Light gray
    
    # Messages
    welcome_message = Column(Text, default="Hello! How can I help you today?", nullable=False)
    placeholder_text = Column(String(255), default="Type your message...", nullable=False)
    
    # AI Customization
    system_prompt = Column(Text, nullable=True)  # Additional instructions for the AI
    
    # AI Provider Configuration (BYOK - Bring Your Own Key)
    ai_provider = Column(String(50), nullable=True)  # 'xai', 'openai', 'anthropic', etc.
    ai_api_key = Column(Text, nullable=True)  # Customer's own AI API key (encrypted)
    ai_model = Column(String(100), nullable=True)  # e.g., 'grok-3-fast', 'gpt-4', 'claude-3'
    
    # TTS Voice Configuration (xAI Grok Voice Agent)
    tts_voice = Column(String(20), nullable=True)  # 'Ara', 'Leo', 'Rex', 'Sal', 'Eve' (default: 'Ara')
    
    # Widget behavior
    position = Column(String(20), default="bottom-right", nullable=False)  # bottom-right, bottom-left, top-right, top-left, center
    auto_open = Column(Boolean, default=False, nullable=False)
    show_branding = Column(Boolean, default=True, nullable=False)  # "Powered by Snip"
    
    # Advanced customization
    widget_width = Column(Integer, nullable=True)  # Custom width in pixels (default: 380px)
    widget_height = Column(Integer, nullable=True)  # Custom height in pixels (default: 550px)
    custom_css = Column(Text, nullable=True)  # Custom CSS for advanced styling
    theme = Column(String(50), nullable=True)  # Theme preset: 'light', 'dark', 'auto', 'custom'
    
    # Onboarding
    has_completed_onboarding = Column(Boolean, default=False, nullable=False)
    
    # Security
    allowed_domains = Column(JSON, default=list, nullable=False)  # List of domains where widget can load
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    client = relationship("Client", back_populates="config")
    
    def __repr__(self):
        return f"<ClientConfig for {self.client_id}>"
    
    def to_widget_config(self) -> dict:
        """Return config formatted for the widget"""
        return {
            "botName": self.bot_name,
            "logoUrl": self.logo_url,
            "colors": {
                "primary": self.primary_color,
                "secondary": self.secondary_color,
                "background": self.background_color,
                "text": self.text_color,
            },
            "welcomeMessage": self.welcome_message,
            "placeholderText": self.placeholder_text,
            "position": self.position,
            "autoOpen": self.auto_open,
            "showBranding": self.show_branding,
            "width": self.widget_width,
            "height": self.widget_height,
            "customCss": self.custom_css,
            "theme": self.theme or "auto",
        }


class Document(Base):
    """
    Documents uploaded by premium clients for RAG
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File info
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, md, html, csv, xlsx, xls
    file_size = Column(Integer, nullable=False)  # bytes
    
    # Processing status
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    chunk_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationship
    client = relationship("Client", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.filename} ({self.status.value})>"


class UsageRecord(Base):
    """
    Daily usage tracking for billing and analytics
    """
    __tablename__ = "usage_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Date for this record
    date = Column(Date, default=date.today, nullable=False, index=True)
    
    # Metrics
    message_count = Column(Integer, default=0, nullable=False)
    token_count = Column(Integer, default=0, nullable=False)
    rag_query_count = Column(Integer, default=0, nullable=False)
    
    # Relationship
    client = relationship("Client", back_populates="usage_records")
    
    class Meta:
        # Unique constraint on client_id + date
        __table_args__ = (
            {"postgresql_concurrently": True}
        )
    
    def __repr__(self):
        return f"<UsageRecord {self.client_id} on {self.date}>"


class Conversation(Base):
    """
    Conversation threads between users and chatbot
    """
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Conversation metadata
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_message_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    
    # Optional: User identifier (if tracking specific users)
    user_id = Column(String(255), nullable=True, index=True)
    
    # Relationship
    client = relationship("Client", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationMessage.created_at")
    
    def __repr__(self):
        return f"<Conversation {self.id} ({self.message_count} messages)>"


class ConversationMessage(Base):
    """
    Individual messages within a conversation
    """
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<ConversationMessage {self.role}: {self.content[:50]}...>"


class FAQ(Base):
    """
    Frequently Asked Questions for clients
    """
    __tablename__ = "faqs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # FAQ content
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # Optional: Categories/tags
    category = Column(String(100), nullable=True)
    priority = Column(Integer, default=0, nullable=False)  # Higher = shown first
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    client = relationship("Client", back_populates="faqs")
    
    def __repr__(self):
        return f"<FAQ {self.question[:50]}...>"

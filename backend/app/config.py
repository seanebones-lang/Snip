"""
Snip Configuration
Environment variables and settings
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        case_sensitive=False,  # Match DATABASE_URL from Railway
    )
    
    # Database - Railway provides DATABASE_URL (Pydantic maps it via case_sensitive=False)
    database_url: str = "postgresql://localhost:5432/snip"
    
    # API Keys
    xai_api_key: str = ""
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_basic: str = ""
    stripe_price_id_standard: str = ""
    stripe_price_id_premium: str = ""
    stripe_price_id_enterprise: str = ""
    stripe_success_url: str = "https://snip.mothership-ai.com/success"
    stripe_cancel_url: str = "https://snip.mothership-ai.com/signup"
    
    # Email
    resend_api_key: str = ""
    
    # JWT Auth
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_data"
    
    # Widget CDN URL (where widget.js is hosted)
    widget_cdn_url: str = "https://widget-sigma-sage.vercel.app"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

"""
Snip Configuration
Environment variables and settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://localhost:5432/snip"
    
    # API Keys
    xai_api_key: str = ""
    
    # JWT Auth
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_data"
    
    # Widget CDN URL (where widget.js is hosted)
    widget_cdn_url: str = "https://snip.yourdomain.com"
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

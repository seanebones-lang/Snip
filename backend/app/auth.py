"""
Authentication utilities
API key generation, hashing, and validation
"""
import secrets
import hashlib
from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from sqlalchemy import func

from .config import get_settings
from .database import get_db
from .models import Client

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"snip_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed: str) -> bool:
    """Verify an API key against its hash"""
    return hash_api_key(api_key) == hashed


async def get_client_from_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Client:
    """
    Dependency to get client from API key
    Used for authenticated endpoints (dashboard)
    Permanent demo key: when PERMANENT_API_KEY matches, return client by PERMANENT_API_KEY_CLIENT_EMAIL with full access.
    """
    settings = get_settings()
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required"
        )

    # Permanent demo key bypass: exact key match → use designated client and grant full access
    if settings.permanent_api_key and api_key.strip() == settings.permanent_api_key.strip():
        email = (settings.permanent_api_key_client_email or "").strip().lower()
        if email:
            client = db.query(Client).filter(func.lower(Client.email) == email).first()
            if client:
                request.state.used_permanent_key = True
                return client
        # Fallback: look up by key hash without is_active so key can work even if client was deactivated
        key_hash = hash_api_key(api_key)
        client = db.query(Client).filter(Client.api_key_hash == key_hash).first()
        if client:
            request.state.used_permanent_key = True
            return client

    # Normal lookup: hash + is_active
    key_hash = hash_api_key(api_key)
    client = db.query(Client).filter(
        Client.api_key_hash == key_hash,
        Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return client


async def get_client_from_client_id(
    client_id: str,
    db: Session = Depends(get_db)
) -> Client:
    """
    Get client from client_id (UUID)
    Used for widget requests (public)
    """
    try:
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.is_active == True
        ).first()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid client ID format"
        )
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )
    
    return client

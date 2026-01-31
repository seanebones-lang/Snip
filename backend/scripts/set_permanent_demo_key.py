#!/usr/bin/env python3
"""
One-time script to make a demo API key permanent and grant full access.
Run with DATABASE_URL and PERMANENT_API_KEY and PERMANENT_API_KEY_CLIENT_EMAIL.

Example (from repo root):
  cd backend && DATABASE_URL="postgresql://..." \\
    PERMANENT_API_KEY="snip_jwdWgGJnpJPOwCSUuDksvnFFQOrEhayYii6Zlad_Voc" \\
    PERMANENT_API_KEY_CLIENT_EMAIL="your-demo@example.com" \\
    python -m scripts.set_permanent_demo_key

Prints the client_id to set as PERMANENT_API_KEY_CLIENT_ID in Railway (optional, for widget bypass).
"""
import os
import sys

# Add parent so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import func
from app.database import SessionLocal, init_db
from app.models import Client
from app.auth import hash_api_key


def main():
    key = (os.environ.get("PERMANENT_API_KEY") or "").strip()
    email = (os.environ.get("PERMANENT_API_KEY_CLIENT_EMAIL") or "").strip().lower()
    if not key or not email:
        print("Usage: PERMANENT_API_KEY=snip_... PERMANENT_API_KEY_CLIENT_EMAIL=you@example.com python -m scripts.set_permanent_demo_key")
        print("Set DATABASE_URL (e.g. from Railway) as well.")
        sys.exit(1)
    if not os.environ.get("DATABASE_URL"):
        print("DATABASE_URL is required.")
        sys.exit(1)

    init_db()
    db = SessionLocal()
    try:
        client = db.query(Client).filter(func.lower(Client.email) == email).first()
        if not client:
            print(f"No client found with email {email}")
            sys.exit(1)
        key_hash = hash_api_key(key)
        client.api_key = key[:16] + "..."
        client.api_key_hash = key_hash
        client.is_active = True
        client.stripe_subscription_status = "active"
        db.commit()
        print(f"Updated client {client.email}: api_key_hash set, is_active=True, stripe_subscription_status=active")
        print(f"Set in Railway (optional for widget bypass): PERMANENT_API_KEY_CLIENT_ID={client.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

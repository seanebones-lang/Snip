from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
import stripe
from stripe import webhooks
from .models import Client, ClientConfig, TierEnum
from .database import get_db
from sqlalchemy.orm import Session
from uuid import uuid4
from .auth import generate_api_key, hash_api_key
from .config import get_settings
from .email import send_api_key_email  # To be created

router = APIRouter()
settings = get_settings()

stripe.api_key = settings.stripe_secret_key

class CheckoutRequest(BaseModel):
    tier: str
    email: str
    company_name: str

@router.post("/api/checkout")
async def create_checkout_session(request: CheckoutRequest):
    """Create Stripe Checkout session for signup"""
    price_map = {
        "basic": settings.stripe_price_id_basic,
        "standard": settings.stripe_price_id_standard,
        "enterprise": settings.stripe_price_id_enterprise
    }
    
    if request.tier not in price_map:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_map[request.tier],
                "quantity": 1,
            }],
            mode="subscription",
            success_url=settings.stripe_success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.stripe_cancel_url,
            metadata={
                "tier": request.tier,
                "email": request.email,
                "company_name": request.company_name
            },
            customer_email=request.email
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        tier = metadata.get('tier')
        email = metadata.get('email') or session.get('customer_email')
        company_name = metadata.get('company_name')
        
        if not email or not company_name or not tier:
            return {"status": "missing_metadata"}
        
        # Check if email already exists
        existing = db.query(Client).filter(Client.email == email).first()
        if existing:
            # Upgrade existing client
            existing.tier = TierEnum[tier.upper()]
            existing.stripe_customer_id = session['customer']
            existing.stripe_subscription_id = session['subscription']
            existing.stripe_subscription_status = 'active'
            db.commit()
            send_api_key_email(existing.email, existing.api_key, tier)  # Send upgrade notice
        else:
            # Create new client
            api_key = generate_api_key()
            api_key_hash = hash_api_key(api_key)
            
            client = Client(
                email=email,
                company_name=company_name,
                tier=TierEnum[tier.upper()],
                api_key=api_key[:16] + "...",
                api_key_hash=api_key_hash,
                stripe_customer_id=session['customer'],
                stripe_subscription_id=session['subscription'],
                stripe_subscription_status='active'
            )
            db.add(client)
            db.flush()
            
            # Create default config
            config = ClientConfig(client_id=client.id)
            db.add(config)
            db.commit()
            
            # Send API key email
            send_api_key_email(email, api_key, tier)
        
        return {"status": "success"}
    
    return {"status": "ignored_event"}


# Mount to main app in main.py
# app.include_router(stripe_router, prefix="/api", tags=["stripe"])

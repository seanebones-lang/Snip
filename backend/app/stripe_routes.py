from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict
import stripe
from .models import Client, ClientConfig, TierEnum
from .database import get_db
from sqlalchemy.orm import Session
from uuid import uuid4
from .auth import generate_api_key, hash_api_key
from .config import get_settings
from .email import send_api_key_email

router = APIRouter()
settings = get_settings()

stripe.api_key = settings.stripe_secret_key

class CheckoutRequest(BaseModel):
    tier: str
    email: str
    company_name: str

@router.post("/api/checkout")
async def create_checkout_session(request: CheckoutRequest):
    tier = request.tier.strip().lower()
    if tier == "enterprise":
        tier = "premium"

    price_map = {
        "basic": settings.stripe_price_id_basic,
        "standard": settings.stripe_price_id_standard,
        "premium": settings.stripe_price_id_premium or settings.stripe_price_id_enterprise
    }
    
    if tier not in price_map or not price_map[tier]:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_map[tier],
                "quantity": 1,
            }],
            mode="subscription",
            success_url=settings.stripe_success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.stripe_cancel_url,
            metadata={
                "tier": tier,
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
        tier_str = (metadata.get('tier') or "").lower()
        email = metadata.get('email') or session.get('customer_email')
        company_name = metadata.get('company_name')

        if tier_str == "enterprise":
            tier_str = "premium"
        
        if not email or not company_name or not tier_str:
            return {"status": "missing_metadata"}

        if tier_str not in {"basic", "standard", "premium"}:
            return {"status": "invalid_tier"}
        
        tier = TierEnum[tier_str.upper()]
        
        # Check existing
        existing = db.query(Client).filter(Client.email == email).first()
        if existing:
            existing.tier = tier
            existing.stripe_customer_id = session['customer']
            existing.stripe_subscription_id = session['subscription']
            existing.stripe_subscription_status = 'active'
            db.commit()
            send_api_key_email(email, existing.api_key[:16] + " (upgraded)", tier_str)
        else:
            api_key = generate_api_key()
            api_key_hash = hash_api_key(api_key)
            
            client = Client(
                email=email,
                company_name=company_name,
                tier=tier,
                api_key=api_key[:16] + "...",
                api_key_hash=api_key_hash,
                stripe_customer_id=session['customer'],
                stripe_subscription_id=session['subscription'],
                stripe_subscription_status='active'
            )
            db.add(client)
            db.flush()
            
            config = ClientConfig(client_id=client.id)
            db.add(config)
            db.commit()
            
            send_api_key_email(email, api_key, tier_str)
        
        return {"status": "success"}
    
    return {"status": "ignored"}

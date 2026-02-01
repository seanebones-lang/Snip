from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict
import stripe
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Client, ClientConfig, TierEnum, ProcessedStripeEvent
from .database import get_db
from .auth import generate_api_key, hash_api_key
from .config import get_settings
from .email import send_api_key_email

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

stripe.api_key = settings.stripe_secret_key

class CheckoutRequest(BaseModel):
    tier: str
    email: str
    company_name: str

@router.post("/checkout")
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

@router.post("/webhooks/stripe")
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
    
    # Idempotency: skip duplicate events (Stripe retries)
    try:
        db.add(ProcessedStripeEvent(event_id=event["id"], processed_at=datetime.utcnow()))
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"status": "duplicate"}
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', '')
        metadata = session.get('metadata', {})
        tier_str = (metadata.get('tier') or "").lower()
        email = metadata.get('email') or session.get('customer_email')
        company_name = metadata.get('company_name')

        if tier_str == "enterprise":
            tier_str = "premium"
        
        if not tier_str:
            return {"status": "missing_metadata"}

        if tier_str not in {"basic", "standard", "premium"}:
            return {"status": "invalid_tier"}
        
        tier = TierEnum[tier_str.upper()]
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')
        
        # Match existing account by EMAIL only. Do not match by Stripe customer id:
        # Stripe can reuse the same customer (same browser/card) for a different signup,
        # which would incorrectly attach a new purchase to an existing account (same dashboard).
        existing = None
        if email:
            existing = db.query(Client).filter(Client.email == email).first()

        if existing:
            if not email:
                email = existing.email
            if not company_name:
                company_name = existing.company_name

            # Rotate key for upgrades so customer always has a valid key
            api_key = generate_api_key()
            api_key_hash = hash_api_key(api_key)

            existing.email = email
            if company_name:
                existing.company_name = company_name
            existing.tier = tier
            existing.api_key = api_key[:16] + "..."
            existing.api_key_hash = api_key_hash
            if stripe_customer_id:
                existing.stripe_customer_id = stripe_customer_id
            if stripe_subscription_id:
                existing.stripe_subscription_id = stripe_subscription_id
            existing.stripe_subscription_status = 'active'
            db.commit()
            email_ok = send_api_key_email(email, api_key, tier_str)
            if not email_ok:
                logger.warning("Stripe checkout.session.completed: API key email failed for session_id=%s email=%s", session_id, email)
                return {"status": "email_failed", "message": "Account created but API key email failed; check logs."}
            logger.info("Stripe checkout.session.completed: account updated and API key email sent session_id=%s email=%s", session_id, email)
        else:
            if not email or not company_name:
                return {"status": "missing_metadata"}

            api_key = generate_api_key()
            api_key_hash = hash_api_key(api_key)
            # If Stripe reused a customer id from another Snip account, don't store it on this new client (unique constraint)
            link_stripe_customer_id = stripe_customer_id
            if link_stripe_customer_id and db.query(Client).filter(Client.stripe_customer_id == link_stripe_customer_id).first():
                link_stripe_customer_id = None

            client = Client(
                email=email,
                company_name=company_name,
                tier=tier,
                api_key=api_key[:16] + "...",
                api_key_hash=api_key_hash,
                stripe_customer_id=link_stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_subscription_status='active'
            )
            db.add(client)
            db.flush()
            
            config = ClientConfig(client_id=client.id)
            db.add(config)
            db.commit()
            
            email_ok = send_api_key_email(email, api_key, tier_str)
            if not email_ok:
                return {"status": "email_failed", "message": "Account created but API key email failed; check logs."}
        
        return {"status": "success"}
    
    if event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        sub_id = sub.get("id")
        client = db.query(Client).filter(Client.stripe_subscription_id == sub_id).first()
        if client:
            client.stripe_subscription_status = "canceled"
            client.is_active = False
            db.commit()
        return {"status": "success"}
    
    if event["type"] == "customer.subscription.updated":
        sub = event["data"]["object"]
        sub_id = sub.get("id")
        status = (sub.get("status") or "active").lower()
        client = db.query(Client).filter(Client.stripe_subscription_id == sub_id).first()
        if client:
            client.stripe_subscription_status = status
            # Optionally sync tier from price
            items = sub.get("items", {}).get("data", [])
            if items and len(items) > 0:
                price_id = items[0].get("price", {}).get("id")
                if price_id:
                    if price_id == settings.stripe_price_id_basic:
                        client.tier = TierEnum.BASIC
                    elif price_id == settings.stripe_price_id_standard:
                        client.tier = TierEnum.STANDARD
                    elif price_id in (settings.stripe_price_id_premium or "", settings.stripe_price_id_enterprise or ""):
                        client.tier = TierEnum.PREMIUM
            db.commit()
        return {"status": "success"}
    
    if event["type"] == "invoice.payment_failed":
        inv = event["data"]["object"]
        sub_id = inv.get("subscription")
        if isinstance(sub_id, dict):
            sub_id = sub_id.get("id")
        if sub_id:
            client = db.query(Client).filter(Client.stripe_subscription_id == sub_id).first()
            if client:
                client.stripe_subscription_status = "past_due"
                db.commit()
        return {"status": "success"}
    
    return {"status": "ignored"}

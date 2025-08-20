from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
import os
from typing import Optional
import logging
from dotenv import load_dotenv
from core.config.settings import settings
from db.crud.credits import add_credits
from api.v1.endpoints.auth import get_email
from db.base import get_db
from sqlalchemy.orm import Session
from schemas.payment import PaymentIntentCreate, CustomerCreate, CheckoutSessionCreate,SubscriptionCreate
# Load environment variables
load_dotenv()

# Initialize FastAPI app
router = APIRouter()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
STRIPE_PUBLISHABLE_KEY = settings.STRIPE_PUBLISHABLE_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Dependency to verify Stripe webhook signature
async def verify_webhook_signature(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

# Get Stripe Configuration (useful for frontend)
@router.get("/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return {
        "publishable_key": STRIPE_PUBLISHABLE_KEY
    }
@router.post("/payments/create-intent")
async def create_payment_intent(payment_data: PaymentIntentCreate):
    """Create a payment intent for one-time payments"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=payment_data.amount,
            currency=payment_data.currency,
            customer=payment_data.customer_id,
            metadata=payment_data.metadata,
            automatic_payment_methods={"enabled": True}
        )
        
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "status": intent.status
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 2. Create Customer
@router.post("/customers/create")
async def create_customer(customer_data: CustomerCreate):
    """Create a new Stripe customer"""
    try:
        customer = stripe.Customer.create(
            email=customer_data.email,
            name=customer_data.name,
            metadata=customer_data.metadata
        )
        
        return {
            "customer_id": customer.id,
            "email": customer.email,
            "created": customer.created
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 3. Create Subscription
@router.post("/subscriptions/create")
async def create_subscription(subscription_data: SubscriptionCreate):
    """Create a new subscription for a customer"""
    try:
        subscription = stripe.Subscription.create(
            customer=subscription_data.customer_id,
            items=[{"price": subscription_data.price_id}],
            trial_period_days=subscription_data.trial_period_days,
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )
        
        response = {
            "subscription_id": subscription.id,
            "status": subscription.status
        }
        
        # Safely get client_secret if payment_intent exists
        if (hasattr(subscription, 'latest_invoice') and 
            hasattr(subscription.latest_invoice, 'payment_intent') and 
            subscription.latest_invoice.payment_intent is not None):
            response["client_secret"] = subscription.latest_invoice.payment_intent.client_secret
        
        return response
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 4. Get Payment Intent Status
@router.get("/payments/{payment_intent_id}/status")
async def get_payment_status(payment_intent_id: str):
    """Get the status of a payment intent"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            "payment_intent_id": intent.id,
            "status": intent.status,
            "amount": intent.amount,
            "currency": intent.currency
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=404, detail="Payment intent not found")

# 5. Cancel Subscription
@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: str):
    """Cancel a subscription"""
    try:
        subscription = stripe.Subscription.cancel(subscription_id)
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "canceled_at": subscription.canceled_at
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 6. Update Subscription
@router.put("/subscriptions/{subscription_id}")
async def update_subscription(subscription_id: str, price_id: str):
    """Update subscription to a new price"""
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription["items"]["data"][0].id,
                "price": price_id,
            }]
        )
        
        return {
            "subscription_id": updated_subscription.id,
            "status": updated_subscription.status,
            "current_period_end": updated_subscription.current_period_end
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 7. Get Customer Subscriptions
@router.get("/customers/{customer_id}/subscriptions")
async def get_customer_subscriptions(customer_id: str):
    """Get all subscriptions for a customer"""
    try:
        subscriptions = stripe.Subscription.list(customer=customer_id)
        
        return {
            "subscriptions": [
                {
                    "id": sub.id,
                    "status": sub.status,
                    "current_period_start": sub.current_period_start,
                    "current_period_end": sub.current_period_end,
                    "price_id": sub.items.data[0].price.id
                }
                for sub in subscriptions.data
            ]
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 8. Create Setup Intent (for saving payment methods)
@router.post("/payments/setup-intent")
async def create_setup_intent(customer_id: str):
    """Create a setup intent to save payment method for future use"""
    try:
        intent = stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=["card"],
        )
        
        return {
            "client_secret": intent.client_secret,
            "setup_intent_id": intent.id
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 9. Webhook Handler (Critical for production)
@router.post("/webhooks/stripe")
async def stripe_webhook(event = Depends(verify_webhook_signature)):
    """Handle Stripe webhooks"""
    try:
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"Payment succeeded: {payment_intent['id']}")
            # Add your business logic here (e.g., fulfill order, update database)
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.warning(f"Payment failed: {payment_intent['id']}")
            # Handle failed payment (e.g., notify user, retry logic)
            
        elif event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            logger.info(f"Subscription created: {subscription['id']}")
            # Handle new subscription (e.g., activate user account)
            
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            logger.info(f"Subscription updated: {subscription['id']}")
            # Handle subscription changes
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            logger.info(f"Subscription canceled: {subscription['id']}")
            # Handle subscription cancellation (e.g., revoke access)
            
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            logger.info(f"Invoice payment succeeded: {invoice['id']}")
            # Handle successful recurring payment
            
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            logger.warning(f"Invoice payment failed: {invoice['id']}")
            # Handle failed recurring payment (e.g., dunning management)
            
        else:
            logger.info(f"Unhandled event type: {event['type']}")
        
        return JSONResponse(content={"status": "success"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

# 10. Get Customer Portal Session (for self-service)
@router.post("/customers/{customer_id}/portal")
async def create_customer_portal_session(customer_id: str, return_url: str):
    """Create a customer portal session for self-service billing"""
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        
        return {"url": session.url}
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 11. Refund Payment
@router.post("/payments/{payment_intent_id}/refund")
async def refund_payment(payment_intent_id: str, amount: Optional[int] = None):
    """Refund a payment (full or partial)"""
    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=amount  # If None, refunds full amount
        )
        
        return {
            "refund_id": refund.id,
            "amount": refund.amount,
            "status": refund.status
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 12. Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "stripe-payment-api"}


@router.post("/checkout/create-session")
async def create_checkout_session(request: Request, checkout_data: CheckoutSessionCreate):
    """Create a Checkout Session that redirects to Stripe-hosted payment page"""
    try:
        email = get_email(request)
        session_params = {
            "success_url": checkout_data.success_url,
            "cancel_url": checkout_data.cancel_url,
            "mode": checkout_data.mode,
        }
        
        # Add customer email if provided
        if checkout_data.customer_email:
            session_params["customer_email"] = email
        
        # Configure based on payment mode
        if checkout_data.mode == "payment":
            # One-time payment
            if not checkout_data.amount:
                raise HTTPException(status_code=400, detail="Amount required for one-time payments")
            
            session_params["line_items"] = [{
                "price_data": {
                    "currency": checkout_data.currency,
                    "product_data": {
                        "name": "One-time Payment",
                    },
                    "unit_amount": checkout_data.amount,
                },
                "quantity": 1,
            }]
            
        elif checkout_data.mode == "subscription":
            # Subscription payment
            if not checkout_data.price_id:
                raise HTTPException(status_code=400, detail="Price ID required for subscriptions")
                
            session_params["line_items"] = [{
                "price": checkout_data.price_id,
                "quantity": 1,
            }]
        
        # Create the checkout session
        checkout_session = stripe.checkout.Session.create(**session_params)
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/checkout/session/{session_id}")
async def get_checkout_session(request: Request, session_id: str, db: Session = Depends(get_db)):
    """Get checkout session details and status"""
    email = get_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            # add 500 credits to user
            add_credits(500, email, db)
        return {
            "session_id": session.id,
            "payment_status": session.payment_status,
            "customer_email": session.customer_details.email if session.customer_details else None,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "payment_intent_id": session.payment_intent if session.payment_intent else None,
            "subscription_id": session.subscription if session.subscription else None
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=404, detail="Checkout session not found")



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
from pydantic import BaseModel
from typing import Optional

class PaymentIntentCreate(BaseModel):
    amount: int  # Amount in cents
    currency: str = "usd"
    customer_id: Optional[str] = None
    metadata: Optional[dict] = {}

class SubscriptionCreate(BaseModel):
    customer_id: str
    price_id: str  # Stripe price ID
    trial_period_days: Optional[int] = None

class CustomerCreate(BaseModel):
    email: str
    name: Optional[str] = None
    metadata: Optional[dict] = {}

class CheckoutSessionCreate(BaseModel):
    price_id: Optional[str] = None  # For subscriptions
    amount: Optional[int] = None  # For one-time payments (in cents)
    currency: str = "usd"
    customer_email: Optional[str] = None
    success_url: str
    cancel_url: str
    mode: str = "payment"  # "payment" for one-time, "subscription" for recurring
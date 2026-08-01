from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionOut(BaseModel):
    id: str
    org_id: str
    plan: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    created_at: datetime

    class Config:
        from_attributes = True

class InvoiceOut(BaseModel):
    id: str
    org_id: str
    amount: int
    currency: str
    status: str
    pdf_url: Optional[str]
    hosted_invoice_url: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True

class CheckoutSessionCreate(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class CheckoutSessionOut(BaseModel):
    url: str
    session_id: str

class PortalSessionCreate(BaseModel):
    return_url: str

class PortalSessionOut(BaseModel):
    url: str

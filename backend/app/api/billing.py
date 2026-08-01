from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
try:
    import stripe
except ImportError:
    stripe = None

from app.core.database import get_db
from app.core.config import get_settings
from app.models.subscription import Subscription, Invoice
from app.models.organization import Organization
from app.schemas.billing import SubscriptionOut, InvoiceOut, CheckoutSessionCreate, CheckoutSessionOut, PortalSessionCreate, PortalSessionOut

settings = get_settings()
router = APIRouter(prefix="/billing", tags=["billing"])

if settings.STRIPE_SECRET_KEY and stripe:
    stripe.api_key = settings.STRIPE_SECRET_KEY

@router.get("/subscription", response_model=SubscriptionOut)
async def get_subscription(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Subscription).where(Subscription.org_id == "default-org")
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")
    return sub

@router.get("/invoices", response_model=List[InvoiceOut])
async def list_invoices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Invoice).where(Invoice.org_id == "default-org").order_by(Invoice.created_at.desc())
    )
    return result.scalars().all()

@router.post("/checkout", response_model=CheckoutSessionOut)
async def create_checkout_session(data: CheckoutSessionCreate, db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY or not stripe:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    # Get or create Stripe customer
    result = await db.execute(
        select(Organization).where(Organization.id == "default-org")
    )
    org = result.scalar_one()

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": data.price_id, "quantity": 1}],
        mode="subscription",
        success_url=data.success_url,
        cancel_url=data.cancel_url,
        customer_email=org.name if "@" in org.name else None,
        metadata={"org_id": org.id},
    )

    return {"url": session.url, "session_id": session.id}

@router.post("/portal", response_model=PortalSessionOut)
async def create_portal_session(data: PortalSessionCreate, db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY or not stripe:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    result = await db.execute(
        select(Subscription).where(Subscription.org_id == "default-org")
    )
    sub = result.scalar_one_or_none()
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No Stripe customer found")

    session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=data.return_url,
    )

    return {"url": session.url}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        # Update or create invoice record
        db_invoice = Invoice(
            org_id="default-org",
            stripe_invoice_id=invoice["id"],
            amount=invoice["amount_due"],
            currency=invoice["currency"],
            status="paid",
            pdf_url=invoice.get("invoice_pdf"),
            hosted_invoice_url=invoice.get("hosted_invoice_url"),
        )
        db.add(db_invoice)
        await db.commit()

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription["id"])
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = subscription["status"]
            sub.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
            sub.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
            sub.cancel_at_period_end = subscription["cancel_at_period_end"]
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription["id"])
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = "canceled"
            sub.plan = "free"
            await db.commit()

    return {"received": True}

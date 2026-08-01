from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)

    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=True)

    plan = Column(String(50), default="free")  # free, pro, enterprise
    status = Column(String(50), default="active")  # active, canceled, past_due, trialing

    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)

    extra_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"), nullable=True)

    stripe_invoice_id = Column(String(255), nullable=True)
    amount = Column(Integer, default=0)  # cents
    currency = Column(String(10), default="usd")
    status = Column(String(50), default="draft")  # draft, open, paid, void, uncollectible

    pdf_url = Column(String(2048), nullable=True)
    hosted_invoice_url = Column(String(2048), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

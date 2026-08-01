from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrgSettings(BaseModel):
    auto_approve_threshold: int = 90
    human_review_threshold: int = 70
    block_threshold: int = 50
    test_weight: float = 0.40
    coverage_weight: float = 0.25
    security_weight: float = 0.20
    behavioral_weight: float = 0.15
    pii_entity_types: list[str] = [
        "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD",
        "US_SSN", "US_PASSPORT", "IBAN", "CRYPTO", "IP_ADDRESS"
    ]
    max_loop_iterations: int = 50
    context_bloat_threshold: int = 8000

class OrganizationCreate(BaseModel):
    name: str
    slug: str

class OrganizationOut(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    settings: dict
    created_at: datetime

    class Config:
        from_attributes = True

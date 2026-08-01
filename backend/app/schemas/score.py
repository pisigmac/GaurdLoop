from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScoreCreate(BaseModel):
    task_id: str
    test_results: dict = {}
    coverage_report: dict = {}
    security_scan: dict = {}
    behavioral_check: dict = {}

class ScoreOut(BaseModel):
    id: str
    task_id: str
    overall: int
    test_score: float
    coverage_score: float
    security_score: float
    behavioral_score: float
    weights: dict
    test_details: dict
    security_details: dict
    behavioral_details: dict
    decision: str
    override_by: Optional[str]
    override_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ScoreDecisionOverride(BaseModel):
    decision: str  # auto_approve, human_review, block
    reason: str

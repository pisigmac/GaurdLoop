from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PiiFinding(BaseModel):
    type: str
    start: int
    end: int
    confidence: float
    replacement: str

class PiiScanOut(BaseModel):
    id: str
    task_id: str
    raw_context_hash: str
    scrubbed_context_hash: str
    findings: List[PiiFinding]
    secrets_found: List[dict]
    blocked: bool
    block_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ContextScrubRequest(BaseModel):
    task_id: str
    context_text: str
    strict_mode: bool = False

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class WebhookIngest(BaseModel):
    source: str
    event_type: str
    payload: Dict[str, Any]
    signature: Optional[str] = None

class WebhookOut(BaseModel):
    id: str
    source: str
    event_type: str
    processed: bool
    task_id: Optional[str]
    received_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BrowserVerifyRequest(BaseModel):
    task_id: str
    url: str
    viewport_width: int = 1280
    viewport_height: int = 720
    baseline_screenshot_url: Optional[str] = None
    run_a11y: bool = True
    run_visual_regression: bool = True

class BrowserVerifyOut(BaseModel):
    id: str
    task_id: str
    url: str
    viewport: dict
    screenshots: List[dict]
    a11y_violations: List[dict]
    visual_regression_score: Optional[str]
    passed: bool
    failure_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

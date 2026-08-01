from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.browser_verify import BrowserVerify
from app.models.task import Task
from app.schemas.browser import BrowserVerifyRequest, BrowserVerifyOut
from app.services.browserverify import BrowserVerify

router = APIRouter(prefix="/browser", tags=["browser"])

@router.post("/verify")
async def verify_browser(
    data: BrowserVerifyRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == data.task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    verifier = BrowserVerify()

    # Run in background to avoid blocking
    async def run_verify():
        result = await verifier.verify(
            url=data.url,
            viewport={"width": data.viewport_width, "height": data.viewport_height},
            baseline_screenshot_path=data.baseline_screenshot_url,
            run_a11y=data.run_a11y,
            run_visual_regression=data.run_visual_regression,
        )

        verify_record = BrowserVerify(
            task_id=data.task_id,
            org_id=task.org_id,
            url=data.url,
            viewport={"width": data.viewport_width, "height": data.viewport_height},
            screenshots=result.screenshots,
            a11y_violations=result.a11y_violations,
            visual_regression_score=str(result.visual_regression_score) if result.visual_regression_score else None,
            passed=result.passed,
            failure_reason=result.failure_reason,
        )
        db.add(verify_record)
        await db.commit()

    background_tasks.add_task(run_verify)

    return {"status": "queued", "task_id": data.task_id, "url": data.url}

@router.get("/verifications/{task_id}", response_model=List[BrowserVerifyOut])
async def get_verifications(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BrowserVerify).where(BrowserVerify.task_id == task_id).order_by(BrowserVerify.created_at.desc())
    )
    return result.scalars().all()

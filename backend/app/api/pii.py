from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.pii_scan import PiiScan
from app.models.task import Task
from app.schemas.pii import PiiScanOut, ContextScrubRequest
from app.services.contextscrub import ContextScrub

router = APIRouter(prefix="/pii", tags=["pii"])

@router.post("/scrub")
async def scrub_context(data: ContextScrubRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == data.task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    scrubber = ContextScrub(strict_mode=data.strict_mode)
    result = scrubber.scrub(data.context_text)

    scan = PiiScan(
        task_id=data.task_id,
        org_id=task.org_id,
        raw_context_hash=scrubber._hash(data.context_text),
        scrubbed_context_hash=scrubber._hash(result.scrubbed_text),
        findings=result.findings,
        secrets_found=result.secrets_found,
        blocked=result.blocked,
        block_reason=result.block_reason,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # If blocked, update task
    if result.blocked:
        task.status = "blocked"
        task.error_log = f"PII/Secret block: {result.block_reason}"
        await db.commit()

    return {
        "scan_id": scan.id,
        "scrubbed_text": result.scrubbed_text,
        "findings_count": len(result.findings),
        "secrets_count": len(result.secrets_found),
        "blocked": result.blocked,
        "block_reason": result.block_reason,
    }

@router.get("/scans/{task_id}", response_model=List[PiiScanOut])
async def get_task_scans(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PiiScan).where(PiiScan.task_id == task_id).order_by(PiiScan.created_at.desc())
    )
    return result.scalars().all()

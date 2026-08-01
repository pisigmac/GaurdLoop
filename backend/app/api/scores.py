from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.score import Score
from app.schemas.score import ScoreOut, ScoreDecisionOverride

router = APIRouter(prefix="/scores", tags=["scores"])

@router.get("", response_model=List[ScoreOut])
async def list_scores(
    task_id: str = None,
    decision: str = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Score).where(Score.org_id == "default-org")
    if task_id:
        query = query.where(Score.task_id == task_id)
    if decision:
        query = query.where(Score.decision == decision)
    query = query.order_by(Score.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{score_id}", response_model=ScoreOut)
async def get_score(score_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Score).where(Score.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return score

@router.post("/{score_id}/override")
async def override_score(
    score_id: str,
    data: ScoreDecisionOverride,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Score).where(Score.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")

    score.decision = data.decision
    score.override_reason = data.reason
    score.override_by = "current-user"  # TODO: from auth

    await db.commit()
    await db.refresh(score)
    return score

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate, AgentOut

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("", response_model=AgentOut)
async def create_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    agent = Agent(
        org_id="default-org",
        name=data.name,
        agent_type=data.agent_type,
        config=data.config,
        extra_metadata=data.extra_metadata or {},
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.get("", response_model=List[AgentOut])
async def list_agents(
    agent_type: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Agent).where(Agent.org_id == "default-org")
    if agent_type:
        query = query.where(Agent.agent_type == agent_type)
    if status:
        query = query.where(Agent.status == status)

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: str,
    data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)
    return agent

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.delete(agent)
    await db.commit()
    return {"deleted": True}

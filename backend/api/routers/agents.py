"""Agent management endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.dependencies import get_current_active_user, get_organization_id
from api.utils.database import get_db
from api.models.user import User
from api.models.agent import Agent
from api.schemas.request.agent import AgentCreate, AgentUpdate
from api.schemas.response.agent import AgentResponse
from api.services.agent import AgentService

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    organization_id: str = Depends(get_organization_id),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new agent."""
    agent_service = AgentService(db)
    agent = await agent_service.create_agent(agent_data, organization_id)
    return agent


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """List all agents for the organization."""
    agent_service = AgentService(db)
    agents = await agent_service.list_agents(
        organization_id=organization_id,
        skip=skip,
        limit=limit
    )
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific agent."""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent(agent_id, organization_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """Update agent."""
    agent_service = AgentService(db)
    agent = await agent_service.update_agent(agent_id, organization_id, agent_update)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> None:
    """Delete agent."""
    agent_service = AgentService(db)
    success = await agent_service.delete_agent(agent_id, organization_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
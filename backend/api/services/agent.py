"""Agent service."""

from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import Session, select, func

from api.models.agent import Agent
from api.schemas.request.agent import AgentCreate, AgentUpdate
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class AgentService:
    """Agent service for AI agent management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_agent(
        self,
        agent_create: AgentCreate,
        organization_id: uuid.UUID
    ) -> Agent:
        """Create a new agent."""
        # Check if organization has reached agent limit
        from api.services.organization import OrganizationService
        org_service = OrganizationService(self.db)
        org = await org_service.get_by_id(organization_id)
        
        if org:
            agent_count = self.db.exec(
                select(func.count(Agent.id)).where(
                    Agent.organization_id == organization_id,
                    Agent.deleted_at == None
                )
            ).first()
            
            if agent_count >= org.max_agents:
                raise ValueError(f"Agent limit reached ({org.max_agents})")
        
        # Create agent
        agent = Agent(
            name=agent_create.name,
            description=agent_create.description,
            organization_id=organization_id,
            greeting_message=agent_create.greeting_message,
            voice_id=agent_create.voice_id,
            voice_speed=agent_create.voice_speed,
            voice_pitch=agent_create.voice_pitch,
            language=agent_create.language,
            ai_model=agent_create.ai_model,
            temperature=agent_create.temperature,
            max_tokens=agent_create.max_tokens,
            system_prompt=agent_create.system_prompt,
            personality_traits=agent_create.personality_traits or [],
            capabilities=agent_create.capabilities or {},
            restrictions=agent_create.restrictions or [],
            business_hours=agent_create.business_hours or {},
            out_of_hours_message=agent_create.out_of_hours_message,
            max_call_duration=agent_create.max_call_duration,
            call_recording_enabled=agent_create.call_recording_enabled,
            transcription_enabled=agent_create.transcription_enabled,
            sentiment_analysis_enabled=agent_create.sentiment_analysis_enabled,
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        logger.info(f"Agent created: {agent.name} for org {organization_id}")
        return agent
    
    async def get_agent(
        self,
        agent_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> Optional[Agent]:
        """Get agent by ID and organization."""
        statement = select(Agent).where(
            Agent.id == agent_id,
            Agent.organization_id == organization_id,
            Agent.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def get_by_phone_number(self, phone_number: str) -> Optional[Agent]:
        """Get agent by phone number."""
        statement = select(Agent).where(
            Agent.phone_number == phone_number,
            Agent.is_active == True,
            Agent.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def list_agents(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """List agents for organization."""
        statement = select(Agent).where(
            Agent.organization_id == organization_id,
            Agent.deleted_at == None
        ).offset(skip).limit(limit)
        
        return list(self.db.exec(statement).all())
    
    async def update_agent(
        self,
        agent_id: uuid.UUID,
        organization_id: uuid.UUID,
        agent_update: AgentUpdate
    ) -> Optional[Agent]:
        """Update agent."""
        agent = await self.get_agent(agent_id, organization_id)
        if not agent:
            return None
        
        # Update fields
        update_data = agent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.updated_at = datetime.utcnow()
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        logger.info(f"Agent updated: {agent.name}")
        return agent
    
    async def delete_agent(
        self,
        agent_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> bool:
        """Soft delete agent."""
        agent = await self.get_agent(agent_id, organization_id)
        if not agent:
            return False
        
        agent.soft_delete()
        agent.is_active = False
        
        self.db.add(agent)
        self.db.commit()
        
        logger.info(f"Agent deleted: {agent.name}")
        return True
    
    async def update_metrics(
        self,
        agent_id: uuid.UUID,
        duration: int,
        success: bool = True
    ) -> None:
        """Update agent metrics after call."""
        agent = self.db.get(Agent, agent_id)
        if not agent:
            return
        
        agent.total_calls += 1
        agent.total_minutes += duration // 60
        
        # Update average duration
        if agent.average_call_duration == 0:
            agent.average_call_duration = duration
        else:
            agent.average_call_duration = (
                (agent.average_call_duration * (agent.total_calls - 1) + duration) /
                agent.total_calls
            )
        
        # Update success rate
        if success:
            current_successful = int(agent.success_rate * (agent.total_calls - 1) / 100)
            agent.success_rate = ((current_successful + 1) / agent.total_calls) * 100
        else:
            current_successful = int(agent.success_rate * (agent.total_calls - 1) / 100)
            agent.success_rate = (current_successful / agent.total_calls) * 100
        
        self.db.add(agent)
        self.db.commit()
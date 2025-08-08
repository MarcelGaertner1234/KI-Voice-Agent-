"""Call service."""

from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import Session, select

from api.models.call import Call, CallTranscript, CallEvent
from api.schemas.request.call import CallCreate
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class CallService:
    """Call service for call management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_call(
        self,
        call_create: CallCreate,
        organization_id: uuid.UUID
    ) -> Call:
        """Create a new call record."""
        # Check organization limits
        from api.services.organization import OrganizationService
        org_service = OrganizationService(self.db)
        limit_check = await org_service.check_limits(organization_id)
        
        if not limit_check["allowed"]:
            raise ValueError(limit_check["reason"])
        
        # Create call
        call = Call(
            call_sid=call_create.call_sid,
            phone_number=call_create.phone_number,
            direction=call_create.direction,
            status="initiated",
            agent_id=call_create.agent_id,
            organization_id=organization_id,
            customer_id=call_create.customer_id,
        )
        
        self.db.add(call)
        self.db.commit()
        self.db.refresh(call)
        
        # Create initial event
        await self.add_event(call.id, "initiated", {"phone_number": call.phone_number})
        
        logger.info(f"Call created: {call.call_sid}")
        return call
    
    async def get_call(
        self,
        call_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> Optional[Call]:
        """Get call by ID and organization."""
        statement = select(Call).where(
            Call.id == call_id,
            Call.organization_id == organization_id,
            Call.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def get_by_sid(self, call_sid: str) -> Optional[Call]:
        """Get call by Twilio SID."""
        statement = select(Call).where(
            Call.call_sid == call_sid,
            Call.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def list_calls(
        self,
        organization_id: uuid.UUID,
        status: Optional[str] = None,
        agent_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Call]:
        """List calls with filtering."""
        statement = select(Call).where(
            Call.organization_id == organization_id,
            Call.deleted_at == None
        )
        
        if status:
            statement = statement.where(Call.status == status)
        
        if agent_id:
            statement = statement.where(Call.agent_id == agent_id)
        
        statement = statement.order_by(Call.started_at.desc()).offset(skip).limit(limit)
        
        return list(self.db.exec(statement).all())
    
    async def update_status(
        self,
        call_id: uuid.UUID,
        status: str,
        **kwargs
    ) -> Optional[Call]:
        """Update call status."""
        call = self.db.get(Call, call_id)
        if not call:
            return None
        
        call.status = status
        
        # Update timestamps based on status
        if status == "answered" and not call.answered_at:
            call.answered_at = datetime.utcnow()
        elif status in ["completed", "failed"] and not call.ended_at:
            call.ended_at = datetime.utcnow()
            if call.answered_at:
                call.duration = int((call.ended_at - call.answered_at).total_seconds())
        
        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(call, key):
                setattr(call, key, value)
        
        call.updated_at = datetime.utcnow()
        
        self.db.add(call)
        self.db.commit()
        
        # Add event
        await self.add_event(call_id, f"status_changed_{status}", kwargs)
        
        logger.info(f"Call status updated: {call.call_sid} -> {status}")
        return call
    
    async def end_call(
        self,
        call_id: uuid.UUID,
        organization_id: uuid.UUID,
        outcome: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Call]:
        """End an active call."""
        call = await self.get_call(call_id, organization_id)
        if not call:
            return None
        
        if call.status in ["completed", "failed"]:
            return call  # Already ended
        
        # Update call
        call.status = "completed"
        call.ended_at = datetime.utcnow()
        if call.answered_at:
            call.duration = int((call.ended_at - call.answered_at).total_seconds())
        
        if outcome:
            call.outcome = outcome
        if notes:
            call.notes = notes
        
        self.db.add(call)
        self.db.commit()
        
        # Update organization usage
        from api.services.organization import OrganizationService
        org_service = OrganizationService(self.db)
        await org_service.update_usage(
            organization_id,
            calls=1,
            minutes=call.duration // 60
        )
        
        # Update agent metrics
        from api.services.agent import AgentService
        agent_service = AgentService(self.db)
        await agent_service.update_metrics(
            call.agent_id,
            call.duration,
            success=outcome != "failed"
        )
        
        # Add event
        await self.add_event(call_id, "ended", {
            "duration": call.duration,
            "outcome": outcome
        })
        
        logger.info(f"Call ended: {call.call_sid}")
        return call
    
    async def add_transcript(
        self,
        call_id: uuid.UUID,
        speaker: str,
        text: str,
        timestamp: Optional[datetime] = None,
        start_time: float = 0.0,
        end_time: float = 0.0,
        metadata: Optional[dict] = None
    ) -> CallTranscript:
        """Add transcript message to call."""
        transcript = CallTranscript(
            call_id=call_id,
            speaker=speaker,
            text=text,
            timestamp=timestamp or datetime.utcnow(),
            start_time=start_time,
            end_time=end_time,
            confidence=metadata.get("confidence") if metadata else None,
            language=metadata.get("language") if metadata else None,
            intent=metadata.get("intent") if metadata else None,
            entities=metadata.get("entities", {}) if metadata else {},
        )
        
        self.db.add(transcript)
        self.db.commit()
        
        return transcript
    
    async def add_event(
        self,
        call_id: uuid.UUID,
        event_type: str,
        event_data: dict
    ) -> CallEvent:
        """Add event to call."""
        event = CallEvent(
            call_id=call_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.utcnow(),
        )
        
        self.db.add(event)
        self.db.commit()
        
        return event
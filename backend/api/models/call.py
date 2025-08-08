"""Call model."""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship
import uuid

from api.models.base import BaseModel


class Call(BaseModel, table=True):
    """Call record."""
    
    __tablename__ = "calls"
    
    # Call info
    call_sid: str = Field(unique=True, index=True)  # Twilio SID
    phone_number: str = Field(index=True)
    direction: str = Field(default="inbound")  # inbound/outbound
    status: str = Field(default="initiated", index=True)  # initiated/ringing/answered/completed/failed
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: int = Field(default=0)  # seconds
    
    # Recording
    recording_url: Optional[str] = None
    recording_duration: Optional[int] = None
    recording_status: Optional[str] = None
    
    # Transcription
    transcription_status: Optional[str] = None
    language_detected: Optional[str] = None
    
    # Analysis
    sentiment: Optional[str] = None  # positive/neutral/negative
    sentiment_score: Optional[float] = None
    keywords: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    topics: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Outcome
    outcome: Optional[str] = None  # appointment_booked/info_provided/transferred/etc
    outcome_details: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    notes: Optional[str] = None
    
    # Cost
    cost_amount: float = Field(default=0.0)
    cost_currency: str = Field(default="EUR")
    
    # Relations
    agent_id: uuid.UUID = Field(foreign_key="agents.id", index=True)
    agent: "Agent" = Relationship(back_populates="calls")
    
    customer_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="customers.id"
    )
    customer: Optional["Customer"] = Relationship(back_populates="calls")
    
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    
    # Nested relations
    transcripts: List["CallTranscript"] = Relationship(back_populates="call")
    events: List["CallEvent"] = Relationship(back_populates="call")
    
    class Config:
        validate_assignment = True


class CallTranscript(BaseModel, table=True):
    """Call transcript messages."""
    
    __tablename__ = "call_transcripts"
    
    # Message info
    speaker: str = Field(nullable=False)  # agent/customer/system
    text: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Audio timing
    start_time: float = Field(default=0.0)  # seconds from call start
    end_time: float = Field(default=0.0)
    
    # Analysis
    confidence: Optional[float] = None
    language: Optional[str] = None
    intent: Optional[str] = None
    entities: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Relations
    call_id: uuid.UUID = Field(foreign_key="calls.id", index=True)
    call: "Call" = Relationship(back_populates="transcripts")


class CallEvent(BaseModel, table=True):
    """Call events for tracking state changes."""
    
    __tablename__ = "call_events"
    
    event_type: str = Field(nullable=False)  # initiated/answered/ended/error/etc
    event_data: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relations
    call_id: uuid.UUID = Field(foreign_key="calls.id", index=True)
    call: "Call" = Relationship(back_populates="events")
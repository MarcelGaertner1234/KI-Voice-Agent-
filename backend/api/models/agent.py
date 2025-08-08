"""Agent model."""

from typing import Optional, List
from sqlmodel import Field, Relationship
import uuid

from api.models.base import BaseModel


class Agent(BaseModel, table=True):
    """AI Agent configuration."""
    
    __tablename__ = "agents"
    
    # Basic info
    name: str = Field(nullable=False, index=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    
    # Phone configuration
    phone_number: Optional[str] = Field(unique=True, index=True)
    greeting_message: str = Field(
        default="Guten Tag, hier ist Ihr KI-Assistent. Wie kann ich Ihnen helfen?"
    )
    
    # Voice settings
    voice_id: str = Field(default="de-DE-Standard-A")  # ElevenLabs voice ID
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    language: str = Field(default="de")
    
    # AI Configuration
    ai_model: str = Field(default="gpt-4-turbo-preview")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500)
    system_prompt: str = Field(nullable=False)
    
    # Behavior settings
    personality_traits: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    capabilities: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    restrictions: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Knowledge base
    knowledge_base_enabled: bool = Field(default=True)
    knowledge_base_ids: List[uuid.UUID] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Call handling
    max_call_duration: int = Field(default=600)  # seconds
    call_recording_enabled: bool = Field(default=True)
    transcription_enabled: bool = Field(default=True)
    sentiment_analysis_enabled: bool = Field(default=True)
    
    # Business rules
    business_hours: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    out_of_hours_message: Optional[str] = None
    holiday_dates: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Integration settings
    calendar_integration_enabled: bool = Field(default=False)
    calendar_id: Optional[str] = None
    crm_integration_enabled: bool = Field(default=False)
    crm_config: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Relations
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
    organization: "Organization" = Relationship(back_populates="agents")
    calls: List["Call"] = Relationship(back_populates="agent")
    
    # Metrics
    total_calls: int = Field(default=0)
    total_minutes: int = Field(default=0)
    average_call_duration: float = Field(default=0.0)
    success_rate: float = Field(default=0.0)


class AgentKnowledgeBase(BaseModel, table=True):
    """Knowledge base articles for agents."""
    
    __tablename__ = "agent_knowledge_bases"
    
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    category: Optional[str] = None
    tags: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Search optimization
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Metadata
    usage_count: int = Field(default=0)
    last_used_at: Optional[str] = None
    effectiveness_score: float = Field(default=0.0)
    
    # Relations
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
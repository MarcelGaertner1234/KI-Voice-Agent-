"""Agent response schemas."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import uuid


class AgentResponse(BaseModel):
    """Agent response."""
    id: uuid.UUID
    name: str
    description: Optional[str]
    is_active: bool
    phone_number: Optional[str]
    greeting_message: str
    voice_id: str
    voice_speed: float
    voice_pitch: float
    language: str
    ai_model: str
    temperature: float
    max_tokens: int
    system_prompt: str
    personality_traits: List[str]
    capabilities: dict
    restrictions: List[str]
    knowledge_base_enabled: bool
    max_call_duration: int
    call_recording_enabled: bool
    transcription_enabled: bool
    sentiment_analysis_enabled: bool
    business_hours: dict
    out_of_hours_message: Optional[str]
    total_calls: int
    total_minutes: int
    average_call_duration: float
    success_rate: float
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
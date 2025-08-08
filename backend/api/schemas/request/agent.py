"""Agent request schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    """Agent creation request."""
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    greeting_message: str = Field(
        default="Guten Tag, hier ist Ihr KI-Assistent. Wie kann ich Ihnen helfen?"
    )
    voice_id: str = Field(default="de-DE-Standard-A")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    language: str = Field(default="de")
    ai_model: str = Field(default="gpt-4-turbo-preview")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=50, le=2000)
    system_prompt: str
    personality_traits: Optional[List[str]] = None
    capabilities: Optional[dict] = None
    restrictions: Optional[List[str]] = None
    business_hours: Optional[dict] = None
    out_of_hours_message: Optional[str] = None
    max_call_duration: int = Field(default=600, ge=60, le=3600)
    call_recording_enabled: bool = Field(default=True)
    transcription_enabled: bool = Field(default=True)
    sentiment_analysis_enabled: bool = Field(default=True)


class AgentUpdate(BaseModel):
    """Agent update request."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    greeting_message: Optional[str] = None
    voice_id: Optional[str] = None
    voice_speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    voice_pitch: Optional[float] = Field(None, ge=0.5, le=2.0)
    language: Optional[str] = None
    ai_model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=50, le=2000)
    system_prompt: Optional[str] = None
    personality_traits: Optional[List[str]] = None
    capabilities: Optional[dict] = None
    restrictions: Optional[List[str]] = None
    business_hours: Optional[dict] = None
    out_of_hours_message: Optional[str] = None
    max_call_duration: Optional[int] = Field(None, ge=60, le=3600)
    call_recording_enabled: Optional[bool] = None
    transcription_enabled: Optional[bool] = None
    sentiment_analysis_enabled: Optional[bool] = None
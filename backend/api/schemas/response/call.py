"""Call response schemas."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import uuid


class CallTranscriptResponse(BaseModel):
    """Call transcript response."""
    id: uuid.UUID
    speaker: str
    text: str
    timestamp: datetime
    start_time: float
    end_time: float
    confidence: Optional[float]
    language: Optional[str]
    intent: Optional[str]
    entities: dict
    
    class Config:
        from_attributes = True


class CallEventResponse(BaseModel):
    """Call event response."""
    id: uuid.UUID
    event_type: str
    event_data: dict
    timestamp: datetime
    
    class Config:
        from_attributes = True


class CallResponse(BaseModel):
    """Call response."""
    id: uuid.UUID
    call_sid: str
    phone_number: str
    direction: str
    status: str
    started_at: datetime
    answered_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration: int
    recording_url: Optional[str]
    recording_duration: Optional[int]
    recording_status: Optional[str]
    transcription_status: Optional[str]
    language_detected: Optional[str]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    keywords: List[str]
    topics: List[str]
    outcome: Optional[str]
    outcome_details: dict
    notes: Optional[str]
    cost_amount: float
    cost_currency: str
    agent_id: uuid.UUID
    customer_id: Optional[uuid.UUID]
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
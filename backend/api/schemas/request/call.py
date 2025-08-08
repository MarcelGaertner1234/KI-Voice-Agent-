"""Call request schemas."""

from typing import Optional
from pydantic import BaseModel
import uuid


class CallCreate(BaseModel):
    """Call creation request."""
    call_sid: str
    phone_number: str
    direction: str = "inbound"
    agent_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None


class CallUpdate(BaseModel):
    """Call update request."""
    status: Optional[str] = None
    recording_url: Optional[str] = None
    recording_duration: Optional[int] = None
    recording_status: Optional[str] = None
    transcription_status: Optional[str] = None
    language_detected: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    outcome: Optional[str] = None
    outcome_details: Optional[dict] = None
    notes: Optional[str] = None
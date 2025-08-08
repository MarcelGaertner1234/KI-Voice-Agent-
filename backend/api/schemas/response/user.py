"""User response schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import uuid


class UserResponse(BaseModel):
    """User response."""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    organization_id: Optional[uuid.UUID]
    role_id: Optional[uuid.UUID]
    language: str
    timezone: str
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True